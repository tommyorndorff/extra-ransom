-- Daily checks for any calendar day: strength training (yes/no), sauna (yes/no), and
-- whether you rode a bike (NULL, 'indoor' or 'outdoor').
-- A row exists only while at least one of the three is set.
CREATE TABLE days (
  person_id  INTEGER NOT NULL REFERENCES people(id) ON DELETE CASCADE,
  date       TEXT    NOT NULL,                     -- YYYY-MM-DD
  strength   INTEGER NOT NULL DEFAULT 0 CHECK (strength IN (0, 1)),
  sauna      INTEGER NOT NULL DEFAULT 0 CHECK (sauna IN (0, 1)),
  bike       TEXT    CHECK (bike IN ('indoor', 'outdoor')),
  updated_at TEXT    NOT NULL DEFAULT (datetime('now')),
  PRIMARY KEY (person_id, date)
);
