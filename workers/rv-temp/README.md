# RV temperature API

Cloudflare Worker + D1 backend for the RV sensor (LilyGo T-SIM7000G + DS18B20, powered from a 12V-outlet USB adapter; firmware lives in the `rv-sensor` repo). The sensor POSTs a small JSON reading about once an hour. The Worker stores it, and sends alerts by **push (ntfy)** with **email as backup**.

Alerts fire when something *changes*, repeat every `REMIND_H` while still true, and send a "Cleared" note on recovery:

| Alert | Condition (defaults in `wrangler.toml`) |
|---|---|
| `low_temp` | temp at or below `LOW_TEMP_F` (37 F) |
| `high_temp` | at or above `HIGH_TEMP_F` (95 F) |
| `low_rail` | external power (USB 5V, only if the sensor has the optional sense divider) at or below `LOW_RAIL_V` (4.5 V): the outlet or adapter lost power |
| `low_batt` | sensor on its own cell (no `rail_v` reported, or it reads low) at or below `LOW_BATT_V` (3.5 V) |
| `no_checkin` | no reading for `MISSED_MIN` (150 min); checked by a 15-minute cron |
| `sensor_fault` | probe reported no valid temperature (DS18B20 fault value, -196.6 F) |

## Deploy (one time)

```bash
cd workers/rv-temp
npm install
npx wrangler login
npx wrangler d1 create rv_temp          # paste the printed database_id into wrangler.toml
npm run migrate:remote
npx wrangler secret put DEVICE_KEY      # long random string; goes into the firmware
npx wrangler secret put READ_KEY        # different long random string; for your own queries
npx wrangler secret put NTFY_TOPIC      # see "Push" below
npx wrangler secret put ALERT_EMAIL     # see "Email" below
npm run deploy
```

Generate keys with `openssl rand -base64 24`. The printed URL (`https://rv-temp-api.<account>.workers.dev`) is what the firmware POSTs to. Test it: `BASE=<url> DEVICE_KEY=... READ_KEY=... ./test-curl.sh 70`, then again with `34` to see a low-temperature alert and a third time with `70` to see it clear.

## Push (ntfy), first-time setup

[ntfy](https://ntfy.sh) is a free push service with iOS and Android apps. No account is needed; the **topic name is the only secret**, so make it long and unguessable.

1. Install the **ntfy** app on your phone.
2. Pick a topic like `rv-sensor-` plus 20 random characters (`openssl rand -hex 10`).
3. In the app, tap **+** and subscribe to that topic (default server ntfy.sh). Allow notifications.
4. Put the same topic in `wrangler secret put NTFY_TOPIC`.

Priority-5 alerts (freeze, offline) are urgent in the app; you can let those bypass Do Not Disturb in the app's per-topic settings. If you'd rather not depend on a public service, ntfy can be self-hosted, or the `push()` function in `src/index.js` can be swapped for another provider.

## Email (backup), first-time setup

Uses Cloudflare Email Routing (free): in the dashboard, **extra-ransom.net -> Email -> Email Routing**, enable it, add your address under *Destination addresses*, and click the verification link. Then `wrangler secret put ALERT_EMAIL` with that address. Mail is sent from `ALERT_FROM` (default `rv-sensor@extra-ransom.net`); it only goes to verified destinations. Check spam the first time.

## Develop locally

```bash
printf 'DEVICE_KEY=dev-device\nREAD_KEY=dev-read\nALERT_EMAIL=me@example.com\n' > .dev.vars   # git-ignored
npm run migrate:local
npm run dev                      # http://localhost:8787; also trigger the cron at /cdn-cgi/handler/scheduled
```

Locally, email is written to a `.eml` file (path printed in the log) and push is skipped unless `NTFY_TOPIC` is set. Unit tests for the pure logic: `npm test`.

## API

| Method | Path | Auth | Purpose |
|---|---|---|---|
| POST | `/reading` | `X-Device-Key` | `{device?, temp_f, rail_v?, batt_v?, rssi?, lat?, lon?}`. `device` defaults to `rv`. Server time is used as the timestamp. |
| GET | `/latest` | `X-Read-Key` | newest reading per device plus active alerts |
| GET | `/readings` | `X-Read-Key` | `?device=rv&hours=48` (max 720), newest first |

Example body: `{"temp_f":70.5,"rail_v":5.0,"batt_v":4.05,"rssi":-83,"lat":35.6,"lon":-82.5}`. Readings older than `KEEP_DAYS` (180) are deleted by the cron. Free-tier Workers/D1 limits are far above one reading per hour; check Cloudflare's current pricing page.
