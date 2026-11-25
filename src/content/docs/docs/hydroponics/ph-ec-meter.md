---
title: 'Continuous pH and EC Meter (ESP32)'
date: 2026-11-25T00:00:00.000Z
weight: 40
sidebar:
  order: 40
---

A bench meter that sits by the reservoir and shows pH, EC and water temperature all the time, instead of the pen-meter routine in [Hydroponics 101](/docs/hydroponics/hydroponics-101/) (dip, wait, read, rinse). An ESP32 reads two cheap analog probe boards through a proper ADC, corrects for temperature, and draws the numbers on a small OLED. It also prints a CSV line every 3 seconds, so a laptop on USB can log it.

> **Status (2026-11-25):** designed; the firmware compiles but nothing has been on real hardware yet. The design was cross-checked against the DFRobot product pages and library source, the ADS1115 datasheet and the ESP32 datasheet, but probe behavior in a real tank is untested. Treat the wiring and calibration numbers as a starting point and expect to adjust them.

## What it does

- **pH** from a combination glass electrode on a BNC interface board.
- **EC** (mS/cm, normalised to 25 °C) from a two-electrode conductivity probe on its own board.
- **Temperature** from a waterproof DS18B20, used to correct both readings.
- A reading every 3 s on a 128×64 OLED. If the probe is dry or the sensor is missing the screen shows `--` rather than a made-up number, and it says `UNCAL` until you've calibrated.
- Serial console at 115200 baud for calibration and logging.

## The two things that make cheap probes misbehave

