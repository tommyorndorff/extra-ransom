-- People and their logged sessions for the Couch to Turkey Trot page.
CREATE TABLE people (
  id          INTEGER PRIMARY KEY AUTOINCREMENT,
  name        TEXT    NOT NULL,
  level       TEXT    NOT NULL DEFAULT 'beginner' CHECK (level IN ('beginner', 'intermediate', 'runner')),
  edit_token  TEXT    NOT NULL UNIQUE,   -- full access: log sessions, change level
  view_token  TEXT    NOT NULL UNIQUE,   -- read-only link for sharing the summary
  created_at  TEXT    NOT NULL DEFAULT (datetime('now'))
);

CREATE TABLE entries (
  id           INTEGER PRIMARY KEY AUTOINCREMENT,
  person_id    INTEGER NOT NULL REFERENCES people(id) ON DELETE CASCADE,
  plan_id      TEXT    NOT NULL,          -- s01..s11 or race
  date         TEXT    NOT NULL,          -- YYYY-MM-DD, the day it was actually done
  distance_mi  REAL,                      -- optional
  duration_min REAL,                      -- optional
  run_pct      INTEGER,                   -- optional, 0-100: share of the time spent running
  note         TEXT,
  updated_at   TEXT    NOT NULL DEFAULT (datetime('now')),
  UNIQUE (person_id, plan_id)
);
CREATE INDEX idx_entries_person ON entries(person_id);
