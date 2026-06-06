# ProTech - Professional Services Platform

A marketplace web application connecting clients with professional service workers (plumbers, electricians, cleaners, carpenters, etc.).

<img width="1586" height="744" alt="Capture5" src="https://github.com/user-attachments/assets/04e5a479-f0e5-4b9d-8fc2-391dd7d4cf3f" />

**Live Application:** Use your current Railway public URL (Settings → Networking on the web service). The old `web-production-e8d37` URL may be inactive if the project was redeployed.

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
