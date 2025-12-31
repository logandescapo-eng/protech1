"""
ProTech Flask Application
Main application file with all routes
"""

import os
from flask import Flask, render_template, request, redirect, url_for, flash, session
from config import SECRET_KEY, DEBUG
from auth import (
    login_user, register_user, register_worker, logout_user,
    login_required, user_type_required, is_logged_in, get_user_type
)
from db_functions import (
    get_workers, get_worker, get_worker_by_user_id,
    get_user_bookings, get_worker_bookings, get_worker_today_schedule,
    create_booking, update_booking_status, get_booking,
    get_user_stats, get_worker_stats,
    create_review, get_pending_reviews,
    get_service_categories, count_unread_notifications,
    get_initials
)

app = Flask(__name__)
app.secret_key = SECRET_KEY
app.debug = DEBUG

# ==================== HELPER FUNCTIONS ====================

def get_current_user_id():
    """Get current user ID from session"""
    return session.get('user_id')

def get_current_user_name():
    """Get current user name from session"""
    return session.get('user_name', 'User')

# ==================== ROUTES ====================

@app.route('/')
def index():
    """Home page"""
    return render_template('index.html')

@app.route('/auth', methods=['GET', 'POST'])
def auth():
    """Authentication page (login/signup)"""
    if request.method == 'POST':
        # Handle login
        if 'login' in request.form:
            email = request.form.get('email', '').strip()
            password = request.form.get('password', '')
            
            if not email or not password:
                flash('Please fill in all fields', 'error')
                return redirect(url_for('auth'))
            
            result = login_user(email, password)
            
            if result['success']:
                flash('Login successful!', 'success')
                if result['user_type'] == 'worker':
                    return redirect(url_for('worker_dashboard'))
                else:
                    return redirect(url_for('user_dashboard'))
            else:
                flash(result['message'], 'error')
                return redirect(url_for('auth'))
        
        # Handle user signup
        elif 'user_signup' in request.form:
            name = request.form.get('name', '').strip()
            email = request.form.get('email', '').strip()
            phone = request.form.get('phone', '').strip()
            password = request.form.get('password', '')
            
            if not all([name, email, phone, password]):
                flash('Please fill in all fields', 'error')
                return redirect(url_for('auth'))
            
            result = register_user(name, email, phone, password, 'user')
            
            if result['success']:
                flash('Registration successful! Please login.', 'success')
            else:
                flash(result['message'], 'error')
            return redirect(url_for('auth'))
        
        # Handle worker signup
        elif 'worker_signup' in request.form:
            name = request.form.get('name', '').strip()
            email = request.form.get('email', '').strip()
            phone = request.form.get('phone', '').strip()
            password = request.form.get('password', '')
            service_area = request.form.get('address', '').strip()
            skills = request.form.get('skills', '').strip()
            experience = request.form.get('experience', 0)
            
            if not all([name, email, phone, password, service_area, skills, experience]):
                flash('Please fill in all fields', 'error')
                return redirect(url_for('auth'))
            
            try:
                experience = int(experience)
            except (ValueError, TypeError):
                experience = 0
            
            result = register_worker(name, email, phone, password, service_area, skills, experience)
            
            if result['success']:
                flash('Worker registration successful! Please login.', 'success')
            else:
                flash(result['message'], 'error')
            return redirect(url_for('auth'))
    
    # GET request - show auth page
    return render_template('auth.html')

@app.route('/logout')
def logout():
    """Logout user"""
    logout_user()
    flash('Logged out successfully', 'success')
    return redirect(url_for('index'))

@app.route('/user/dashboard')
@login_required
@user_type_required('user')
def user_dashboard():
    """User dashboard"""
    user_id = get_current_user_id()
    user_name = get_current_user_name()
    
    # Get user statistics
    stats = get_user_stats(user_id)
    
    # Get upcoming bookings
    upcoming_bookings = get_user_bookings(user_id, None, 5)
    upcoming_bookings = [b for b in upcoming_bookings if b['status'] in ['pending', 'confirmed', 'in_progress']]
    
    # Get initials for avatar
    initials = get_initials(user_name)
    
    return render_template('user_dashboard.html',
                         user_name=user_name,
                         stats=stats,
                         upcoming_bookings=upcoming_bookings,
                         initials=initials)

@app.route('/worker/dashboard')
@login_required
@user_type_required('worker')
def worker_dashboard():
    """Worker dashboard"""
    user_id = get_current_user_id()
    user_name = get_current_user_name()
    
    # Get worker info
    worker = get_worker_by_user_id(user_id)
    if not worker:
        flash('Worker profile not found', 'error')
        return redirect(url_for('logout'))
    
    worker_id = worker['id']
    
    # Get worker statistics
    stats = get_worker_stats(worker_id)
    
    # Get pending job requests
    pending_requests = get_worker_bookings(worker_id, 'pending', 5)
    
    # Get today's schedule
    today_schedule = get_worker_today_schedule(worker_id)
    
    # Get recent completed jobs
    recent_completed = get_worker_bookings(worker_id, 'completed', 5)
    
    # Get notifications count
    unread_notifications = count_unread_notifications(user_id)
    
    # Get initials for avatar
    initials = get_initials(user_name)
    
    return render_template('worker_dashboard.html',
                         user_name=user_name,
                         worker=worker,
                         stats=stats,
                         pending_requests=pending_requests,
                         today_schedule=today_schedule,
                         recent_completed=recent_completed,
                         unread_notifications=unread_notifications,
                         initials=initials)

