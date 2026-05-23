"""
Authentication functions for ProTech
Converted from PHP auth_functions.php
"""

import bcrypt
from db_connection import get_db_cursor, get_db_connection
from functools import wraps
from flask import session, redirect, url_for, flash, has_request_context

def sanitize_input(data):
    """Sanitize user input"""
    if data is None:
        return ''
    return str(data).strip()

def register_user(name, email, phone, password, user_type):
    """Register a new user"""
    name = sanitize_input(name)
    email = sanitize_input(email)
    phone = sanitize_input(phone)
    user_type = sanitize_input(user_type)
    
    # Hash password
    hashed_password = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')
    
    conn = get_db_connection()
    try:
        cur = get_db_cursor(conn)
        
        # Check if email already exists
        cur.execute("SELECT id FROM users WHERE email = %s", (email,))
        if cur.fetchone():
            return {'success': False, 'message': 'Email already exists'}
        
        # Insert user
        cur.execute(
            "INSERT INTO users (name, email, phone, password, user_type) VALUES (%s, %s, %s, %s, %s) RETURNING id",
            (name, email, phone, hashed_password, user_type)
        )
        user_id = cur.fetchone()['id']
        conn.commit()

        try:
            from escrow_service import ensure_wallet
            ensure_wallet(user_id)
        except Exception:
            pass
        
        return {'success': True, 'user_id': user_id, 'message': 'Registration successful'}
        
    except Exception as e:
        conn.rollback()
        return {'success': False, 'message': f'Registration failed: {str(e)}'}
    finally:
        cur.close()
        conn.close()

def register_worker(name, email, phone, password, service_area, skills, experience):
    """Register a worker with additional info"""
    # First register as user
    result = register_user(name, email, phone, password, 'worker')
    
    if result['success']:
        user_id = result['user_id']
        service_area = sanitize_input(service_area)
        skills = sanitize_input(skills)
        experience = int(experience) if experience else 0
        
        conn = get_db_connection()
        try:
            cur = get_db_cursor(conn)
            
            # Insert worker details
            cur.execute(
                "INSERT INTO workers (user_id, service_area, skills, experience) VALUES (%s, %s, %s, %s)",
                (user_id, service_area, skills, experience)
            )
            conn.commit()
            
            return {'success': True, 'message': 'Worker registration successful'}
            
        except Exception as e:
            conn.rollback()
            return {'success': False, 'message': f'Worker details registration failed: {str(e)}'}
        finally:
            cur.close()
            conn.close()
    
    return result

def login_user(email, password):
    """Login user and return result"""
    email = sanitize_input(email)
    
    conn = get_db_connection()
    try:
        cur = get_db_cursor(conn)
        
        cur.execute(
            "SELECT id, name, email, password, user_type FROM users WHERE email = %s",
            (email,)
        )
        user = cur.fetchone()
        
        if user:
            # Verify password
            # Convert PHP's $2y$ to Python's $2b$ format if needed
            stored_hash = user['password']
            if stored_hash.startswith('$2y$'):
                stored_hash = '$2b$' + stored_hash[4:]
            
            if bcrypt.checkpw(password.encode('utf-8'), stored_hash.encode('utf-8')):
                # Set session variables
                session['user_id'] = user['id']
                session['user_name'] = user['name']
                session['user_email'] = user['email']
                session['user_type'] = user['user_type']
                session['logged_in'] = True
                
                return {
                    'success': True,
                    'user_type': user['user_type'],
                    'message': 'Login successful'
                }
            else:
                return {'success': False, 'message': 'Invalid password'}
        else:
            return {'success': False, 'message': 'User not found'}
            
    except Exception as e:
        return {'success': False, 'message': f'Login failed: {str(e)}'}
    finally:
        cur.close()
        conn.close()

def is_logged_in():
    """Check if user is logged in"""
    return session.get('logged_in', False)

def get_user_type():
    """Get current user type from session"""
    return session.get('user_type')

def logout_user():
    """Logout user"""
    session.clear()
    return {'success': True, 'message': 'Logged out successfully'}

# Decorator to require login
def login_required(f):
    """Decorator to require login"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not is_logged_in():
            flash('Please login to access this page.', 'error')
            return redirect(url_for('auth'))
        return f(*args, **kwargs)
    return decorated_function

# Decorator to require specific user type
def user_type_required(user_type):
    """Decorator to require specific user type"""
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            if not is_logged_in():
                flash('Please login to access this page.', 'error')
                return redirect(url_for('auth'))
            if get_user_type() != user_type:
                flash('You do not have permission to access this page.', 'error')
                return redirect(url_for('auth'))
            return f(*args, **kwargs)
        return decorated_function
    return decorator
