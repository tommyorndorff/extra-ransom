// Hydroponics pH / EC / temperature meter. See src/content/docs/docs/hydroponics/ph-ec-meter.md.
//
// Every CYCLE_MS: read pH with the EC board powered off (so it can't inject current into
// the water), power the EC board, read EC, power it off, read the DS18B20 for temperature
// compensation, redraw the OLED and print one CSV line on the serial port.

#include <Arduino.h>
#include <Wire.h>
#include <Preferences.h>
#include <Adafruit_ADS1X15.h>
#include <OneWire.h>
#include <DallasTemperature.h>
#include <U8g2lib.h>
#include "config.h"

// 0.96" SSD1306 128x64. For a 1.3" module use U8G2_SH1106_128X64_NONAME_F_HW_I2C instead.
U8G2_SSD1306_128X64_NONAME_F_HW_I2C oled(U8G2_R0, U8X8_PIN_NONE);
Adafruit_ADS1115 ads;
OneWire oneWire(PIN_ONEWIRE);
DallasTemperature tempSensor(&oneWire);
Preferences prefs;

struct Cal {
  float vPh7 = DEFAULT_V_PH7;  // volts with the probe in the neutral buffer
  float vPh4 = DEFAULT_V_PH4;  // volts with the probe in the acid buffer
  float buf7 = 7.00f;          // actual pH of those buffers (7.00 or 7.01; 4.01)
  float buf4 = 4.01f;
  float calTempC = 25.0f;      // water temperature when the acid point was measured
  float ecK = DEFAULT_EC_K;    // mS/cm per volt at 25 °C
  bool ph7ok = false;
  bool ph4ok = false;
  bool ecDone = false;
  bool phDone() const { return ph7ok && ph4ok; }
} cal;

float tempC = NAN;  // last good temperature; NAN until the sensor answers
bool adsOk = false;

// ---------------------------------------------------------------- measurement

float readVolts(uint8_t channel) {
  float v[SAMPLES];
  for (int i = 0; i < SAMPLES; i++) v[i] = ads.computeVolts(ads.readADC_SingleEnded(channel));
  for (int i = 1; i < SAMPLES; i++) {  // insertion sort, then take the median
    float x = v[i];
    int j = i - 1;
    while (j >= 0 && v[j] > x) { v[j + 1] = v[j]; j--; }
    v[j + 1] = x;
  }
  return v[SAMPLES / 2];
}

float readEcVolts() {
  digitalWrite(PIN_EC_POWER, EC_POWER_ON);
  delay(EC_SETTLE_MS);
  float v = readVolts(ADS_CH_EC);
  digitalWrite(PIN_EC_POWER, !EC_POWER_ON);
  return v;
}

float readPhVolts() {
  digitalWrite(PIN_EC_POWER, !EC_POWER_ON);
  delay(PH_SETTLE_MS);
  return readVolts(ADS_CH_PH);
}

float tempForMath() { return isnan(tempC) ? 25.0f : tempC; }

// The electrode's slope (V per pH unit) scales with absolute temperature.
float phFromVolts(float v) {
  float slopeAtCal = (cal.vPh4 - cal.vPh7) / (cal.buf7 - cal.buf4);
  float slope = slopeAtCal * (tempForMath() + 273.15f) / (cal.calTempC + 273.15f);
  return cal.buf7 + (cal.vPh7 - v) / slope;
}

float ecFromVolts(float v) {  // mS/cm, normalised to 25 °C
  return cal.ecK * v / (1.0f + EC_TEMP_COEF * (tempForMath() - 25.0f));
}

void updateTemp() {
  float t = tempSensor.getTempCByIndex(0);
  tempC = (t == DEVICE_DISCONNECTED_C || t < -20 || t > 80) ? NAN : t;
  tempSensor.requestTemperatures();  // non-blocking; read it next cycle
}

// ---------------------------------------------------------------- calibration

