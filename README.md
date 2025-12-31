# ProTech - Professional Services Platform

A marketplace web application connecting clients with professional service workers (plumbers, electricians, cleaners, carpenters, etc.).

<img width="1586" height="744" alt="Capture5" src="https://github.com/user-attachments/assets/04e5a479-f0e5-4b9d-8fc2-391dd7d4cf3f" />



## 📋 Quick Start

### Prerequisites
- Python 3.8+ 
- PostgreSQL 13+
- pip (Python package manager)

### Installation

1. **Install Python dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

2. **Configure database in `config.py`:**
   ```python
   DB_PASS = 'your_postgresql_password'  # Update with your PostgreSQL password
   ```

3. **Run the application:**
   ```bash
   python app.py
   ```

4. **Access the application:**
   Open your browser to: **http://127.0.0.1:5000**

---

## 🐳 Docker Deployment (For Sharing with Others)

To host the application so others can access it, use Docker:

**⚠️ Important:** Docker containers **must be running** for the link to work. If Docker is stopped, the link will not be accessible.

1. **Install Docker Desktop** (if not already installed)

2. **Build and start containers:**
   ```bash
   docker-compose up --build
   ```

3. **Access locally:**
   - **http://127.0.0.1:5000** (from your computer)

4. **Share with others on your network:**
   - Find your IP address: `ipconfig` (Windows) or `ifconfig` (Mac/Linux)
   - Share: `http://YOUR_IP_ADDRESS:5000`
   - Example: `http://192.168.43.186:5000`

See **[DOCKER_SETUP.md](DOCKER_SETUP.md)** for detailed Docker instructions.

**Note:** The application is only accessible when Docker containers are running. Stop Docker = link stops working.

## 🔑 Test Login Credentials

All test accounts use password: `password123`

| Email | Password | Type |
|-------|----------|------|
| john@example.com | password123 | Client |
| mike@example.com | password123 | Worker (Plumber) |
| sarah@example.com | password123 | Worker (Electrician) |
| david@example.com | password123 | Worker (Cleaner) |

## ✨ Features

### For Clients
- 🔍 Browse and search for professionals by skill, location, and rating
- 📅 Book services with specific date, time, and description
- 📊 Track booking status (pending → confirmed → in progress → completed)
- ⭐ Leave reviews and ratings
- 📈 View booking history and spending statistics

### For Professionals
- 📥 Receive and manage job requests
- ✅ Accept or decline bookings
- 📆 View daily schedule and upcoming jobs
- 💰 Track earnings and completed jobs
- ⭐ Build reputation through reviews

## 🗂️ Project Structure

```
protech/
├── app.py              # Main Flask application
├── config.py           # Database configuration
├── auth.py             # Authentication functions
├── db_functions.py     # Database operations
├── db_connection.py    # Database connection helper
├── requirements.txt    # Python dependencies
├── database.sql        # PostgreSQL schema
└── templates/          # HTML templates (Jinja2)
    ├── base.html
    ├── auth.html
    ├── index.html
    ├── user_dashboard.html
    └── worker_dashboard.html
```

## 🗄️ Database

### Important: Database Safety
- The database (`protech_db`) remains unchanged
- All existing data is preserved
- Only the application code changed from PHP to Python

### Database Schema

| Table | Description |
|-------|-------------|
| `users` | All accounts (clients + workers) |
| `workers` | Professional details (skills, rate, rating) |
| `service_categories` | Service types (Plumbing, Electrical, etc.) |
| `bookings` | Service appointments |
| `reviews` | Ratings and comments |
| `notifications` | User alerts |
| `favorites` | Saved workers |
| `messages` | Chat messages |

## 🔧 Configuration

Edit `config.py` to update database settings:

```python
DB_HOST = '127.0.0.1'
DB_PORT = '5432'
DB_NAME = 'protech_db'
DB_USER = 'postgres'
DB_PASS = 'your_password'  # ← Update this
```

## 📱 User Flows

### Client Journey
1. **Register** → Creates user account
2. **Browse** → Search workers by skill/location
3. **Book** → Select date, time, describe the job
4. **Wait** → Worker reviews and accepts
5. **Service** → Worker completes the job
6. **Review** → Rate and review the worker

### Worker Journey
1. **Register** → Creates worker profile with skills/experience
2. **Receive** → Gets notified of new job requests
3. **Review** → Accept or decline bookings
4. **Complete** → Mark jobs as completed
5. **Build** → Earn ratings and reviews

## 🛠️ Technology Stack

- **Backend:** Python Flask
- **Database:** PostgreSQL
- **Frontend:** HTML, CSS, JavaScript
- **Templating:** Jinja2

## 📝 Notes

- Ensure PostgreSQL is running before starting the application
- Database connection errors will be displayed in the terminal
- All passwords are hashed using bcrypt
