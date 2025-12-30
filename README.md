# ProTech - Professional Services Platform

A marketplace web application connecting clients with professional service workers (plumbers, electricians, cleaners, carpenters, etc.).

## 📋 Quick Start

See **[SETUP_GUIDE.md](SETUP_GUIDE.md)** for detailed installation instructions.

### Prerequisites
- PHP 8.0+ with `pdo_pgsql` extension
- PostgreSQL 13+

### Quick Setup (after installing PHP and PostgreSQL)

```bash
# 1. Create database
psql -U postgres -c "CREATE DATABASE protech_db;"

# 2. Import schema
psql -U postgres -d protech_db -f database.sql

# 3. Edit config.php - set your PostgreSQL password:
#    define('DB_PASS', 'your_postgres_password');

# 4. Start server (Windows - use 127.0.0.1 instead of localhost)
php -S 127.0.0.1:8000 router.php

# 5. Open http://127.0.0.1:8000 in your browser
```

### Test Accounts (password: `password123`)
| Email | Type |
|-------|------|
| john@example.com | Client |
| mike@example.com | Plumber |
| sarah@example.com | Electrician |

---

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

---

## 🗂️ Project Structure

```
protech/
├── index.html              # Landing page
├── auth.html               # Login/Registration
├── config.php              # Database configuration ← EDIT THIS
├── database.sql            # PostgreSQL schema
├── SETUP_GUIDE.md          # Installation guide
│
├── Core Files:
│   ├── auth_functions.php  # Authentication logic
│   └── db_functions.php    # Database operations
│
├── Client Pages:
│   ├── user.php            # Client dashboard
│   ├── browse_workers.php  # Find professionals
│   ├── book_worker.php     # Book a service
│   ├── my_bookings.php     # View bookings
│   └── review.php          # Leave reviews
│
├── Worker Pages:
│   ├── worker.php          # Worker dashboard
│   └── job_requests.php    # Manage requests
│
└── Handlers:
    ├── login_handler.php
    ├── user_signup_handler.php
    ├── worker_signup_handler.php
    ├── handle_booking.php
    └── logout.php
```

---

## 🗄️ Database Schema (PostgreSQL)

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

---

## 🔧 Configuration Details

### config.php Settings

```php
define('DB_HOST', 'localhost');   // PostgreSQL server
define('DB_PORT', '5432');        // Default PostgreSQL port
define('DB_NAME', 'protech_db');  // Database name
define('DB_USER', 'postgres');    // PostgreSQL username
define('DB_PASS', '');            // ← YOUR PASSWORD HERE
```

### Required PHP Extensions

Make sure these are enabled in `php.ini`:
```ini
extension=pdo_pgsql
extension=pgsql
extension=mbstring
```

---

## 📱 User Flows

### Client Journey
1. **Register** → Creates user account
2. **Browse** → Search workers by skill/location
3. **Book** → Select date, time, describe the job
4. **Wait** → Worker reviews and accepts
5. **Service** → Worker completes the job
6. **Review** → Rate and review the worker

### Worker Journey
1. **Register** → Add skills, experience, hourly rate
2. **Receive** → Get notified of new requests
3. **Accept/Decline** → Review job details
4. **Complete** → Mark job as done
5. **Earn** → Get paid and build reputation

---

## 🔒 Security Notes

- Passwords hashed with bcrypt (`password_hash`)
- Prepared statements prevent SQL injection
- Input sanitization on all user data
- Session-based authentication

---

## 📄 License

Educational/demonstration purposes.
