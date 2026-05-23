# ProTech - Professional Services Platform

A marketplace web application connecting clients with professional service workers (plumbers, electricians, cleaners, carpenters, etc.).

<img width="1586" height="744" alt="Capture5" src="https://github.com/user-attachments/assets/04e5a479-f0e5-4b9d-8fc2-391dd7d4cf3f" />

**Live Application:** Use your current Railway public URL (Settings → Networking on the web service). The old `web-production-e8d37` URL may be inactive if the project was redeployed.

---

## Deploy to Railway (live site)

1. **Push code** — Railway redeploys automatically when connected to GitHub (`main` branch).
2. **Postgres service** — Add PostgreSQL in the same Railway project.
3. **Web service variables:**

   | Variable | Value |
   |----------|--------|
   | `DATABASE_URL` | `${{ Postgres.DATABASE_URL }}` |
   | `SECRET_KEY` | long random string |
   | `FLASK_DEBUG` | `False` |

4. **Initialize the database** (once), from your PC with the Postgres **public** `DATABASE_URL`:

   ```bash
   python init_db.py "YOUR_DATABASE_URL"
   ```

5. Open the web service **public URL** → `/auth` → sign up or use demo logins below.

Health check: `https://YOUR-URL/health` should return `{"status":"ok","database":"connected"}`.

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
