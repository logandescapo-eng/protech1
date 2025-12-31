# Setting Up Database on Railway

## Step 1: Connect Database to Flask App

1. Go to your **Flask app service** in Railway
2. Click **"Variables"** tab
3. Click **"+ New Variable"**
4. Name: `DATABASE_URL`
5. Value: `${{ Postgres.DATABASE_URL }}` (copy exactly from Railway's Connect modal)
6. Click **"Add"**

## Step 2: Run Database SQL

Railway's Connect modal doesn't have a query editor. Use one of these methods:

### Option A: Railway CLI (Recommended)

1. Install Railway CLI: `npm i -g @railway/cli`
2. Login: `railway login`
3. Link to your project: `railway link`
4. Run the init script:
   ```bash
   railway run python init_railway_db.py
   ```

### Option B: Temporary Python Script

1. In Railway, go to your Flask app service
2. Go to **"Settings"** → **"Deploy"**
3. Temporarily change **"Start Command"** to: `python init_railway_db.py`
4. Save and redeploy (this will run the script)
5. After it completes, change Start Command back to: `python app.py`
6. Redeploy again

### Option C: Use pgAdmin or DBeaver

1. Use the connection details from Railway's Connect modal
2. Connect with pgAdmin/DBeaver GUI tool
3. Open Query Tool
4. Copy/paste contents of `database.sql`
5. Execute