void loadCal() {
  prefs.begin("phec", true);
  cal.vPh7 = prefs.getFloat("v7", cal.vPh7);
  cal.vPh4 = prefs.getFloat("v4", cal.vPh4);
  cal.buf7 = prefs.getFloat("b7", cal.buf7);
  cal.buf4 = prefs.getFloat("b4", cal.buf4);
  cal.calTempC = prefs.getFloat("tc", cal.calTempC);
  cal.ecK = prefs.getFloat("k", cal.ecK);
  cal.ph7ok = prefs.getBool("p7ok", false);
  cal.ph4ok = prefs.getBool("p4ok", false);
  cal.ecDone = prefs.getBool("ecok", false);
  prefs.end();
}

void saveCal() {
  prefs.begin("phec", false);
  prefs.putFloat("v7", cal.vPh7);
  prefs.putFloat("v4", cal.vPh4);
  prefs.putFloat("b7", cal.buf7);
  prefs.putFloat("b4", cal.buf4);
  prefs.putFloat("tc", cal.calTempC);
  prefs.putFloat("k", cal.ecK);
  prefs.putBool("p7ok", cal.ph7ok);
  prefs.putBool("p4ok", cal.ph4ok);
  prefs.putBool("ecok", cal.ecDone);
  prefs.end();
}

bool slopeOk(float v7, float v4, float b7, float b4) {
  float slope = (v4 - v7) / (b7 - b4);
  return slope >= SLOPE_MIN_V && slope <= SLOPE_MAX_V;
}

// "cal7 [pH]" and "cal4 [pH]": the optional number is the buffer's actual pH.
// A rejected reading is reported and NOT stored.
void calPh(bool neutral, float bufferPh) {
  float v = readPhVolts();
  if (neutral) {
    float b7 = bufferPh > 0 ? bufferPh : 7.00f;
    if (v < PH7_MIN_V || v > PH7_MAX_V) {
      Serial.printf("REJECTED: %.4f V is outside %.3f-%.3f V for a neutral buffer. Probe in the buffer? Wired right?\n", v, PH7_MIN_V, PH7_MAX_V);
      return;
    }
    if (cal.ph4ok && !slopeOk(v, cal.vPh4, b7, cal.buf4)) {
      cal.ph4ok = false;  // the old acid point no longer fits; it has to be redone
      Serial.println("note: slope no longer plausible with the stored acid point; redo cal4");
    }
    cal.vPh7 = v; cal.buf7 = b7; cal.ph7ok = true;
    Serial.printf("neutral point: %.4f V at pH %.2f\n", v, b7);
  } else {
    float b4 = bufferPh > 0 ? bufferPh : 4.01f;
    if (!cal.ph7ok) { Serial.println("REJECTED: do cal7 first"); return; }
    if (!slopeOk(cal.vPh7, v, cal.buf7, b4)) {
      Serial.printf("REJECTED: %.4f V gives slope %.3f V/pH, outside %.2f-%.2f. Old calibration kept.\n", v,
                    (v - cal.vPh7) / (cal.buf7 - b4), SLOPE_MIN_V, SLOPE_MAX_V);
      return;
    }
    cal.vPh4 = v; cal.buf4 = b4; cal.calTempC = tempForMath(); cal.ph4ok = true;
    Serial.printf("acid point: %.4f V at pH %.2f, %.1f C -> pH calibrated\n", v, b4, cal.calTempC);
  }
  saveCal();
}

void handleCommand(String cmd) {
  cmd.trim();
  cmd.toLowerCase();
  if (cmd.startsWith("cal7")) {
    calPh(true, cmd.substring(4).toFloat());
  } else if (cmd.startsWith("cal4")) {
    calPh(false, cmd.substring(4).toFloat());
  } else if (cmd.startsWith("calec ")) {
    float target = cmd.substring(6).toFloat();  // mS/cm of the standard, e.g. 1.413
    float v = readEcVolts();
    float k = (target > 0 && v > 0.01f) ? target * (1.0f + EC_TEMP_COEF * (tempForMath() - 25.0f)) / v : 0;
    if (k >= EC_K_MIN && k <= EC_K_MAX) {
      cal.ecK = k;
      cal.ecDone = true;
      Serial.printf("EC: %.4f V at %.1f C -> K = %.4f mS/cm per V\n", v, tempForMath(), cal.ecK);
      saveCal();
    } else {
      Serial.printf("REJECTED: %.4f V gives K = %.3f, outside %.2f-%.2f. Probe in the standard? usage: calec 1.413\n", v, k, EC_K_MIN, EC_K_MAX);
    }
  } else if (cmd == "reset") {
    cal = Cal();
    saveCal();
    Serial.println("calibration cleared");
  } else if (cmd == "raw") {
    Serial.printf("pH %.4f V, EC %.4f V, T %.2f C\n", readPhVolts(), readEcVolts(), tempC);
  } else if (cmd.length()) {
    Serial.println("commands: cal7 [pH] | cal4 [pH] | calec <mS/cm> | raw | reset");
    Serial.println("Put the probe in the buffer, let the reading settle for a minute, then send the command.");
    Serial.println("Optional [pH] is the buffer's real value, e.g. cal7 7.01.");
  }
}

