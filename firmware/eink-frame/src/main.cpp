// E-ink gift frame: wake, join Wi-Fi, fetch today's weather + poem/message, draw, deep-sleep.
// Everything happens in setup(); the chip never reaches loop().
//
//   No saved Wi-Fi, or Wi-Fi failed twice in a row -> setup hotspot "Poem-Frame-XXXX" for 5 min
//   HTTP 200 -> draw, sleep until the server's next refresh slot
//   HTTP 401 -> "not registered" screen (token missing or deleted in the admin page)
//   anything else -> keep the old picture, retry in 1 h (backing off to 6 h)
#include <Arduino.h>
#include <WiFi.h>
#include <WiFiClientSecure.h>
#include <HTTPClient.h>
#include <Preferences.h>
#include <WiFiManager.h>
#include <ArduinoJson.h>
#include "config.h"
#include "roots.h"
#include "render.h"

RTC_DATA_ATTR static uint8_t failCount = 0;       // survives deep sleep, reset on power loss
RTC_DATA_ATTR static uint8_t shownScreen = 0;     // 0 frame, 1 setup, 2 charge, 3 not registered

static Preferences prefs;
static String token;

[[noreturn]] static void sleepFor(uint32_t seconds) {
  Serial.printf("sleeping %u s\n", seconds);
  Serial.flush();
  displayOff();
  WiFi.disconnect(true);
  WiFi.mode(WIFI_OFF);
  esp_sleep_enable_timer_wakeup((uint64_t)seconds * 1000000ULL);
  esp_deep_sleep_start();
  while (true) {}
}

static uint32_t backoff() {
  uint32_t s = RETRY_SLEEP_S << min<uint8_t>(failCount > 0 ? failCount - 1 : 0, 3);
  return min<uint32_t>(s, RETRY_SLEEP_MAX_S);
}

static int readBatteryMv() {
#if PIN_BATTERY_ADC >= 0
  analogSetPinAttenuation(PIN_BATTERY_ADC, ADC_11db);
  uint32_t sum = 0;
  for (int i = 0; i < 8; i++) sum += analogReadMilliVolts(PIN_BATTERY_ADC);
  return (int)(sum / 8 * BATTERY_DIVIDER);
#else
  return -1;
#endif
}

static String apName() {
  uint8_t mac[6];
  WiFi.macAddress(mac);
  char buf[8];
  snprintf(buf, sizeof(buf), "%02X%02X", mac[4], mac[5]);
  return String(PORTAL_AP_PREFIX) + buf;
}

static void loadToken() {
  prefs.begin("frame", false);
  token = prefs.getString("token", "");
  if (!token.length() && strlen(DEVICE_TOKEN)) {
    token = DEVICE_TOKEN;
    prefs.putString("token", token);
  }
}

static bool connectSaved() {
  WiFi.mode(WIFI_STA);
  WiFi.begin();
  uint32_t t0 = millis();
  while (WiFi.status() != WL_CONNECTED && millis() - t0 < WIFI_TIMEOUT_MS) delay(100);
  return WiFi.status() == WL_CONNECTED;
}

static bool runPortal() {
  String ap = apName();
  if (shownScreen != 1) {
    String join = "1. On your phone, join the Wi-Fi network " + ap;
    const char *lines[] = {join.c_str(), "2. A setup page opens (or visit 192.168.4.1)",
                           "3. Pick your home Wi-Fi, type its password, Save"};
    renderNotice("Hello! Let's get on Wi-Fi.", lines, 3,
                 "This screen changes by itself once it's connected. If it doesn't, it tries again in an hour.");
    shownScreen = 1;
  }
  WiFiManager wm;
  wm.setDebugOutput(false);
  wm.setConfigPortalTimeout(PORTAL_TIMEOUT_S);
  wm.setTitle("Poem frame");
  WiFiManagerParameter pToken("token", "Frame code (leave as it is)", token.c_str(), 40);
  wm.addParameter(&pToken);
  bool ok = wm.startConfigPortal(ap.c_str());
  String t = pToken.getValue();
  t.trim();
  if (t.length() && t != token) {
    token = t;
    prefs.putString("token", token);
  }
  return ok && WiFi.status() == WL_CONNECTED;
}

void setup() {
  Serial.begin(115200);
  int mv = readBatteryMv();
  Serial.printf("\nframe %s, battery %d mV, wake cause %d\n", FW_VERSION, mv, (int)esp_sleep_get_wakeup_cause());

  if (mv > 2500 && mv < BATTERY_EMPTY_MV) {
    if (shownScreen != 2) {
      const char *lines[] = {"My battery is almost empty.", "Plug me into a USB-C charger for a few hours."};
      renderNotice("Time for a charge", lines, 2, nullptr);
      shownScreen = 2;
    }
    sleepFor(2 * 3600);
  }

  loadToken();
  WiFiManager probe;
  bool saved = probe.getWiFiIsSaved();
  bool online = saved && connectSaved();
  if (!online) {
    failCount = min<uint8_t>(failCount + 1, 250);
    if (!saved || failCount >= 2) online = runPortal();
    if (!online) sleepFor(backoff());
  }

  WiFiClientSecure client;
  client.setCACert(ROOT_CAS);
  HTTPClient http;
  http.setTimeout(12000);
  http.begin(client, API_URL);
  http.addHeader("X-Token", token);
  http.addHeader("X-Battery-mV", String(mv));
  http.addHeader("X-RSSI", String(WiFi.RSSI()));
  http.addHeader("X-FW", FW_VERSION);
  int code = http.GET();
  String body = code > 0 ? http.getString() : "";
  http.end();
  Serial.printf("GET %d, %u bytes\n", code, body.length());

  if (code == 401) {
    if (shownScreen != 3) {
      String id = "Frame " + apName().substring(strlen(PORTAL_AP_PREFIX));
      const char *lines[] = {"This frame isn't registered yet.", id.c_str()};
      renderNotice("Almost there", lines, 2, "Ask whoever gave it to you to finish setting it up.");
      shownScreen = 3;
    }
    sleepFor(DEFAULT_SLEEP_S);
  }

  JsonDocument doc;
  if (code != 200 || deserializeJson(doc, body) || !doc["body"].is<JsonObject>()) {
    failCount = min<uint8_t>(failCount + 1, 250);
    sleepFor(backoff());
  }

  renderFrame(doc.as<JsonObjectConst>(), mv);
  shownScreen = 0;
  failCount = 0;
  uint32_t s = doc["sleep_s"] | (uint32_t)DEFAULT_SLEEP_S;
  sleepFor(constrain(s, 600u, 16u * 3600u));
}

void loop() {}
