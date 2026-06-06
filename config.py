"""
Database Configuration for ProTech
This file contains database connection settings.
The database itself will NOT be changed - we're just connecting differently.
"""

import os
from urllib.parse import urlparse

# Railway provides DATABASE_URL, parse it if available
DATABASE_URL = os.getenv('DATABASE_URL')

if DATABASE_URL:
    # Parse Railway DATABASE_URL (format: postgresql://user:password@host:port/dbname)
    # Railway sometimes uses postgres:// instead of postgresql://
    if DATABASE_URL.startswith('postgres://'):
        DATABASE_URL = DATABASE_URL.replace('postgres://', 'postgresql://', 1)
    
    parsed = urlparse(DATABASE_URL)
    DB_HOST = parsed.hostname
    DB_PORT = str(parsed.port) if parsed.port else '5432'
    DB_NAME = parsed.path.lstrip('/')
    DB_USER = parsed.username
    DB_PASS = parsed.password
    # Reconstruct DATABASE_URL for psycopg2
    DATABASE_URL = f"postgresql://{DB_USER}:{DB_PASS}@{DB_HOST}:{DB_PORT}/{DB_NAME}"
else:
    # Fallback to individual environment variables (for local dev or docker-compose)
    DB_HOST = os.getenv('DB_HOST', '127.0.0.1')
    DB_PORT = os.getenv('DB_PORT', '5432')
    DB_NAME = os.getenv('DB_NAME', 'protech_db')
    DB_USER = os.getenv('DB_USER', 'postgres')
    DB_PASS = os.getenv('DB_PASS', 'postgres123')
    DATABASE_URL = f"postgresql://{DB_USER}:{DB_PASS}@{DB_HOST}:{DB_PORT}/{DB_NAME}"

# Flask configuration
_on_cloud = bool(
    os.getenv('RAILWAY_ENVIRONMENT')
    or os.getenv('RAILWAY_PUBLIC_DOMAIN')
    or os.getenv('RENDER')
    or os.getenv('RENDER_SERVICE_ID')
    or os.getenv('DATABASE_URL')
)
SECRET_KEY = os.getenv('SECRET_KEY', 'dev-secret-change-in-production')
DEBUG = os.getenv('FLASK_DEBUG', 'false' if _on_cloud else 'true').lower() == 'true'

# Escrow (platform holds funds until job completion)
ESCROW_PLATFORM_FEE_PERCENT = float(os.getenv('ESCROW_PLATFORM_FEE_PERCENT', '5'))
ESCROW_DEMO_DEPOSIT_MAX = float(os.getenv('ESCROW_DEMO_DEPOSIT_MAX', '1000'))