// ---------------------------------------------------------------- display

void draw(float ph, float ec, bool ecDry) {
  char buf[16];
  oled.clearBuffer();
  oled.setFont(u8g2_font_6x10_tr);
  oled.drawStr(0, 9, "pH");
  oled.drawStr(68, 9, "EC mS/cm");

  oled.setFont(u8g2_font_logisoso20_tn);
  if (ph >= 0 && ph <= 14) { snprintf(buf, sizeof buf, "%.2f", ph); } else { strcpy(buf, "--"); }
  oled.drawStr(0, 40, buf);
  if (!ecDry && ec < 99) { snprintf(buf, sizeof buf, "%.2f", ec); } else { strcpy(buf, "--"); }
  oled.drawStr(68, 40, buf);

  oled.setFont(u8g2_font_6x10_tr);
  if (isnan(tempC)) { strcpy(buf, "T --"); } else { snprintf(buf, sizeof buf, "%.1f C", tempC); }
  oled.drawStr(0, 62, buf);
  const char* status = !adsOk ? "NO ADC" : (!cal.phDone() && !cal.ecDone) ? "UNCAL" : !cal.phDone() ? "pH UNCAL" : !cal.ecDone ? "EC UNCAL" : "";
  oled.drawStr(128 - oled.getStrWidth(status), 62, status);
  oled.sendBuffer();
}

// ---------------------------------------------------------------- main

void setup() {
  Serial.begin(115200);
  pinMode(PIN_EC_POWER, OUTPUT);
  digitalWrite(PIN_EC_POWER, !EC_POWER_ON);
  Wire.begin(PIN_SDA, PIN_SCL);
  oled.begin();
  adsOk = ads.begin(0x48, &Wire);
  ads.setGain(GAIN_ONE);  // +/-4.096 V full scale; inputs must stay below the ADS1115's own supply (3.3 V)
  ads.setDataRate(RATE_ADS1115_16SPS);  // slow rate = good 50/60 Hz mains rejection
  tempSensor.begin();
  tempSensor.setWaitForConversion(false);
  tempSensor.requestTemperatures();
  loadCal();
  Serial.println("ms,ph,ec_mS_cm,temp_c");
  Serial.println("type 'help' for calibration commands");
}

void loop() {
  uint32_t start = millis();
  while (Serial.available()) {
    static String line;
    char c = Serial.read();
    if (c == '\n') { handleCommand(line); line = ""; }
    else if (c != '\r' && line.length() < 40) { line += c; }
  }

  if (!adsOk) adsOk = ads.begin(0x48, &Wire);  // keep retrying if it wasn't there at boot
  float ph = NAN, ec = NAN;
  bool ecDry = true;
  if (adsOk) {
    ph = phFromVolts(readPhVolts());
    float ecV = readEcVolts();
    ecDry = ecV < 0.02f;  // below ~20 mV the EC probe is dry or unplugged
    ec = ecFromVolts(ecV);
  }
  updateTemp();  // temperature works even if the ADC is missing
  draw(ph, ec, ecDry);
  if (adsOk) Serial.printf("%lu,%.2f,%.3f,%.1f\n", (unsigned long)start, ph, ecDry ? NAN : ec, tempC);
  int32_t wait = CYCLE_MS - (millis() - start);
  if (wait > 0) delay(wait);
}
