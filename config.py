"""
Database Configuration for ProTech
This file contains database connection settings.
The database itself will NOT be changed - we're just connecting differently.
"""

import os

# Database connection settings (same as PHP config.php)
DB_HOST = os.getenv('DB_HOST', '127.0.0.1')
DB_PORT = os.getenv('DB_PORT', '5432')
DB_NAME = os.getenv('DB_NAME', 'protech_db')
DB_USER = os.getenv('DB_USER', 'postgres')
DB_PASS = os.getenv('DB_PASS', 'postgres123')  # Update this with your PostgreSQL password

# Flask configuration
SECRET_KEY = os.getenv('SECRET_KEY', 'your-secret-key-change-this-in-production')
DEBUG = os.getenv('FLASK_DEBUG', 'True').lower() == 'true'

# Database connection string
DATABASE_URL = f"postgresql://{DB_USER}:{DB_PASS}@{DB_HOST}:{DB_PORT}/{DB_NAME}"
