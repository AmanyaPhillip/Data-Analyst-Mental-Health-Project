# Live Feed — Progress Report

## Overview

The dashboard (`Data-Analyst-Mental-Health-Project-dashboard`) has a new **Live Feed** page (`/dashboard/live`) that pulls a value directly from Statistics Canada's public Web Data Service (WDS) API instead of the static cleaned CSVs, and feeds it into the existing trend-direction model (`06_trend_direction_model.ipynb`) to predict whether the next CCHS cycle will rise or fall.

This is additive and experimental: it does not replace or modify the curated dashboard, the cleaning notebooks, or any cleaned CSV. It is a separate page showing what a live-data version of the pipeline could look like.

---

## Why this is possible

StatCan's Web Data Service is a free, public, key-less API. Every StatCan table download (like the ones already used for `perceived_mh_annual`, `suicidal_thoughts`, etc.) carries a **vector ID** per series — a stable lookup key StatCan uses internally. Querying WDS with that vector ID returns the latest published values for that exact series, independent of when the team last downloaded and cleaned the CSV.

This was verified directly: calling WDS for vector `v1806947204` (Newfoundland and Labrador, "perceived mental health, very good or excellent") returned the same 2019/2020 and 2021/2022 values already in the cleaned CSV, plus the 2023/2024 value.

**Scope limitation:** vector IDs only survived the cleaning step for `perceived_mh_annual` (312 series — every province/territory × sex × indicator combination in that table). The other four StatCan cleaned files (`suicidal_thoughts`, `stress_coping`, `cchs_mh_disorders`, `perceived_health_quarterly`) had the vector column dropped during cleaning, so they are not live-enabled yet. Extending coverage would mean re-extracting vector IDs from the raw StatCan source files for those tables.

---

## What Was Built

### 1. `api_service` — a small FastAPI microservice

Lives in the dashboard repo (`Data-Analyst-Mental-Health-Project-dashboard/api_service/`), self-contained with its own copy of:

- `models/06_trend_direction_model.joblib` (the trained model)
- `data/perceived_mh_annual.csv` (the cleaned table that still has vector IDs)
- `requirements.txt`, `Procfile`, `.python-version`

Endpoints:

| Endpoint | Purpose |
|---|---|
| `GET /health` | Confirms the model loaded and reports how many vectors are indexed |
| `GET /vectors` | Lists all 312 known series (geo, sex, age group, indicator, last cleaned value) |
| `GET /live/{vector_id}` | Raw passthrough to StatCan WDS for a given vector |
| `POST /predict` | Direct model call, same input shape as `models/running.py` |
| `GET /live-predict/{vector_id}` | Fetches the live StatCan value for that vector, builds the model's feature row automatically (geo, geo_level, sex, age_group, indicator, year_gap from historical cycle spacing, quality flag from StatCan's status code), and returns the live value **and** the model's Up/Down prediction with probabilities |

### 2. Dashboard integration

- New page: `app/dashboard/live/page.tsx` — a province/sex/indicator picker across all 312 series, a button that fetches the live value + prediction, and a comparison against the last cleaned snapshot.
- New API routes: `app/api/live-vectors/route.ts`, `app/api/live-predict/route.ts` — these proxy server-side to the model service, so the Railway URL is never exposed to the browser.
- New component: `components/live-predictor.tsx`.
- One nav link added to `components/dashboard-nav.tsx`. No existing page, route, or component was otherwise modified.

### 3. Deployment

- **Model service:** deployed on Railway from the dashboard repo's own `api_service/` subfolder (Root Directory setting), independent of the shared analysis repo — this avoided needing another maintainer's approval to connect a new CI/deploy integration to their GitHub repo.
- **Dashboard:** existing Vercel deployment, with `LIVE_MODEL_API_URL` added as an environment variable pointing at the Railway service.

Both are now live in production — verified end-to-end on the real deployed dashboard URL, not just localhost.

---

## Bug Found and Fixed

The first production deploy showed an empty "Live model service not reachable" state on Vercel even though Railway was healthy. Root cause: the page's server-side code fetched its own internal API route (`/api/live-vectors`) using an absolute URL that defaulted to `http://localhost:3000` whenever `NEXT_PUBLIC_BASE_URL` wasn't set — and it never was in production, since that variable only existed in the local, gitignored `.env.local`. The loopback request silently failed on Vercel's serverless runtime, which has no `localhost:3000`.

