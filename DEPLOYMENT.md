# SupplySense — Deployment Guide

Team deployment: **https://stock-sense-orpin.vercel.app** (hosted by a teammate; may lag behind this repo)

The app is two pieces that deploy independently:

- **Frontend** (React + Vite) → **Vercel** (static hosting)
- **Backend** (FastAPI + Prophet) → **Render** (Docker web service) + **Render Postgres**

> The backend is heavy (Prophet, ChromaDB, pandas/scipy), so it is deployed on Render via
> **Docker** rather than the native Python runtime; this keeps the Prophet build reproducible.
> The free instance has 512 MB RAM and sleeps after ~15 minutes of inactivity, so the first
> request after a pause takes 30–60 seconds.

---

## 1. Backend + database on Render

The included `render.yaml` blueprint provisions both:

1. Render Dashboard → **New → Blueprint** → select this repo.
2. Render creates the backend web service (Docker, root `backend/`) and a free Postgres database.
   `SECRET_KEY` is generated and `DATABASE_URL` is wired automatically.
3. After the first deploy, set these in the backend service's **Environment** tab:
   - `CORS_ORIGINS` = your frontend URL, e.g. `https://stock-sense-orpin.vercel.app`
   - *(optional)* `CORS_ORIGIN_REGEX` = `https://.*\.vercel\.app` to allow Vercel preview deploys
   - `GEMINI_API_KEY` and/or `OPENROUTER_API_KEY` for AI features (forecasting works without them;
     OCR, explanations and translations need one)
   - *(optional)* `SERPER_API_KEY` for live disease/festival web search
4. Seed the demo data once from the service's **Shell** tab: `python seed_data.py`
5. Note the backend URL, e.g. `https://<your-backend>.onrender.com`.

**Manual alternative** (no blueprint): create a Web Service → Docker → root `backend/` →
health check path `/api/health`, then set the variables above plus a Postgres `DATABASE_URL`.

---

## 2. Frontend on Vercel

1. Vercel → **New Project** → import this repo.
2. Set **Root Directory** to `frontend`. `vercel.json` handles the Vite build and SPA routing.
3. Add an environment variable:
   - `VITE_API_BASE_URL` = `https://<your-backend>.onrender.com/api`
4. Deploy, then make sure the backend's `CORS_ORIGINS` contains the final Vercel URL
   (scheme + host, no trailing slash).

---

## 3. Local development

```bash
docker compose up --build
# Frontend  http://localhost:5173
# Backend   http://localhost:8000  (Swagger UI at /docs)
# Unified   http://localhost        (nginx)
```

Locally, leave `VITE_API_BASE_URL` and `CORS_ORIGINS` unset: the app uses the relative `/api`
path and the localhost CORS defaults.

---

## Production checklist

- [ ] `SECRET_KEY` set to a strong random value (Render generates one)
- [ ] `DEBUG=false` on the backend
- [ ] `DATABASE_URL` points at Postgres (SQLite is wiped on every Render restart)
- [ ] `CORS_ORIGINS` includes the exact frontend origin
- [ ] `VITE_API_BASE_URL` set on Vercel to the backend `/api` URL
- [ ] At least one AI key (`GEMINI_API_KEY` / `OPENROUTER_API_KEY`) if you need AI features
