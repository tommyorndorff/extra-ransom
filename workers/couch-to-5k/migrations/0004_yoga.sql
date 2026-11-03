-- Yoga (yes/no) joins strength, sauna and bike as a daily check.
ALTER TABLE days ADD COLUMN yoga INTEGER NOT NULL DEFAULT 0 CHECK (yoga IN (0, 1));
