CREATE TABLE readings (
  id      INTEGER PRIMARY KEY AUTOINCREMENT,
  device  TEXT NOT NULL,
  ts      INTEGER NOT NULL,   -- unix seconds, server receive time
  temp_f  REAL,               -- degrees F; NULL when the probe faulted
  rail_v  REAL,               -- 12V branch voltage (via divider)
  batt_v  REAL,               -- on-board 18650 voltage
  rssi    INTEGER,
  lat     REAL,
  lon     REAL
);
CREATE INDEX readings_device_ts ON readings (device, ts DESC);

-- One row per currently-active alert, so we notify on change, not every reading.
CREATE TABLE alert_state (
  device    TEXT NOT NULL,
  kind      TEXT NOT NULL,
  last_sent INTEGER NOT NULL,
  PRIMARY KEY (device, kind)
);