1. **Don't read the ESP32's own ADC.** It is noisy and noticeably non-linear. An ADS1115 (16-bit, I2C, about $5 on a breakout) fixes that and keeps the analog wiring short.
2. **Don't run a pH probe and an EC probe in the same water at the same time.** The EC board drives current through the water, and the pH electrode picks it up, so the pH reading jumps whenever EC is powered. The cheap fix used here is time-sharing: the firmware powers the EC board from a GPIO only while it reads EC, waits for the pH reading to settle after it turns off, and reads pH with EC off. A galvanic isolator between the boards is the "proper" fix. I haven't tried either yet, so whether the time-sharing is clean enough is the first thing to check on the bench (see [Verify before trusting it](#verify-before-trusting-it)).

## Bill of materials

**Read this first: lab-grade probes are not meant to live in the tank.** DFRobot sells the cheap pH kit (SEN0161-V2) as intended for laboratory testing, with drift after extended measurement, and says of the cheap EC probe (DFR0300) that it is for intermittent sampling and that long immersion shortens its life, because the platinum-black coating on a lab-grade EC probe can be permanently damaged. A meter that is "continuous" has to either use probes rated for continuous immersion or accept replacing the cheap ones often. The table lists both.

| Part | Qty | Example | Price | Notes |
|---|---|---|---|---|
| ESP32 dev board | 1 | [Espressif ESP32-DevKitC-32E at DigiKey](https://www.digikey.com/en/products/detail/espressif-systems/ESP32-DEVKITC-32E/12091810) ([overview](https://www.espressif.com/en/products/devkits/esp32-devkitc)) | $10 | Any ESP32-WROOM-32 DevKit works; the firmware targets PlatformIO's `esp32dev`. |
| 16-bit ADC, I2C | 1 | [Adafruit ADS1115 breakout (1085)](https://www.adafruit.com/product/1085) | $14.95 | Address 0x48. Power it from 3.3 V so its inputs (limit: supply + 0.3 V) can't be over-driven. |
| pH probe + board, budget | 1 | [DFRobot Gravity Lab Grade Analog pH Sensor Kit V2 (SEN0161-V2)](https://www.dfrobot.com/product-1782.html) | $39.50 | Output 0–3.0 V on a 3.3–5.5 V supply. Lab grade: fine for dipping, drifts if left in. Comes with calibration solutions. |
| pH probe + board, continuous | 1 | [DFRobot Gravity Industrial Analog pH Sensor Kit V2 (SEN0169-V2)](https://www.dfrobot.com/product-2069.html) | $64.90 | Rated for 24/7 immersion. I haven't checked that its board has the same output range and constants as the lab-grade one, so check its page and `raw` readings before trusting the defaults. |
| EC probe + board | 1 | [DFRobot Gravity Analog EC Meter Kit, K=1 (DFR0300)](https://www.dfrobot.com/product-1123.html) | $69.90 | Output 0–3.4 V on a 3.0–5.0 V supply; recommended range 1–15 mS/cm; ±5% of full scale before calibration. DFRobot's own guide says K=1 is the one for hydroponic nutrient. Includes 1.413 and 12.88 mS/cm standards. Intermittent use only (see above). |
| EC probe, continuous | 1 | [DFRobot Gravity Industrial EC Sensor (SEN0451)](https://www.dfrobot.com/product-2565.html) | $199 | Rated for continuous immersion but a different board (PT1000 temperature on the probe) and its useful range is 100–2000 µS/cm, which covers lettuce but not much stronger feeds. **The firmware's EC constants and wiring are for the K=1 board and would need rework.** |
| Waterproof temperature probe | 1 | [DFRobot DS18B20 waterproof (DFR0198)](https://www.dfrobot.com/product-689.html) or [SparkFun SEN-11050](https://www.sparkfun.com/temperature-sensor-waterproof-ds18b20.html) | $6.90 / $10.95 | Needs a 4.7 kΩ pull-up between data and 3.3 V; the DFRobot one doesn't include it. |
| OLED, I2C, 128×64 | 1 | [Adafruit monochrome 0.96″ 128×64 OLED (326)](https://www.adafruit.com/product/326) | $17.50 | Generic SSD1306 modules from any electronics store are much cheaper. A 1.3″ SH1106 works with a one-line change in `main.cpp`. OLEDs burn in over months of a static image, so switch it off when idle. |
| High-side switch for the EC board | 1 | A P-channel MOSFET or small load switch | cents | See [Wiring](#wiring). Optional but recommended. |
| pH buffers, 4.01 and 7.01 | 1 each | [Hanna GroLine HI7004-050 (4.01)](https://hannainst.com/groline-ph-4-01-calibration-buffer-500-ml.html) and [HI7007-050 (7.01)](https://hannainst.com/groline-ph-7-01-calibration-buffer-500-ml.html) | $24.99 each | 500 mL. Note 7.01, not 7.00; the firmware lets you say which you have. The DFRobot pH kit also ships with solutions. |
| EC standard, 1.413 mS/cm | 1 | [Hanna HI7031L](https://hannainst.com/hi7031l.html) | $21.99 | 500 mL. The EC kit above includes small bottles. Buy standards, don't mix your own. |
| Breadboard or perfboard, jumpers, USB cable, small enclosure | | | | Keep everything above the water line and away from splashes. |

For comparison, the Apera pen meters in the [Garage Grow Setup](/docs/hydroponics/garage-grow-setup/) shopping list are $72–112 each. The point of this build is continuous readings, not saving money. If the probes turn out to need constant replacing, a pen meter and a weekly dip is the honest alternative.

## Wiring

Power everything from the ESP32's 3.3 V so no analog output can exceed what the ADS1115 will tolerate (its inputs must stay within a few hundred mV of its own supply).

| From | To | ESP32 GPIO / pin |
|---|---|---|
| ADS1115 SDA, OLED SDA | shared I2C data | 21 |
| ADS1115 SCL, OLED SCL | shared I2C clock | 22 |
| ADS1115 A0 | pH board analog out | |
| ADS1115 A1 | EC board analog out | |
| EC board VCC | switched 3.3 V (see below) | 25 |
| DS18B20 data | | 4 |
| All grounds | common | GND |
| pH board VCC, ADS1115, OLED, DS18B20 | | 3V3 |

Notes:

- **Switch the EC board's supply with a high-side P-MOSFET (or load switch) rather than straight from the GPIO.** DFRobot doesn't state the board's supply current, and the ESP32's datasheet only guarantees a pin's high level down to 2.64 V under load, below the EC board's 3.0 V minimum. If the board is switched by a P-MOSFET whose gate is on GPIO25, the logic is inverted: set `EC_POWER_ON` to `LOW` in `config.h`. Driving the board directly from the pin (`HIGH`) is fine for a first bench test with a short wire, but check the supply voltage at the board while it's on.
- Run the ground wire of the pH and EC boards back to one point.
- Use the ADS1115's single-ended mode on A0 and A1 (the firmware does).
- Switching only the supply leaves the EC probe still tied to ground through the unpowered board. Whether that disturbs the pH reading is untested; see the bench checks below. DFRobot sells a signal isolator ([DFR0504](https://www.dfrobot.com/product-1621.html), $19.90) for exactly this problem, but it needs a 5 V supply on the microcontroller side and adds about ±20 mV of error, roughly 0.12 mS/cm of EC, so you'd calibrate EC through it.
- Pins are in [`include/config.h`](https://github.com/tommyorndorff/extra-ransom/blob/main/firmware/ph-ec-meter/include/config.h) if you need to move them.

## Firmware

Code: [`firmware/ph-ec-meter/`](https://github.com/tommyorndorff/extra-ransom/tree/main/firmware/ph-ec-meter) (PlatformIO, Arduino framework). `pio run -t upload` builds and flashes; `pio device monitor` opens the console.

Each 3-second cycle:

1. Make sure the EC board is off, wait 300 ms, take 9 ADC reads from A0 and keep the median (the median throws out spikes from pump or heater switching). The ADC runs at a slow 16 samples per second, which rejects 50/60 Hz mains pickup. The EC board has been off since the previous cycle, so the pH probe has had about a second to settle.
2. Turn the EC board on, wait 500 ms, take the median of 9 reads from A1, turn it off.
3. Read the DS18B20 (the conversion started on the previous cycle, so it never blocks). This works even if the ADC is missing; the firmware keeps retrying the ADC.
4. Convert and draw. Print `ms,ph,ec_mS_cm,temp_c`.

The maths:

- **pH** is linear in probe voltage between the two calibration points. The slope scales with absolute temperature (the Nernst relationship), so a reading at 18 °C is corrected using the slope measured at the calibration temperature.
- **EC** is `K × volts`, divided by `1 + 0.0185 × (T − 25)` to report the value at 25 °C. That coefficient is the one DFRobot's own EC library uses; it's a rule of thumb for solutions, not measured for any particular nutrient mix.
- If the temperature sensor is missing, both fall back to 25 °C and the screen shows `T --`.

## Calibrating

Type commands into the serial monitor. Rinse the probes in clean water between solutions, put them in the standard, wait a minute for the reading to settle, then send the command. Results are stored in flash. Every command checks the result against a plausible window (DFRobot's own acceptance ranges) and **rejects and discards** a bad reading instead of storing it, so a slip can't leave you with a broken calibration.

| Command | What it does |
|---|---|
| `cal7` or `cal7 7.01` | Probe in the neutral buffer. The optional number is the buffer's real pH (default 7.00). Must read between 1.32 and 1.68 V. |
| `cal4` or `cal4 4.01` | Probe in the acid buffer (default 4.01). Needs `cal7` first. The resulting slope has to land between 0.14 and 0.19 V per pH unit (the ideal is 0.059 V × the 3 pH units, about 0.177 at 25 °C on this board). The water temperature is recorded for the temperature correction. |
| `calec 1.413` | EC probe in the 1.413 mS/cm standard: sets the EC constant, if it lands between 0.5× and 1.5× the default. |
| `raw` | Prints the raw probe voltages, useful when something looks off. |
| `reset` | Clears the stored calibration. |

Do `cal7` first, then `cal4`. Calibrate pH before each new batch of nutrient, then monthly once readings look stable. A two-point pH calibration with 4 and 7 buffers fits the 5.5–6.5 range this system runs in, so there's no need for a pH 10 buffer. Buffers drift a few hundredths of a pH with temperature (a 7.01 buffer reads about 7.03 at 15–20 °C), which is below this meter's accuracy.

## Verify before trusting it

Things I'd check on the bench, in this order:

1. **Probes in the same bucket,** in three runs: (a) EC probe out of the water; (b) EC probe in the water but its board unpowered; (c) the normal cycle. Each run, does the pH value stay put (within about 0.05) over a few minutes and match a pen meter or pH 7 buffer? A difference between (a) and (b) means the ground path through the unpowered EC board is the problem (switch the EC ground and probe leads too, or use the isolator); a difference between (b) and (c) means the excitation is, so lengthen `PH_SETTLE_MS`.
2. **EC against a second standard,** e.g. 2.76 mS/cm after calibrating on 1.413. DFRobot's own library uses two constants, switching at about 2.0–2.5 mS/cm, which suggests the response isn't perfectly linear across the range. A single-point calibration assumes the probe is linear through zero; if the second standard is off by more than a few percent, EC at nutrient strength isn't trustworthy and a better probe (or the two-constant approach) is the fix. Also note the board's own spec of ±5% of full scale: the output at 1.413 mS/cm is only about 0.23 V, so noise matters.
3. **Temperature:** the DS18B20 against a thermometer you trust.
4. **Drift after a week in the tank.** The budget probes are lab grade and not meant to stay submerged (see the BOM), so expect drift and shortened probe life; the continuous-rated pH probe should do better. If the reading wanders, take the probe out for a pen-meter cross-check, and recalibrate.
5. **Waterproofing and grounding** of the enclosure; the garage is damp and the tower's pump and heater share the reservoir.

## Ideas for later

- **Wi-Fi logging:** post readings to a Cloudflare Worker and D1 table like the other sensor builds on this site, with pH/EC trend charts and an alert when pH leaves 5.5–6.5.
- **Isolated pH board** if time-sharing proves too noisy.
- A small **dosing pump** for pH-down. Not recommended until the readings have proven themselves; a stuck-on acid pump will kill a tank.

## Safety

- The probes sit in the same reservoir as the heater and pump. Keep the meter on low-voltage USB power, away from the AC side, and keep the enclosure out of splash range.
- pH Down is acid: gloves and eye protection when adjusting (see [Garage Grow Setup](/docs/hydroponics/garage-grow-setup/)).
- Don't rely on this for anything safety-related. It reports; it doesn't control anything.
