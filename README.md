# ProTech - Professional Services Platform

**IT Innovation in Business — Final Project (Full-Stack Website Development)**

A secure, scalable marketplace connecting clients with professional service workers. Built for the *Web Technology in Business* + *Web Application Development* final project requirements.

## Rubric alignment (200 pts)

| Requirement | Implementation |
|-------------|----------------|
| **Django + Django Templates** | Server-rendered Jinja2/Django templates in `templates/` |
| **Auth & RBAC** | Registration, login, logout, `@user_type_required`, Django Admin |
| **Password reset** | `/password-reset/` (console email in dev) |
| **Admin / CMS** | `/admin/` — users, workers, bookings, reviews, escrow |
| **Security** | CSRF middleware, hashed passwords, `.env` + `.gitignore`, XSS/ORM protections |
| **Unit + integration tests** | `python manage.py test` — models + auth/booking flows |
| **Docker multi-service** | `docker-compose.yml` — PostgreSQL, Redis, Django, Nginx |
| **Logging** | Structured loggers in `settings.py` → console + `logs/django.log` |
| **Redis caching** | Worker/category lists cached (`protech_project/cache_utils.py`) |
| **README & linting** | This file + `flake8` / `black` in CI |

**Technology Stack:**
- **Backend:** Django 5.2.15 + Django REST Framework
- **Database:** PostgreSQL 15
- **Cache:** Redis 7
- **Frontend:** Django Templates (Jinja2) + HTML, CSS, JavaScript
- **Web Server:** Gunicorn + Nginx
- **Containerization:** Docker + Docker Compose

---

## 📋 Table of Contents

