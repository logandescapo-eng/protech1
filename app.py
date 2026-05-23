"""
ProTech Flask Application
Main application file with all routes
"""

import os
import bcrypt
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
    create_review, get_pending_reviews, get_reviews_by_user, get_worker_reviews,
    get_service_categories, count_unread_notifications, get_notifications,
    mark_notification_read, mark_all_notifications_read,
    get_user_favorites, add_favorite, remove_favorite,
    get_user_by_id, update_user_profile, update_worker_profile,
    get_message_contacts, get_messages_between, send_message,
    mark_messages_read, count_unread_messages,
    get_initials, create_notification
)
from escrow_service import (
    ensure_wallet, get_wallet, get_wallet_transactions, get_escrow_vault_summary,
    get_escrow_for_booking, deposit_demo_funds, fund_escrow, release_escrow, refund_escrow,
)
from config import ESCROW_PLATFORM_FEE_PERCENT

app = Flask(__name__)
app.secret_key = SECRET_KEY
app.debug = DEBUG

if os.getenv('RAILWAY_ENVIRONMENT') or os.getenv('DATABASE_URL'):
    from werkzeug.middleware.proxy_fix import ProxyFix
    app.wsgi_app = ProxyFix(app.wsgi_app, x_for=1, x_proto=1, x_host=1)
    app.config['SESSION_COOKIE_SECURE'] = True
    app.config['SESSION_COOKIE_SAMESITE'] = 'Lax'

# ==================== HELPER FUNCTIONS ====================

def get_current_user_id():
    """Get current user ID from session"""
    return session.get('user_id')

def get_current_user_name():
    """Get current user name from session"""
    return session.get('user_name', 'User')

def dashboard_url():
    """URL for the logged-in user's main dashboard"""
    if get_user_type() == 'worker':
        return url_for('worker_dashboard')
    return url_for('user_dashboard')

@app.context_processor
def inject_layout_context():
    """Shared template variables for nav badges and links"""
    ctx = {
        'is_logged_in': is_logged_in(),
        'layout_dashboard_url': dashboard_url() if is_logged_in() else url_for('index'),
        'platform_fee_percent': ESCROW_PLATFORM_FEE_PERCENT,
    }
    if is_logged_in():
        uid = session.get('user_id')
        ctx.update({
            'layout_unread_notifications': count_unread_notifications(uid),
            'layout_unread_messages': count_unread_messages(uid),
            'layout_user_type': get_user_type(),
        })
    else:
        ctx.update({
            'layout_unread_notifications': 0,
            'layout_unread_messages': 0,
            'layout_user_type': None,
        })
    return ctx


def _render_landing_page(title, subtitle, content_template, cta_label=None, cta_url=None):
    return render_template(
        'landing/page.html',
        page_title=title,
        page_subtitle=subtitle,
        content_template=content_template,
        cta_label=cta_label,
        cta_url=cta_url,
    )

# ==================== ROUTES ====================

@app.route('/health')
def health():
    """Health check for Railway (includes DB connectivity)."""
    try:
        from db_connection import get_db_connection
        conn = get_db_connection()
        cur = conn.cursor()
        cur.execute('SELECT 1')
        cur.close()
        conn.close()
        return {'status': 'ok', 'database': 'connected'}, 200
    except Exception as e:
        return {'status': 'error', 'database': str(e)}, 503

@app.route('/')
def index():
    """Home page"""
    return render_template('index.html')


@app.route('/start/client')
def start_client():
    """Find a professional — dashboard or sign up"""
    if is_logged_in():
        if get_user_type() == 'user':
            return redirect(url_for('browse_workers'))
        return redirect(url_for('worker_dashboard'))
    return redirect(url_for('auth', tab='user'))


@app.route('/start/worker')
def start_worker():
    """Become a worker — dashboard or worker signup"""
    if is_logged_in():
        if get_user_type() == 'worker':
            return redirect(url_for('worker_dashboard'))
        return redirect(url_for('user_dashboard'))
    return redirect(url_for('auth', tab='worker'))


@app.route('/contact', methods=['POST'])
def contact_submit():
    """Landing page contact form"""
    name = request.form.get('name', '').strip()
    email = request.form.get('email', '').strip()
    if name and email:
        flash('Thank you for your message! We will get back to you soon.', 'success')
    else:
        flash('Please provide your name and email.', 'error')
    return redirect(url_for('index') + '#contact')


