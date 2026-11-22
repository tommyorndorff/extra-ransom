# E-ink frame API

Cloudflare Worker + D1 backend for the e-ink gift frames (`firmware/eink-frame/`). Each frame calls one endpoint a couple of times a day and gets back the weather line, the day's poem or a personal message, and how long to sleep.

- Runs on `www.extra-ransom.net/api/eink/*` (same zone as the site and the c25k worker).
- **Weather**: [Open-Meteo](https://open-meteo.com/) daily forecast (no API key; free for non-commercial use), cached 15 min at the edge. After 3 pm local the header shows tomorrow's forecast.
- **Poem of the day**: one per local date, shared by every frame, from [PoetryDB](https://poetrydb.org/) (`/random,linecount/1;N` with N from 4 to 14 depending on the date). Anything too long for the screen is rejected (over 16 lines, a line over 70 characters, or over 650 characters in all), and if PoetryDB is down it uses one of four public-domain fallbacks in `src/poems.js`. Stored in `daily_poems` so it doesn't change between wakes.
- **Messages** replace the poem. A message dated for the frame's local date wins over the newest pinned message, which wins over the poem. Unscheduled, unpinned messages are never shown.
- **Refresh times** are per frame (default `06:00,17:00` local). The response's `sleep_s` lands on the next one. A wake up to 25 min early counts as that slot, which absorbs the ESP32's RTC drift.
- Text is rewritten to Latin-1 (curly quotes become straight, dashes become hyphens) because the frame's fonts can't draw anything else.
- Tokens are 20-character random strings. Anyone with a frame's token can read what that frame shows, nothing more. The admin key can do everything.

## Deploy (one time)

```bash
cd workers/eink-frame
npm install
npx wrangler login
npx wrangler d1 create eink-frame          # copy the printed database_id into wrangler.toml
npm run migrate:remote
npx wrangler secret put ADMIN_KEY          # a long random string
npm run deploy
```

Then open `https://www.extra-ransom.net/api/eink/admin`, enter the admin key, add a frame (type the town and press Find; it fills in latitude, longitude and time zone), and copy its token into the flash command (`EINK_TOKEN=… pio run -t upload`). From the same page you can preview what a frame will show, add dated or pinned messages, and see each frame's last check-in, battery voltage and Wi-Fi signal.

## Develop locally

```bash
cd workers/eink-frame
echo 'ADMIN_KEY=dev-admin-key' > .dev.vars     # git-ignored
npm run migrate:local
npm run dev                                     # http://localhost:8787/api/eink/admin
npm test                                        # unit tests for the pure helpers
```

To point a test frame at a local worker, change `API_URL` in `firmware/eink-frame/include/config.h` to your machine's LAN address over plain `http://` and use `WiFiClient` instead of `WiFiClientSecure`. That's a local hack, so don't commit it.

## API

| Method | Path | Auth | Purpose |
|---|---|---|---|
| GET | `/api/eink/frame` | `X-Token` (or `?t=`) | the frame payload; also records `X-Battery-mV`, `X-RSSI`, `X-FW` |
| GET | `/api/eink/admin` | none (page); the key is typed in | admin page |
| GET | `/api/eink/geocode?q=` | `X-Admin-Key` | town → place, lat, lon, tz (Open-Meteo geocoding) |
| GET / POST | `/api/eink/devices` | `X-Admin-Key` | list / create `{name, place?, lat, lon, tz, units?, refresh?}` |
| PATCH / DELETE | `/api/eink/devices/:id` | `X-Admin-Key` | edit any of those fields / delete (frame then shows "not registered") |
| GET | `/api/eink/devices/:id/preview` | `X-Admin-Key` | what the frame would get right now (doesn't touch telemetry) |
| GET / POST | `/api/eink/devices/:id/messages` | `X-Admin-Key` | list / add `{body, from?, show_on?: YYYY-MM-DD, pinned?}` |
| DELETE | `/api/eink/messages/:id` | `X-Admin-Key` | remove a message |

Frame payload:

```json
{
  "v": 1, "date": "Sunday, November 22", "place": "Asheville", "updated": "Sun 6:02 AM",
  "weather": { "label": "Today", "icon": "drizzle", "text": "Drizzle", "hi": 57, "lo": 49, "unit": "F", "pop": 53 },
  "body": { "kind": "poem", "title": "Song", "author": "John Clare", "lines": ["I wish I was where I would be,", "  With love alone to dwell,"] },
  "sleep_s": 39480
}
```

`body` is `{ "kind": "message", "text": "…", "from": "…" }` for messages. `weather` is `null` if Open-Meteo is unreachable, and the frame says so. `icon` is one of `clear`, `partly`, `cloudy`, `fog`, `drizzle`, `rain`, `snow`, `storm`.
