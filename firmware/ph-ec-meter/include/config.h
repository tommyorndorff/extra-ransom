#pragma once
// Pins and tuning for the pH / EC meter. Change here, not in main.cpp.

// I2C bus shared by the ADS1115 (0x48) and the OLED (0x3C).
constexpr int PIN_SDA = 21;
constexpr int PIN_SCL = 22;

constexpr int PIN_ONEWIRE = 4;   // DS18B20 data (4.7 k pull-up to 3V3)
constexpr int PIN_EC_POWER = 25; // powers the EC board only while it is being read

constexpr uint8_t ADS_CH_PH = 0; // ADS1115 input for the pH board's analog out
constexpr uint8_t ADS_CH_EC = 1; // ADS1115 input for the EC board's analog out

// Level that turns the EC board's supply ON. HIGH when GPIO25 feeds the board directly;
// use LOW if a high-side P-MOSFET (gate on GPIO25) switches it, which is the better build.
constexpr int EC_POWER_ON = HIGH;

constexpr uint32_t CYCLE_MS = 3000;     // one pH + EC + temperature pass
constexpr uint32_t PH_SETTLE_MS = 300;  // wait after EC power-down before reading pH
constexpr uint32_t EC_SETTLE_MS = 500;  // wait after EC power-up before reading EC
constexpr int SAMPLES = 9;              // ADC reads per value (16 SPS each, rejects 50/60 Hz); the median is used

// Placeholder calibration, used until you calibrate (display shows "UNCAL").
// pH: DFRobot Gravity pH v2 sample values (mV at pH 7 and pH 4).
constexpr float DEFAULT_V_PH7 = 1.500f;
constexpr float DEFAULT_V_PH4 = 2.032f;
// EC: mS/cm per volt. 1000/(820*200) * 1000 from the DFRobot Gravity EC sample.
constexpr float DEFAULT_EC_K = 6.098f;
constexpr float EC_TEMP_COEF = 0.0185f; // per °C; the value DFRobot's EC library uses

// Calibration sanity windows (DFRobot's own acceptance ranges, in volts).
constexpr float PH7_MIN_V = 1.322f, PH7_MAX_V = 1.678f;
constexpr float SLOPE_MIN_V = 0.14f, SLOPE_MAX_V = 0.19f;  // volts per pH unit at ~25 °C (Nernst: 0.059)
constexpr float EC_K_MIN = 3.05f, EC_K_MAX = 9.15f;        // 0.5x to 1.5x of DEFAULT_EC_K