@app.route('/workers')
@login_required
def browse_workers():
    """Browse workers page"""
    filters = {}
    
    if request.args.get('skill'):
        filters['skill'] = request.args.get('skill')
    if request.args.get('location'):
        filters['service_area'] = request.args.get('location')
    if request.args.get('min_rating'):
        try:
            filters['min_rating'] = float(request.args.get('min_rating'))
        except (ValueError, TypeError):
            pass
    
    filters['limit'] = 20
    
    workers = get_workers(filters)
    categories = get_service_categories()
    
    return render_template('browse_workers.html', workers=workers, categories=categories)

@app.route('/book/<int:worker_id>', methods=['GET', 'POST'])
@login_required
def book_worker(worker_id):
    """Book a worker"""
    user_id = get_current_user_id()
    worker = get_worker(worker_id)
    
    if not worker:
        flash('Worker not found', 'error')
        return redirect(url_for('browse_workers'))
    
    if request.method == 'POST':
        data = {
            'title': request.form.get('title', '').strip(),
            'description': request.form.get('description', '').strip(),
            'scheduled_date': request.form.get('scheduled_date', ''),
            'scheduled_time': request.form.get('scheduled_time', ''),
            'estimated_duration': request.form.get('estimated_duration', 60),
            'address': request.form.get('address', '').strip(),
            'price': request.form.get('price', 0),
            'service_category_id': request.form.get('service_category_id')
        }
        
        if not all([data['title'], data['scheduled_date'], data['scheduled_time'], data['address']]):
            flash('Please fill in all required fields', 'error')
            return redirect(url_for('book_worker', worker_id=worker_id))
        
        try:
            data['estimated_duration'] = int(data['estimated_duration'])
            data['price'] = float(data['price'])
            if data.get('service_category_id'):
                data['service_category_id'] = int(data['service_category_id'])
        except (ValueError, TypeError):
            flash('Invalid input values', 'error')
            return redirect(url_for('book_worker', worker_id=worker_id))
        
        result = create_booking(user_id, worker_id, data)
        
        if result['success']:
            flash('Booking request submitted successfully!', 'success')
            return redirect(url_for('user_dashboard'))
        else:
            flash(result.get('message', 'Failed to create booking'), 'error')
    
    categories = get_service_categories()
    return render_template('book_worker.html', worker=worker, categories=categories)

@app.route('/bookings')
@login_required
def my_bookings():
    """User's bookings page"""
    user_id = get_current_user_id()
    user_type = get_user_type()
    
    if user_type == 'worker':
        worker = get_worker_by_user_id(user_id)
        if worker:
            bookings = get_worker_bookings(worker['id'])
        else:
            bookings = []
    else:
        bookings = get_user_bookings(user_id)
    
    return render_template('my_bookings.html', bookings=bookings, user_type=user_type)

@app.route('/booking/<int:booking_id>/status', methods=['POST'])
@login_required
def update_booking(booking_id):
    """Update booking status"""
    user_id = get_current_user_id()
    user_type = get_user_type()
    action = request.form.get('action', '')
    
    booking = get_booking(booking_id)
    if not booking:
        flash('Booking not found', 'error')
        return redirect(url_for('my_bookings'))
    
    # Check authorization
    if user_type == 'worker':
        worker = get_worker_by_user_id(user_id)
        if not worker or booking['worker_id'] != worker['id']:
            flash('Unauthorized', 'error')
            return redirect(url_for('my_bookings'))
    else:
        if booking['user_id'] != user_id:
            flash('Unauthorized', 'error')
            return redirect(url_for('my_bookings'))
    
    # Map actions to statuses
    status_map = {
        'accept': 'confirmed',
        'decline': 'cancelled',
        'complete': 'completed',
        'cancel': 'cancelled'
    }
    
    if action in status_map:
        result = update_booking_status(booking_id, status_map[action], user_id)
        if result['success']:
            flash(f'Booking {action}ed successfully', 'success')
        else:
            flash(result.get('message', 'Failed to update booking'), 'error')
    
    return redirect(url_for('my_bookings'))

@app.route('/review/<int:booking_id>', methods=['GET', 'POST'])
@login_required
def review(booking_id):
    """Leave a review"""
    user_id = get_current_user_id()
    booking = get_booking(booking_id)
    
    if not booking:
        flash('Booking not found', 'error')
        return redirect(url_for('user_dashboard'))
    
    if booking['user_id'] != user_id:
        flash('Unauthorized', 'error')
        return redirect(url_for('user_dashboard'))
    
    if booking['status'] != 'completed':
        flash('Can only review completed bookings', 'error')
        return redirect(url_for('user_dashboard'))
    
    if request.method == 'POST':
        rating = request.form.get('rating')
        comment = request.form.get('comment', '').strip()
        
        try:
            rating = int(rating)
            if rating < 1 or rating > 5:
                raise ValueError()
        except (ValueError, TypeError):
            flash('Please provide a valid rating (1-5)', 'error')
            return redirect(url_for('review', booking_id=booking_id))
        
        result = create_review(booking_id, user_id, booking['worker_id'], rating, comment)
        
        if result['success']:
            flash('Review submitted successfully!', 'success')
            return redirect(url_for('user_dashboard'))
        else:
            flash(result.get('message', 'Failed to create review'), 'error')
    
    return render_template('review.html', booking=booking)

# ==================== ERROR HANDLERS ====================

@app.errorhandler(404)
def not_found(error):
    return render_template('404.html'), 404

@app.errorhandler(500)
def internal_error(error):
    return render_template('500.html'), 500

# ==================== RUN APPLICATION ====================

if __name__ == '__main__':
    # Bind to 0.0.0.0 for cloud hosting, 127.0.0.1 for local dev
    # Cloud platforms set PORT env var, so use that or default to 5000
    port = int(os.getenv('PORT', 5000))
    # Always bind to 0.0.0.0 for cloud compatibility
    host = '0.0.0.0'
    app.run(host=host, port=port, debug=DEBUG)
