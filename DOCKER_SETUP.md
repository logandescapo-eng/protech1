# Docker Setup Guide for ProTech

This guide will help you host your ProTech application using Docker so others can access it.

## 📋 Prerequisites

1. **Docker Desktop** installed on your computer
   - Download from: https://www.docker.com/products/docker-desktop
   - Install and make sure it's running

2. **Docker Compose** (usually included with Docker Desktop)

## 🚀 Quick Start

### Step 1: Update Docker Configuration

The `docker-compose.yml` file is already configured. You may want to:
- Change the PostgreSQL password (currently `postgres123`)
- Change the Flask secret key for production

### Step 2: Build and Start Containers

Open your terminal in the project folder and run:

```bash
docker-compose up --build
```

This will:
- Build the Flask application image
- Start PostgreSQL database
- Start the Flask web server
- Initialize the database with schema

**First time will take a few minutes** to download images and build.

### Step 3: Access Your Application

Once containers are running, you'll see:
```
web_1  |  * Running on http://0.0.0.0:5000
```

Your app is now available at:
- **Local:** http://localhost:5000
- **Network:** http://YOUR_IP_ADDRESS:5000

### Step 4: Find Your IP Address

To let others access it, find your computer's IP:

**Windows:**
```powershell
ipconfig
```
Look for "IPv4 Address" (usually something like 192.168.1.xxx)

**Mac/Linux:**
```bash
ifconfig
# or
ip addr
```

### Step 5: Share the Link

Share this link with others:
```
http://YOUR_IP_ADDRESS:5000
```

**Example:** `http://192.168.1.100:5000`

## 🔧 Common Commands

### Start containers (in background):
```bash
docker-compose up -d
```

### Stop containers:
```bash
docker-compose down
```

### View logs:
```bash
docker-compose logs -f
```

### Restart containers:
```bash
docker-compose restart
```

### Rebuild after code changes:
```bash
docker-compose up --build
```

## 🌐 Making it Accessible to Others

### Option 1: Local Network (Same WiFi)
- Make sure your firewall allows port 5000
- Share: `http://YOUR_IP:5000`
- Others on the same network can access it

### Option 2: Internet Access (Advanced)
For internet access, you'll need:
1. **Port forwarding** on your router (port 5000)
2. **Dynamic DNS** service (like No-IP, DuckDNS)
3. Or use a **cloud service** (AWS, DigitalOcean, etc.)

### Option 3: Cloud Hosting (Recommended for Production)
Deploy to:
- **Heroku** (free tier available)
- **Railway** (easy deployment)
- **DigitalOcean App Platform**
- **AWS Elastic Beanstalk**

## 🔒 Security Notes

1. **Change default passwords** in `docker-compose.yml`
2. **Update SECRET_KEY** in environment variables
3. **Use HTTPS** in production (requires reverse proxy like nginx)
4. **Don't expose database port** (5432) publicly

## 📝 Environment Variables

You can customize settings in `docker-compose.yml`:

```yaml
environment:
  - DB_PASS=your_secure_password
  - SECRET_KEY=your-random-secret-key
  - FLASK_DEBUG=False  # Set to False in production
```

## 🐛 Troubleshooting

### Port already in use:
Change port in `docker-compose.yml`:
```yaml
ports:
  - "8080:5000"  # Use port 8080 instead
```

### Database connection errors:
- Wait for database to be healthy (check logs)
- Verify passwords match in docker-compose.yml

### Can't access from other devices:
- Check Windows Firewall settings
- Make sure Docker Desktop is running
- Verify IP address is correct

## 📦 What Gets Created

- **protech_web** - Flask application container
- **protech_db** - PostgreSQL database container
- **postgres_data** - Persistent database storage volume

## 🎯 Next Steps

1. Test locally: http://localhost:5000
2. Test from another device on same network
3. For production, consider:
   - Adding nginx reverse proxy
   - Setting up SSL/HTTPS
   - Using a cloud hosting service
