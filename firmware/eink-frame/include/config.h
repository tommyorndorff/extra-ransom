#pragma once
// Everything you might change per build. Pins are ESP32 GPIO numbers, not FireBeetle silkscreen
// labels; check DFRobot's FireBeetle 2 ESP32-E pinout for which header pad each one is.

#define API_URL "https://www.extra-ransom.net/api/eink/frame"

// Display: Waveshare 7.5" V2 panel through a Good Display DESPI-C02 FPC adapter (3.3 V).
// SPI uses the ESP32 VSPI defaults: SCK = GPIO18, MOSI (DIN) = GPIO23.
#define PIN_EPD_CS   14
#define PIN_EPD_DC   13
#define PIN_EPD_RST  26
#define PIN_EPD_BUSY 25

// Battery: the FireBeetle 2 ESP32-E reads half the battery voltage through two 1 MOhm resistors.
// Most sources put it on GPIO34 (A2); confirm on your board, or set to -1 to disable.
#define PIN_BATTERY_ADC 34
#define BATTERY_DIVIDER 2.0f
#define BATTERY_LOW_MV  3500   // show "please charge" in the footer
#define BATTERY_EMPTY_MV 3300  // stop fetching; show the charge screen and check again every 2 h

#define WIFI_TIMEOUT_MS   15000
#define PORTAL_TIMEOUT_S  300   // setup hotspot stays up this long per attempt
#define PORTAL_AP_PREFIX  "Poem-Frame-"
#define RETRY_SLEEP_S     3600  // after a failed wake (Wi-Fi or server)
#define RETRY_SLEEP_MAX_S (6 * 3600)
#define DEFAULT_SLEEP_S   (6 * 3600)