**Fix:** the page now calls `LIVE_MODEL_API_URL` (the Railway service) directly, instead of looping back through its own route. Verified working on the live production URL after the fix.

---

## Deployment Steps (Railway + Vercel)

### Why Railway, and why the dashboard repo instead of the analysis repo

`api_service` was first added to the shared analysis repo (`AmanyaPhillip/Data-Analyst-Mental-Health-Project`). Railway's GitHub integration needs the repo owner (or an admin collaborator) to approve installing the Railway GitHub App on that repo — Amanya was unavailable to do that. Rather than block on it, `api_service` was made self-contained (bundling its own copy of the model + `perceived_mh_annual.csv`) and moved into the dashboard repo, which is owned outright, so Railway could connect without needing anyone else's approval. The original commits in the analysis repo were reverted to keep it clean.

### Step-by-step

1. **Create a Railway account** at railway.com and start a **New Project**.
2. **Deploy from GitHub repo** → authorize Railway's GitHub App → select the repo. Use your **own** repo (`samiromer2/Data-Analyst-Mental-Health-Project-dashboard`), not a repo you don't own/administer — Railway can't get GitHub App access to someone else's repo without their approval.
3. **False start:** the first deploy auto-detected `package.json` at the repo root and deployed the whole Next.js dashboard instead of the Python service — the generated domain served the MindMetrics site, not the API. Root cause: Railway's build root defaulted to the repo root.
4. **Fix:** in the service's **Settings → Source → Root Directory**, set it to:
   ```
   api_service
   ```
   This scopes Railway's build to that subfolder only, so it finds `api_service/Procfile`, `api_service/requirements.txt`, and `api_service/.python-version` and builds it as an isolated Python app, ignoring the Next.js code entirely.
5. **Redeploy** after changing Root Directory (Railway usually triggers this automatically on save; use the Deployments tab's "Redeploy" if not).
6. **Generate a public domain:** Settings → Networking → Public Networking → **Generate Domain**. Railway does not expose a domain by default. When it asks for a port, any number works (8080 was used) — the `Procfile` starts uvicorn on Railway's own injected `$PORT` env var (`web: uvicorn main:app --host 0.0.0.0 --port $PORT`), so whatever port is entered here is the one Railway sets `$PORT` to, and the two always match automatically.
7. **Verify** the service directly before touching the dashboard:
   ```
   curl https://<your-railway-domain>/health
   curl https://<your-railway-domain>/live-predict/1806947204
   ```
8. **Wire it into Vercel:** dashboard project → **Settings → Environment Variables** → add `LIVE_MODEL_API_URL` = the Railway domain (with `https://`, no trailing slash) → check all environments → **Redeploy** the latest deployment (env var changes don't apply retroactively to already-running deployments).
9. **Verify on the real production URL**, not just localhost — this is what caught the `localhost:3000` self-fetch bug described above, since it only failed in Vercel's actual serverless environment.

### Known leftover cleanup

The first, misconfigured Railway service (the one that served the Next.js app) is unused now that `adorable-prosperity` (Root Directory = `api_service`) is the working one. It should be deleted from the Railway project so there's only one active service and no confusion about which domain is the real API.

---

## Key Takeaways

1. Live, real-time StatCan data is technically feasible and already working in production for one dataset (`perceived_mh_annual`, 312 series).
2. The existing `06_trend_direction_model` needed no changes — it now serves live predictions over HTTP with no retraining.
3. The live feature is fully additive: it did not touch the cleaning notebooks, cleaned CSVs, curated dashboard pages, or any existing dashboard code beyond one nav link.
4. Extending live coverage to the other four StatCan tables requires re-deriving vector IDs from the raw source files, since cleaning currently drops that column for them.
5. A subtle Next.js production bug (server-side self-fetch defaulting to `localhost`) can pass every local test and still fail silently in production — worth checking for in any future "page calls its own API route" pattern.

---

## Housekeeping

An earlier Railway service was created under the wrong root directory and ended up serving the Next.js dashboard itself instead of `api_service`. That service (domain `data-analyst-mental-health-project-dashboard-production...`) is no longer used — the working service is `adorable-prosperity` — and should be deleted from the Railway project to avoid confusion or duplicate usage.
