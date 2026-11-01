-- Each person picks a color shown as their dot on the public team page.
-- NULL means "use the default palette color for this person" (see colorOf in src/index.js).
ALTER TABLE people ADD COLUMN color TEXT;