@app.route('/pricing')
def landing_pricing():
    return _render_landing_page(
        'Pricing',
        'Simple, transparent fees built around secure escrow.',
        'landing/pricing_content.html',
        'Get started',
        url_for('start_client'),
    )


@app.route('/faq')
def landing_faq():
    return _render_landing_page(
        'Frequently Asked Questions',
        'Answers to common questions about ProTech.',
        'landing/faq_content.html',
        'Contact support',
        url_for('landing_support'),
    )


@app.route('/support')
def landing_support():
    return _render_landing_page(
        'Support',
        'We are here to help.',
        'landing/support_content.html',
    )


@app.route('/privacy')
def landing_privacy():
    return _render_landing_page('Privacy Policy', None, 'landing/privacy_content.html')


@app.route('/terms')
def landing_terms():
    return _render_landing_page('Terms of Service', None, 'landing/terms_content.html')


@app.route('/careers')
def landing_careers():
    return _render_landing_page('Careers', 'Build the future of local services.', 'landing/careers_content.html')


@app.route('/blog')
def landing_blog():
    return _render_landing_page('Blog', 'News and guides from ProTech.', 'landing/blog_content.html')


@app.route('/success-stories')
def landing_success_stories():
    return _render_landing_page(
        'Success Stories',
        'Real professionals and clients on ProTech.',
        'landing/success_stories_content.html',
        'Become a worker',
        url_for('start_worker'),
    )


@app.route('/resources')
def landing_resources():
    return _render_landing_page(
        'Resources',
        'Guides for clients and professionals.',
        'landing/resources_content.html',
    )

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
    pending_reviews = get_pending_reviews(user_id)
    recent_completed = [b for b in get_user_bookings(user_id) if b['status'] == 'completed'][:5]
    pending_review_ids = {b['id'] for b in pending_reviews}
    
    return render_template('user.html',
                         user_name=user_name,
                         stats=stats,
                         upcoming_bookings=upcoming_bookings,
                         pending_reviews=pending_reviews,
                         pending_review_ids=pending_review_ids,
                         recent_completed=recent_completed,
                         initials=initials,
                         unread_notifications=count_unread_notifications(user_id),
                         unread_messages=count_unread_messages(user_id))

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
    
    return render_template('worker.html',
                         user_name=user_name,
                         worker=worker,
                         stats=stats,
                         pending_requests=pending_requests,
                         today_schedule=today_schedule,
                         recent_completed=recent_completed,
                         unread_notifications=unread_notifications,
                         unread_messages=count_unread_messages(user_id),
                         initials=initials)

@app.route('/workers')
@login_required
@user_type_required('user')
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
@user_type_required('user')
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
            flash('Booking created. Place funds in escrow to secure payment.', 'success')
            return redirect(url_for('escrow_pay', booking_id=result['booking_id']))
        else:
            flash(result.get('message', 'Failed to create booking'), 'error')
    
    categories = get_service_categories()
    return render_template(
        'book_worker.html',
        worker=worker,
        categories=categories,
        platform_fee_percent=ESCROW_PLATFORM_FEE_PERCENT,
    )

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
    
    pending_review_ids = set()
    if user_type != 'worker':
        pending_review_ids = {b['id'] for b in get_pending_reviews(user_id)}

    wallet = get_wallet(user_id)
    for b in bookings:
        b['escrow'] = get_escrow_for_booking(b['id'])
    
    return render_template('my_bookings.html',
                         bookings=bookings,
                         user_type=user_type,
                         pending_review_ids=pending_review_ids,
                         wallet=wallet,
                         platform_fee_percent=ESCROW_PLATFORM_FEE_PERCENT)

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
            if action == 'complete':
                escrow_result = release_escrow(booking_id)
                if escrow_result.get('success') and escrow_result.get('worker_payout') is not None:
                    flash(
                        f'Escrow released: ${escrow_result["worker_payout"]:.2f} paid to professional '
                        f'({ESCROW_PLATFORM_FEE_PERCENT}% platform fee applied).',
                        'success',
                    )
                    booking = get_booking(booking_id)
                    if booking:
                        worker = get_worker(booking['worker_id'])
                        if worker:
                            create_notification(
                                worker['user_id'], 'Payment received',
                                f'${escrow_result["worker_payout"]:.2f} from escrow for "{booking["title"]}".',
                                'system', '/wallet',
                            )
                elif escrow_result.get('message') != 'No escrow funds held for this booking':
                    flash(escrow_result.get('message', 'Escrow release failed'), 'error')
            elif action in ('decline', 'cancel'):
                refund_result = refund_escrow(booking_id)
                if refund_result.get('success') and refund_result.get('refunded'):
                    flash(f'${refund_result["refunded"]:.2f} returned to client wallet from escrow.', 'success')
                    booking = get_booking(booking_id)
                    if booking:
                        create_notification(
                            booking['user_id'], 'Escrow refunded',
                            f'${refund_result["refunded"]:.2f} was refunded to your wallet.',
                            'system', '/wallet',
                        )
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

