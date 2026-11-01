# Couch to Turkey Trot API

Cloudflare Worker + D1 (SQLite) backend for `/couch-to-5k/`. It stores each person's logged sessions (date, distance, time, rough running share, notes) so the page can sync across devices and show a per-person progress summary.

- Runs on `www.extra-ransom.net/api/c25k/*` (same origin as the page, so no CORS setup in production).
- **Edit link** (`?p=<edit_token>`): log, change, and remove sessions; change plan level.
- **View link** (`summary/?p=<view_token>`): read-only.
- **Everyone** (`/couch-to-5k/team/`, public): one colored dot per person with which sessions are logged and totals. No names, notes or links; each person picks their own dot color on the main page.
- **Admin** (`/couch-to-5k/admin/`): create and delete people and copy their links. Needs the `ADMIN_KEY` secret.
- Tokens are random 32-character strings stored in D1. Anyone holding a link has that access, so treat edit links like passwords. Store first names or nicknames only.

## Deploy (one time)

You need a Cloudflare account that owns the `extra-ransom.net` zone (its nameservers are Cloudflare's, and the `www` record is proxied).

```bash
cd workers/couch-to-5k
npm install
npx wrangler login
npx wrangler d1 create c25k            # copy the printed database_id into wrangler.toml
npm run migrate:remote                  # creates the tables (and applies any later migrations)
npx wrangler secret put ADMIN_KEY       # choose a long random string
npm run deploy
```

Then open `https://www.extra-ransom.net/couch-to-5k/admin/`, enter the admin key, add people, and send each their edit link. Redeploy after code changes with `npm run deploy`; schema changes go in a new numbered file under `migrations/`, applied with `npm run migrate:remote`.

Free-tier limits (Workers and D1) are far above what a family tracker needs; check Cloudflare's current pricing page.

## Develop locally

```bash
cd workers/couch-to-5k
echo 'ADMIN_KEY=dev-admin-key' > .dev.vars     # git-ignored
npm run migrate:local
npm run dev                                     # http://localhost:8787
```

Serve the site (`make serve`, or any static server over `public/`) and open the page with the API override, which only works from localhost:
`http://localhost:1313/couch-to-5k/admin/?api=http://localhost:8787/api/c25k`

Unit tests for the validation helpers: `npm test`.

## API

| Method | Path | Auth | Purpose |
|---|---|---|---|
| GET | `/api/c25k/people` | `X-Admin-Key` | list people with links' tokens |
| POST | `/api/c25k/people` | `X-Admin-Key` | create `{name, level}` |
| DELETE | `/api/c25k/people/:id` | `X-Admin-Key` | delete a person and their entries |
| GET | `/api/c25k/team` | none (public) | anonymous dots: color, level, logged sessions, totals |
| GET | `/api/c25k/me` | `X-Token` | person + all entries |
| PATCH | `/api/c25k/me` | edit token | `{level?, color?}`: level is beginner, intermediate or runner; color is `#rrggbb` |
| PUT | `/api/c25k/entries/:planId` | edit token | upsert `{date, distance_mi, duration_min, run_pct, note}` |
| DELETE | `/api/c25k/entries/:planId` | edit token | remove a logged session |

`planId` is `s01`..`s11` or `race`. Distance, time, run percentage and note are optional.