- [Project Description](#project-description)
- [Features](#features)
- [Technology Stack](#technology-stack)
- [Prerequisites](#prerequisites)
- [Installation](#installation)
- [Docker Setup](#docker-setup)
- [Testing](#testing)
- [Caching Strategy](#caching-strategy)
- [Logging](#logging)
- [Security](#security)
- [Project Structure](#project-structure)
- [API Endpoints](#api-endpoints)
- [Admin Panel](#admin-panel)
- [Deployment](#deployment)

---

## Project Description

ProTech is a full-stack web application that serves as a marketplace connecting clients with professional service workers. The platform includes:

- User authentication and role-based access control
- Service booking and management
- Review and rating system
- Escrow payment system
- Real-time messaging
- Admin panel for content management

---

## Features

### Authentication & Authorization
- User registration, login, logout
- Role-based access control (Client, Worker, Admin)
- Secure password handling with Django's built-in password hashing
- Session-based authentication
- Password reset functionality

### Content Management
- Django Admin interface for managing all content
- CRUD operations for users, workers, bookings, reviews
- Service category management

### Security
- Protection against XSS, CSRF, and SQL injection (Django built-in)
- Environment variables hidden using .env
- Secure session cookies in production
- HSTS, SSL redirect in production

### Caching
- Redis caching for frequently accessed data
- Cached user sessions
- Cached service categories and worker lists
- Configurable cache timeout (default: 300 seconds)

### Logging
- Structured logging with multiple log levels (INFO, DEBUG, WARNING, ERROR)
- Logs to both console and file
- Separate loggers for each app (users, bookings, escrow)
- Configurable log level via environment variable

---

## Technology Stack

**Backend:**
- Django 5.2.15
- Django REST Framework 3.17.1
- Python 3.11

**Database:**
- PostgreSQL 15
- psycopg2-binary 2.9.12

**Caching:**
- Redis 7
- django-redis 7.0.0

**Web Server:**
- Gunicorn 26.0.0
- Nginx (alpine)

**Development Tools:**
- python-dotenv 1.2.2

**Testing:**
- Django Test Framework
- Unit tests for models and views

**Code Quality:**
- flake8 (linting)
- black (code formatting)
- isort (import sorting)

---

## Prerequisites

- Docker 20.10+
- Docker Compose 2.0+
- Python 3.11+ (for local development)
- Git

---

## Installation

### Local Development Setup

1. **Clone the repository:**
```bash
git clone <repository-url>
cd protech
```

2. **Create virtual environment:**
```bash
python -m venv venv
venv\Scripts\activate  # On Windows
source venv/bin/activate  # On Linux/Mac
```

3. **Install dependencies:**
```bash
pip install -r requirements.txt
```

4. **Configure environment variables:**
```bash
cp .env.example .env
# Edit .env with your configuration
```

5. **Run migrations and demo data:**
```bash
python manage.py migrate
python manage.py seed_demo
```

6. **Create superuser (optional):**
```bash
python manage.py createsuperuser
```

7. **Run development server:**
```bash
python manage.py runserver
```

8. **Access the application:**
- Frontend: http://127.0.0.1:8000
- Admin Panel: http://127.0.0.1:8000/admin

---

## Docker Setup

### Using Docker Compose (Recommended)

1. **Configure environment variables:**
```bash
cp .env.example .env
# Edit .env with your configuration
```

2. **Build and start all services:**
```bash
docker compose up --build
```

The backend entrypoint runs **migrate**, **collectstatic**, and **seed_demo** automatically.

3. **Access the application:**
- Frontend (via Nginx): http://localhost
- Backend (direct): http://localhost:8000
- Admin Panel: http://localhost/admin
- Health check: http://localhost/health/

4. **Demo login (after seed):**
- Client: `john@example.com` / `password123`
- Worker: `mike@example.com` / `password123`

5. **Create superuser:**
```bash
docker-compose exec backend python manage.py createsuperuser
```

6. **Stop services:**
```bash
docker-compose down
```

7. **Stop services and remove volumes:**
```bash
docker-compose down -v
```

### Docker Services

The docker-compose.yml includes the following services:

- **db**: PostgreSQL 15 database
- **redis**: Redis 7 for caching
- **backend**: Django application with Gunicorn
- **nginx**: Nginx reverse proxy

---

## Testing

### Run All Tests

```bash
# Local development
python manage.py test

# Docker
docker-compose exec backend python manage.py test
```

### Run Specific App Tests

```bash
# Users app
python manage.py test users

# Bookings app
python manage.py test bookings

# Reviews app
python manage.py test reviews

# Escrow app
python manage.py test escrow
```

### Run Tests with Coverage

```bash
pip install coverage
coverage run --source='.' manage.py test
coverage report
coverage html
```

### Test Coverage

The project includes unit tests for:
- User model and authentication
- Worker model
- Booking model
- Review model
- Escrow/wallet models
- Service categories
- Messages and notifications

---

## Caching Strategy

### Redis Configuration

The application uses Redis for caching with the following strategy:

1. **Session Caching**: User sessions are stored in Redis for better performance
2. **Query Caching**: Frequently accessed data is cached:
   - Service categories (cache for 1 hour)
   - Worker listings (cache for 5 minutes)
   - User profiles (cache for 10 minutes)
3. **Cache Invalidation**: Cache is automatically invalidated when data is updated

### Cache Configuration

Cache settings in `protech_project/settings.py`:
```python
CACHES = {
    'default': {
        'BACKEND': 'django_redis.cache.RedisCache',
        'LOCATION': 'redis://redis:6379/1',
        'OPTIONS': {
            'CLIENT_CLASS': 'django_redis.client.DefaultClient',
        },
        'KEY_PREFIX': 'protech',
        'TIMEOUT': 300,
    }
}
```

### Manual Cache Management

```bash
# Clear all cache
docker-compose exec backend python manage.py shell
>>> from django.core.cache import cache
>>> cache.clear()
```

---

## Logging

### Log Configuration

The application uses structured logging with the following configuration:

- **Log Levels**: INFO, DEBUG, WARNING, ERROR
- **Log Handlers**: Console and File
- **Log Location**: `logs/django.log`
- **Log Format**: `{levelname} {asctime} {module} {process} {thread} {message}`

### Log Files

Logs are stored in the `logs/` directory:
- `django.log`: Main application log

### Viewing Logs

```bash
# View logs in real-time
tail -f logs/django.log

# Docker logs
docker-compose logs -f backend
```

### Log Levels

Set log level via environment variable:
```bash
# In .env file
DJANGO_LOG_LEVEL=DEBUG  # For development
DJANGO_LOG_LEVEL=INFO   # For production
```

---

## Security

### Security Features

1. **CSRF Protection**: Enabled by Django
2. **XSS Protection**: Enabled by Django templates
3. **SQL Injection**: Protected by Django ORM
4. **Password Security**: Hashed using Django's password hasher
5. **Session Security**: Secure cookies in production
6. **HSTS**: Enabled in production
7. **SSL Redirect**: Enabled in production

### Environment Variables

Sensitive data is stored in environment variables:
- `SECRET_KEY`: Django secret key
- `DB_PASS`: Database password
- `REDIS_URL`: Redis connection string

### Security Headers

Production mode includes:
- SECURE_SSL_REDIRECT
- SESSION_COOKIE_SECURE
- CSRF_COOKIE_SECURE
- SECURE_HSTS_SECONDS
- SECURE_CONTENT_TYPE_NOSNIFF
- X_FRAME_OPTIONS

---

## Project Structure

```
protech/
├── protech_project/          # Django project settings
│   ├── __init__.py
│   ├── settings.py           # Main settings with caching, logging
│   ├── urls.py               # Main URL configuration
│   ├── wsgi.py               # WSGI configuration
│   └── asgi.py               # ASGI configuration
├── users/                    # Users app
│   ├── models.py             # User, Worker, Message models
│   ├── views.py              # Authentication views
│   ├── urls.py               # User URLs
│   ├── admin.py              # Admin configuration
│   └── tests.py              # Unit tests
├── bookings/                 # Bookings app
│   ├── models.py             # Booking model
│   ├── views.py              # Booking views
│   ├── urls.py               # Booking URLs
│   ├── admin.py              # Admin configuration
│   └── tests.py              # Unit tests
├── reviews/                  # Reviews app
│   ├── models.py             # Review model
│   ├── views.py              # Review views
│   ├── urls.py               # Review URLs
│   ├── admin.py              # Admin configuration
│   └── tests.py              # Unit tests
├── escrow/                   # Escrow app
│   ├── models.py             # Wallet, Escrow models
│   ├── views.py              # Escrow views
│   ├── urls.py               # Escrow URLs
│   ├── admin.py              # Admin configuration
│   └── tests.py              # Unit tests
├── templates/                # Django templates
├── static/                   # Static files
├── media/                    # User uploaded files
├── logs/                     # Application logs
├── nginx/                    # Nginx configuration
│   └── nginx.conf
├── Dockerfile.backend        # Backend Dockerfile
├── docker-compose.yml        # Docker Compose configuration
├── requirements.txt          # Python dependencies
├── .env.example              # Environment variables template
├── .flake8                   # Flake8 configuration
├── pyproject.toml            # Black and isort configuration
└── manage.py                 # Django management script
```

---

## API Endpoints

### Authentication
- `GET /` - Home page
- `POST /login/` - User login
- `POST /logout/` - User logout
- `POST /register/` - User registration
- `GET /profile/` - User profile (requires login)

### Bookings
- `GET /bookings/` - List bookings (requires login)
- `POST /bookings/create/` - Create booking (requires login)
- `GET /bookings/<id>/` - Booking details (requires login)

### Reviews
- `GET /reviews/` - List reviews (requires login)
- `POST /reviews/create/<booking_id>/` - Create review (requires login)

### Escrow
- `GET /escrow/wallet/` - View wallet (requires login)
- `POST /escrow/fund/<booking_id>/` - Fund escrow (requires login)
- `POST /escrow/release/<booking_id>/` - Release escrow (requires login)
- `POST /escrow/refund/<booking_id>/` - Refund escrow (requires login)

### Admin
- `GET /admin/` - Django Admin panel (requires staff)

---

## Admin Panel

Access the Django Admin panel at `/admin/` with superuser credentials.

### Admin Features
- User management
- Worker profile management
- Booking management
- Review moderation
- Escrow transaction monitoring
- Service category management

---

## Deployment

### Production Deployment

1. **Set environment variables:**
```bash
# .env file for production
DEBUG=False
SECRET_KEY=<your-secret-key>
ALLOWED_HOSTS=yourdomain.com,www.yourdomain.com
DB_NAME=protech_db
DB_USER=postgres
DB_PASS=<strong-password>
DB_HOST=db
DB_PORT=5432
REDIS_URL=redis://redis:6379/1
ESCROW_PLATFORM_FEE_PERCENT=5.0
DJANGO_LOG_LEVEL=INFO
```

2. **Build and deploy:**
```bash
docker-compose -f docker-compose.yml up -d --build
```

3. **Run migrations:**
```bash
docker-compose exec backend python manage.py migrate
```

4. **Collect static files:**
```bash
docker-compose exec backend python manage.py collectstatic --noinput
```

5. **Create superuser:**
```bash
docker-compose exec backend python manage.py createsuperuser
```

### Deployment Platforms

The application is containerized and can be deployed to:
- AWS ECS
- Google Cloud Run
- Azure Container Instances
- DigitalOcean App Platform
- Railway
- Render

---

## Code Quality

### Linting

Run flake8 for code linting:
```bash
flake8 .
```

### Formatting

Run black for code formatting:
```bash
black .
```

### Import Sorting

Run isort for import sorting:
```bash
isort .
```

### Run All Quality Checks

```bash
flake8 . && black . && isort .
```

---

## License

This project is for educational purposes.

---

## Contact

For questions or support, please open an issue in the repository.