# ==================== ACCOUNT PAGES ====================

@app.route('/notifications')
@login_required
def notifications_page():
    """View and manage notifications"""
    user_id = get_current_user_id()
    if request.args.get('mark_all'):
        mark_all_notifications_read(user_id)
        flash('All notifications marked as read', 'success')
        return redirect(url_for('notifications_page'))
    nid = request.args.get('read')
    if nid:
        try:
            mark_notification_read(int(nid))
        except (ValueError, TypeError):
            pass
        return redirect(url_for('notifications_page'))
    items = get_notifications(user_id, limit=50)
    return render_template('notifications.html', notifications=items)

@app.route('/messages', methods=['GET', 'POST'])
@login_required
def messages_page():
    """Chat with booking contacts"""
    user_id = get_current_user_id()
    user_type = get_user_type()
    contacts = get_message_contacts(user_id, user_type)
    other_id = request.args.get('with', type=int)

    if request.method == 'POST':
        receiver_id = request.form.get('receiver_id', type=int)
        body = request.form.get('message', '').strip()
        if receiver_id and body:
            result = send_message(user_id, receiver_id, body)
            if result['success']:
                flash('Message sent', 'success')
            else:
                flash('Failed to send message', 'error')
        return redirect(url_for('messages_page', **{'with': receiver_id} if receiver_id else {}))

    conversation = []
    active_contact = None
    if other_id:
        active_contact = get_user_by_id(other_id)
        if active_contact:
            conversation = get_messages_between(user_id, other_id)
            mark_messages_read(user_id, other_id)

    return render_template(
        'messages.html',
        contacts=contacts,
        conversation=conversation,
        active_contact=active_contact,
        other_id=other_id
    )

@app.route('/reviews')
@login_required
def reviews_page():
    """Reviews list (written by client or received by worker)"""
    user_id = get_current_user_id()
    user_type = get_user_type()
    pending = []
    reviews = []
    if user_type == 'worker':
        worker = get_worker_by_user_id(user_id)
        if worker:
            reviews = get_worker_reviews(worker['id'], limit=50)
    else:
        pending = get_pending_reviews(user_id)
        reviews = get_reviews_by_user(user_id, limit=50)
    return render_template(
        'reviews_list.html',
        reviews=reviews,
        pending_reviews=pending,
        user_type=user_type
    )

@app.route('/favorites', methods=['GET', 'POST'])
@login_required
@user_type_required('user')
def favorites_page():
    """Saved favorite workers"""
    user_id = get_current_user_id()
    if request.method == 'POST':
        action = request.form.get('action')
        worker_id = request.form.get('worker_id', type=int)
        if worker_id:
            if action == 'remove':
                remove_favorite(user_id, worker_id)
                flash('Removed from favorites', 'success')
            elif action == 'add':
                add_favorite(user_id, worker_id)
                flash('Added to favorites', 'success')
        return redirect(url_for('favorites_page'))
    favorites = get_user_favorites(user_id)
    return render_template('favorites.html', favorites=favorites)

@app.route('/profile')
@login_required
def profile_page():
    """View profile"""
    user_id = get_current_user_id()
    user = get_user_by_id(user_id)
    worker = get_worker_by_user_id(user_id) if get_user_type() == 'worker' else None
    stats = None
    if get_user_type() == 'worker' and worker:
        stats = get_worker_stats(worker['id'])
    elif get_user_type() == 'user':
        stats = get_user_stats(user_id)
    return render_template('profile.html', user=user, worker=worker, stats=stats)

