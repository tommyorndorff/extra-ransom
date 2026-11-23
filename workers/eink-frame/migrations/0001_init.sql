-- E-ink gift frames: one row per frame, optional messages, and the shared poem of the day.
CREATE TABLE devices (
  id           INTEGER PRIMARY KEY AUTOINCREMENT,
  name         TEXT    NOT NULL,                 -- who it's for (admin only, never shown on the frame)
  token        TEXT    NOT NULL UNIQUE,          -- compiled into / typed into the frame
  place        TEXT    NOT NULL DEFAULT '',      -- label under the date, e.g. "Asheville"
  lat          REAL    NOT NULL,
  lon          REAL    NOT NULL,
  tz           TEXT    NOT NULL,                 -- IANA zone, e.g. America/New_York
  units        TEXT    NOT NULL DEFAULT 'F' CHECK (units IN ('F', 'C')),
  refresh      TEXT    NOT NULL DEFAULT '06:00,17:00',   -- local wake times
  last_seen    TEXT,
  battery_mv   INTEGER,
  rssi         INTEGER,
  fw           TEXT,
  created_at   TEXT    NOT NULL DEFAULT (datetime('now'))
);

CREATE TABLE messages (
  id          INTEGER PRIMARY KEY AUTOINCREMENT,
  device_id   INTEGER NOT NULL REFERENCES devices(id) ON DELETE CASCADE,
  body        TEXT    NOT NULL,
  from_name   TEXT,
  show_on     TEXT,                 -- YYYY-MM-DD (frame's local date) or NULL
  pinned      INTEGER NOT NULL DEFAULT 0,   -- shown every day until unpinned/deleted
  created_at  TEXT    NOT NULL DEFAULT (datetime('now'))
);
CREATE INDEX idx_messages_device ON messages(device_id);

CREATE TABLE daily_poems (
  date   TEXT PRIMARY KEY,          -- YYYY-MM-DD
  poem   TEXT NOT NULL              -- JSON {title, author, lines}
);
