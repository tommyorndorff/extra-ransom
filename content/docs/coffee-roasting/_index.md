---
title: "Coffee Roasting"
weight: 100
---

Notes on home coffee roasting — hardware setup, roast logging, and profiles.

The setup here uses [Artisan](https://artisan-scope.org/) roaster scope software running on a headless Ubuntu server with a [Phidget VINT Hub](https://www.phidgets.com/?tier=3&catid=2&pcid=1&prodid=1202) for thermocouple input, controlled remotely from a Mac on the same network.

## Equipment

- **Roaster**: FreshRoast SR800
- **Sensor hub**: Phidgets HUB0002_0 VINT hub
- **Thermocouple input**: Phidgets TMP1101_1-4x (4-channel K-type)
- **Probe**: MECCANIXITY K-type thermocouple, 1.5×100mm, 9.8 ft wire, 0–1100°C (32–2012°F), stainless steel
- **Probe fitting**: Evolution Sensors 1/8 NPT stainless steel compression fitting, for 1/16" (0.0625") diameter thermocouple probes
- **Fitting ferrule**: Evolution Sensors PTFE ferrule, for 1/16" diameter RTD/thermocouple compression fittings

## Pages

- [Artisan on Headless Linux](artisan-linux-setup) — install, configure, and run Artisan on Ubuntu with a Phidget VINT over USB; remote access from macOS
- [Logging Roasts to This Site](logging-roasts) — how to export from Artisan and add a roast profile page