@app.route('/settings', methods=['GET', 'POST'])
@login_required
def settings_page():
    """Account settings"""
    user_id = get_current_user_id()
    user_type = get_user_type()
    user = get_user_by_id(user_id)
    worker = get_worker_by_user_id(user_id) if user_type == 'worker' else None

    if request.method == 'POST':
        form_type = request.form.get('form_type', 'profile')
        if form_type == 'profile':
            name = request.form.get('name', '').strip()
            phone = request.form.get('phone', '').strip()
            if not name or not phone:
                flash('Name and phone are required', 'error')
            elif update_user_profile(user_id, name, phone):
                session['user_name'] = name
                flash('Profile updated', 'success')
            else:
                flash('Could not update profile', 'error')
            if user_type == 'worker':
                service_area = request.form.get('service_area', '').strip()
                skills = request.form.get('skills', '').strip()
                experience = request.form.get('experience', 0)
                bio = request.form.get('bio', '').strip()
                if service_area and skills:
                    try:
                        update_worker_profile(user_id, service_area, skills, experience, bio or None)
                    except (ValueError, TypeError):
                        flash('Invalid experience value', 'error')
        elif form_type == 'password':
            current = request.form.get('current_password', '')
            new_pass = request.form.get('new_password', '')
            confirm = request.form.get('confirm_password', '')
            stored = user['password']
            if stored.startswith('$2y$'):
                stored = '$2b$' + stored[4:]
            if not bcrypt.checkpw(current.encode(), stored.encode()):
                flash('Current password is incorrect', 'error')
            elif len(new_pass) < 6:
                flash('New password must be at least 6 characters', 'error')
            elif new_pass != confirm:
                flash('Passwords do not match', 'error')
            else:
                new_hash = bcrypt.hashpw(new_pass.encode(), bcrypt.gensalt()).decode()
                from db_connection import get_db_connection, get_db_cursor
                conn = get_db_connection()
                try:
                    cur = get_db_cursor(conn)
                    cur.execute("UPDATE users SET password = %s WHERE id = %s", (new_hash, user_id))
                    conn.commit()
                    flash('Password updated', 'success')
                except Exception:
                    conn.rollback()
                    flash('Could not update password', 'error')
                finally:
                    cur.close()
                    conn.close()
        return redirect(url_for('settings_page'))

    return render_template('settings.html', user=user, worker=worker, user_type=user_type)

# ==================== ESCROW & WALLET ====================

@app.route('/wallet', methods=['GET', 'POST'])
@login_required
def wallet_page():
    """User wallet — balance, deposits (demo), transaction history"""
    user_id = get_current_user_id()
    ensure_wallet(user_id)

    if request.method == 'POST':
        try:
            amount = float(request.form.get('amount', 0))
        except (ValueError, TypeError):
            amount = 0
        result = deposit_demo_funds(user_id, amount)
        if result['success']:
            flash(f'${amount:.2f} added to your wallet (demo deposit)', 'success')
        else:
            flash(result.get('message', 'Deposit failed'), 'error')
        return redirect(url_for('wallet_page'))

    wallet = get_wallet(user_id)
    transactions = get_wallet_transactions(user_id)
    vault = get_escrow_vault_summary()
    return render_template(
        'wallet.html',
        wallet=wallet,
        transactions=transactions,
        vault=vault,
        platform_fee_percent=ESCROW_PLATFORM_FEE_PERCENT,
    )

@app.route('/booking/<int:booking_id>/escrow', methods=['GET', 'POST'])
@login_required
@user_type_required('user')
def escrow_pay(booking_id):
    """Fund escrow for a booking from wallet balance"""
    user_id = get_current_user_id()
    ensure_wallet(user_id)
    booking = get_booking(booking_id)

    if not booking or booking['user_id'] != user_id:
        flash('Booking not found', 'error')
        return redirect(url_for('my_bookings'))

    escrow = get_escrow_for_booking(booking_id)
    wallet = get_wallet(user_id)

    if request.method == 'POST':
        result = fund_escrow(user_id, booking_id)
        if result['success']:
            flash(f'${result["amount"]:.2f} secured in escrow. Funds are held until the job is completed.', 'success')
            worker = get_worker(booking['worker_id'])
            if worker:
                create_notification(
                    worker['user_id'], 'Payment in escrow',
                    f'Client placed ${result["amount"]:.2f} in escrow for "{booking["title"]}".',
                    'system', '/bookings',
                )
            return redirect(url_for('my_bookings'))
        flash(result.get('message', 'Escrow payment failed'), 'error')

    return render_template(
        'escrow_pay.html',
        booking=booking,
        wallet=wallet,
        escrow=escrow,
        platform_fee_percent=ESCROW_PLATFORM_FEE_PERCENT,
    )

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
