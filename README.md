# Databiqs Website Backend

Unified Flask API for the Databiqs site: **Groq chatbot** + **CMS admin** (JSON file storage, no database).

Deploy on [Railway](https://railway.app) via `railpack.json` / `start.sh` (gunicorn).

## Features

| Feature | Endpoints |
|--------|-----------|
| Chatbot | `POST /api/prompt`, `POST /api/reset` |
| Public CMS | `GET /api/content` |
| Admin CMS | `POST /api/admin/login`, `GET/PUT /api/admin/content`, `PATCH/DELETE /api/admin/content/:section` |
| Health | `GET /api/health`, `GET /health` |
....
## Local setup

```bash
pip install -r requirements.txt
copy .env.example .env   # Windows
# Set GROQ_API_KEY for chatbot; admin works without it for health/login tests
python databiqs-website.py
```

Server listens on **http://localhost:3050** (override with `PORT`).

## Environment variables

| Variable | Required | Description |
|----------|----------|-------------|
| `GROQ_API_KEY` | Yes (chat) | Groq API key for `/api/prompt` |
| `FLASK_SECRET_KEY` | Production | Session signing for chatbot |
| `ADMIN_EMAIL` | Optional | Default `admin@databiqs.com` |
| `ADMIN_PASSWORD` | Optional | Admin password |
| `ADMIN_JWT_SECRET` | Production | JWT for admin routes |
| `CONTENT_FILE` | Optional | Path to CMS JSON (default: `./content-store.json` in this repo) |

## Frontend (local)

From `../databiqs-website`:

```bash
npm run server          # starts this backend
npm start               # CRA proxies API to localhost:3050
# or: npm run dev       # both together
```

Set `REACT_APP_CONTENT_API_URL` only when not using the dev proxy (e.g. production build against Railway).

## CMS data

Site content is stored in **`content-store.json`** in this repository. Railway persists the file on the service volume; redeploy without a volume resets to the committed default unless you sync from admin saves.
