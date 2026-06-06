# ProTech - Professional Services Platform

A marketplace web application connecting clients with professional service workers (plumbers, electricians, cleaners, carpenters, etc.).

<img width="1586" height="744" alt="Capture5" src="https://github.com/user-attachments/assets/04e5a479-f0e5-4b9d-8fc2-391dd7d4cf3f" />

**Live Application:** This is a Flask app — it does **not** run on `github.com/...` alone. Use your **Railway** or **Render** public URL (see below). The old `web-production-e8d37` URL is inactive if that service was removed.

---

## GitHub → live site (choose one)

| Method | What you get |
|--------|----------------|
| **Railway + GitHub** (recommended) | Auto-deploy on every push to `main` |
| **Render Blueprint** | One-click deploy from `render.yaml` |
| **GitHub Actions → Railway** | Same as Railway, triggered by workflow after you add secrets |

After deploy:

1. Set your public URL in **`live-config.js`** (`window.PROTECH_LIVE_URL = 'https://your-app.up.railway.app'`) so [GitHub Pages](https://logandescapo-eng.github.io/protech1/) login links redirect to the live app.
2. Paste the same URL in the repo **About** section (Settings → General → Website).

> GitHub Pages only hosts static files. The full Flask app (auth, bookings, escrow) runs on Railway or Render. Pages acts as the public entry point once `live-config.js` is set.

### GitHub Actions (CI + optional Railway deploy)

On every push to `main`, **CI** runs (`.github/workflows/ci.yml`) — imports the app and checks `/health`.

To enable **automatic Railway deploy** from GitHub:

1. Railway → your **web** service → **Settings** → copy **Service ID**.
2. Railway → **Account Settings** → **Tokens** → create a token.
3. GitHub repo → **Settings** → **Secrets and variables** → **Actions** → add:
   - `RAILWAY_TOKEN` — token from step 2
   - `RAILWAY_SERVICE_ID` — service ID from step 1
4. Push to `main` or run **Actions** → **Deploy to Railway** → **Run workflow**.

Without those secrets, CI still passes; deploy is skipped with a notice in the workflow log.

### Deploy to Render (alternative)

1. Go to [dashboard.render.com](https://dashboard.render.com) → **New** → **Blueprint**.
2. Connect repo `logandescapo-eng/protech1` — Render reads `render.yaml`.
3. After deploy, open **protech-web** → copy the `.onrender.com` URL.
4. Run `init_db.py` and `migrate_escrow.py` with the Render Postgres **External** connection string.

---

## Deploy to Railway (live site)

> **Old links like `web-production-e8d37.up.railway.app` will not work** if that project/service was removed. You must use the URL from **your** Railway project (step 4).

### A. Create or reconnect the project

1. Go to [railway.app](https://railway.app) → **New Project**.
2. **Deploy from GitHub repo** → select `logandescapo-eng/protech1` → branch `main`.
3. Railway creates a **web** service from the `Dockerfile`.

### B. Add PostgreSQL

1. In the same project: **+ New** → **Database** → **PostgreSQL**.

### C. Configure the web service

**Variables** (click the **web** service, not Postgres):

| Variable | Value |
|----------|--------|
| `DATABASE_URL` | `${{ Postgres.DATABASE_URL }}` |
| `SECRET_KEY` | long random string |
| `FLASK_DEBUG` | `False` |

**Settings → Networking → Public Networking** → **Generate Domain**.

Copy that URL — this is your live link (example: `https://protech1-production-xxxx.up.railway.app`).

### D. Verify deploy

1. **Deployments** tab should show **Success** (green).
2. Open `https://YOUR-DOMAIN/health` — should include `"status":"ok"`.
3. Open `https://YOUR-DOMAIN/` — landing page loads.

If deploy fails, open **View logs** on the failed deployment.

### E. Initialize database (once, on your PC)

Postgres → **Connect** → copy **public** `DATABASE_URL`:

```bash
python init_db.py "YOUR_DATABASE_URL"
python migrate_escrow.py "YOUR_DATABASE_URL"
```

Then test `https://YOUR-DOMAIN/auth` with demo logins below.

### F. CLI deploy (optional)

```bash
npm i -g @railway/cli
railway login
railway link
railway up
railway domain
```

**Escrow on existing DB:** `python migrate_escrow.py "YOUR_DATABASE_URL"`

---

## Escrow payments

ProTech holds job payments in a **platform escrow vault** until the worker marks the job complete.

1. **Wallet** (`/wallet`) — add demo funds (simulated bank deposit).
2. **Book a pro** — after booking, **Pay into escrow** moves money from wallet → vault.
3. **Job complete** — funds release to the worker's wallet (minus 5% platform fee by default).
4. **Cancelled** — full refund from escrow back to the client's wallet.

This build uses an internal ledger (not real banks). For production, connect **Stripe** or another licensed processor and map webhooks to `escrow_service.py`.

---

## 🎯 What ProTech Does

ProTech is a marketplace platform that connects clients with skilled professional service workers. 

**For Clients:**
- Browse and search for professionals by skill, location, and rating
- Book services with specific date, time, and description
- Track booking status and leave reviews

**For Professionals:**
- Create a profile with skills and experience
- Receive and manage job requests
- Build reputation through client reviews

---

## 🛠️ Technology Stack

- **Backend:** Python Flask
- **Database:** PostgreSQL
- **Frontend:** HTML, CSS, JavaScript
- **Templating:** Jinja2
- **Containerization:** Docker
- **Hosting:** Railway

---

## Demo login (after database setup)

| Email | Password | Role |
|-------|----------|------|
| john@example.com | password123 | Client |
| mike@example.com | password123 | Worker |

If login fails, the DB may still have the old wrong hash. From the project folder, with your Railway `DATABASE_URL`:

```bash
python fix_passwords.py "YOUR_DATABASE_URL"
```

Or re-run full setup:

```bash
python init_db.py "YOUR_DATABASE_URL"
```

**Note:** Older seed data used hash for `password` (not `password123`). Try `password` only if you have not run `fix_passwords.py` or `init_db.py` since this fix.
