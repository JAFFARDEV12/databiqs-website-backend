# Databiqs Website Backend

Unified **Flask** API for the Databiqs site:

- **Groq chatbot** — `/api/prompt`, `/api/reset`
- **CMS admin** — JSON file storage (`content-store.json`), **no database**

**Repo:** https://github.com/JAFFARDEV12/databiqs-website-backend  
**Frontend repo:** https://github.com/JAFFARDEV12/databiqs-website  

Folder layout on any laptop:

```text
company-website/
├── databiqs-website/            ← React frontend (separate clone)
└── databiqs-website-backend/    ← this repo
```

---

## Features / API map

| Feature | Endpoints |
|---------|-----------|
| Chatbot | `POST /api/prompt`, `POST /api/reset` |
| Public CMS | `GET /api/content` |
| Admin CMS | `POST /api/admin/login`, `GET/PUT /api/admin/content`, `PATCH/DELETE /api/admin/content/:section` |
| Health | `GET /api/health`, `GET /health` |

Default local URL: **http://localhost:3050**

---

## Prerequisites

- **Python 3.10+**
- **pip**
- Git
- A **Groq API key** for the chatbot — https://console.groq.com

---

## A-to-Z local setup (new laptop)

### 1. Clone

```bash
git clone https://github.com/JAFFARDEV12/databiqs-website-backend.git
cd databiqs-website-backend
```

### 2. Create virtual environment (recommended)

**Windows (PowerShell)**

```bash
python -m venv .venv
.\.venv\Scripts\Activate.ps1
```

**macOS / Linux**

```bash
python3 -m venv .venv
source .venv/bin/activate
```

### 3. Install dependencies

```bash
pip install -r requirements.txt
```

Packages: `flask`, `flask-cors`, `openai`, `python-dotenv`, `gunicorn`, `PyJWT`

### 4. Create `.env` (APIs go here)

**Windows**

```bash
copy .env.example .env
```

**macOS / Linux**

```bash
cp .env.example .env
```

Open `databiqs-website-backend/.env` and fill values.

### 5. Environment variables (where each API / secret goes)

| Variable | Required? | Where to get it / what to put | Purpose |
|----------|-----------|-------------------------------|---------|
| `GROQ_API_KEY` | **Yes** for chatbot | https://console.groq.com → API Keys | Calls Groq for `/api/prompt` |
| `GROQ_BASE_URL` | Optional | Default is fine | OpenAI-compatible Groq base URL |
| `GROQ_MODEL` | Optional | Default is fine | Model id for chat |
| `FLASK_SECRET_KEY` | **Yes** in production | Any long random string | Session cookie signing |
| `ADMIN_EMAIL` | Optional | Your admin email | Admin login |
| `ADMIN_PASSWORD` | Optional | Strong password | Admin login |
| `ADMIN_JWT_SECRET` | **Yes** in production | Long random secret | JWT for admin routes (must stay stable while admins are logged in) |
| `CONTENT_FILE` | Optional | Absolute/relative path | Override CMS JSON path |
| `PORT` | Optional | e.g. `3050` | Listen port (default 3050) |

#### Example `.env` (placeholders only)

```env
GROQ_API_KEY=gsk_your_real_key_here
GROQ_BASE_URL=https://api.groq.com/openai/v1
GROQ_MODEL=openai/gpt-oss-20b
FLASK_SECRET_KEY=change-me-in-production
ADMIN_EMAIL=admin@databiqs.com
ADMIN_PASSWORD=DatabiqsAdmin2026!
ADMIN_JWT_SECRET=databiqs-admin-dev-secret-change-in-production
# CONTENT_FILE=
```

> **Never commit `.env`.** It is listed in `.gitignore`.  
> Admin CMS health/login can work without Groq; **chatbot will fail** until `GROQ_API_KEY` is set.

### 6. Start the server

```bash
python databiqs-website.py
```

Or with gunicorn (production-style):

```bash
# Windows: use start via WSL/Git Bash, or:
gunicorn --bind 0.0.0.0:3050 --workers 2 --threads 4 --timeout 120 "databiqs-website:app"
```

`start.sh` / Railway use gunicorn and `PORT` from the host.

### 7. Verify

Open: http://localhost:3050/api/health

You should get a healthy JSON response.

---

## Run together with the frontend

1. Clone frontend next to this folder as `databiqs-website`.
2. From the **frontend** folder:

```bash
cd ../databiqs-website
npm install
npm run server:install
npm run dev
```

| Service | URL |
|---------|-----|
| Website | http://localhost:3000 |
| Admin | http://localhost:3000/admin/login |
| This API | http://localhost:3050 |

Frontend CRA proxies `/api/*` → `http://localhost:3050` in development.  
Only set `REACT_APP_CONTENT_API_URL` on the frontend when you are **not** using that proxy (production builds).

---

## CMS data (no database)

Site content is stored in:

**`content-store.json`** (in this repository)

- Railway: persist the file on a volume if you need saves to survive redeploys.
- Local: file is created/updated when you publish from the admin panel.
- Allowed sections: `services`, `caseStudies`, `blogs`, `team`, `testimonials`, `media`

---

## Production deploy

### Railway (recommended for Flask)

1. Create a new Railway project from this GitHub repo.
2. Add the same variables from `.env.example` in Railway **Variables**.
3. Start command is already defined in `railpack.json` / `start.sh` (gunicorn).
4. Copy the public URL (e.g. `https://xxxx.up.railway.app`) — no trailing slash.
5. On the **frontend** host (Vercel), set:

   ```env
   REACT_APP_CONTENT_API_URL=https://xxxx.up.railway.app
   ```

6. Change `ADMIN_PASSWORD`, `ADMIN_JWT_SECRET`, and `FLASK_SECRET_KEY` from defaults.

### Vercel

Entry is `app.py` for serverless-style deploy. Still set all env vars in the Vercel project dashboard.

CORS already allows:

- `http://localhost:3000`
- `https://www.databiqs.com` / `https://databiqs.com`
- `https://databiqs-website.vercel.app`
- Other `*.vercel.app` preview URLs

---

## Default admin credentials (local / demo)

| Field | Default |
|-------|---------|
| Email | `admin@databiqs.com` |
| Password | `DatabiqsAdmin2026!` |

Override with `ADMIN_EMAIL` and `ADMIN_PASSWORD` in `.env`.

If you see **Invalid or expired token** after changing hosts or `ADMIN_JWT_SECRET`, sign out and sign in again.

---

## Troubleshooting

| Problem | Fix |
|---------|-----|
| Chatbot 500 / model errors | Check `GROQ_API_KEY`, restart server after editing `.env` |
| Port in use | `set PORT=3051` (Windows) or `PORT=3051 python databiqs-website.py` |
| Frontend can’t call API | Run on 3050; leave frontend `REACT_APP_CONTENT_API_URL` empty in local |
| Content resets on Railway | Attach a volume or sync `content-store.json`; ephemeral disk loses writes |
| CORS errors from a new frontend domain | Add that origin in `databiqs-website.py` CORS list |

---

## Project files

| File | Role |
|------|------|
| `databiqs-website.py` | Main Flask app (chat + CMS) |
| `app.py` | Deploy entry (e.g. Vercel) |
| `content-store.json` | CMS JSON store |
| `requirements.txt` | Python dependencies |
| `.env.example` | Template for secrets |
| `start.sh` / `railpack.json` | Railway / gunicorn start |
