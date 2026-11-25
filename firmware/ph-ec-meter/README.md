# pH / EC meter firmware

PlatformIO / Arduino firmware for a continuous hydroponics pH, EC and temperature meter: ESP32 DevKit + ADS1115 ADC + SSD1306 OLED. Parts, wiring, calibration and caveats are on the site page (`src/content/docs/docs/hydroponics/ph-ec-meter.md`).

```bash
pio run -t upload     # build and flash
pio device monitor    # 115200 baud; CSV lines, plus calibration commands
```

Pins and tuning are in `include/config.h`. Calibration (`cal7 [pH]`, `cal4 [pH]`, `calec <mS/cm>`, `raw`, `reset`) is typed into the serial monitor and stored in flash.

Status: compiles; not yet run on hardware.
