"""
Database functions for ProTech
Converted from PHP db_functions.php
"""

from datetime import datetime, date
from db_connection import get_db_cursor, get_db_connection

# ==================== WORKER FUNCTIONS ====================

def get_workers(filters=None):
    """Get all available workers with optional filters"""
    if filters is None:
        filters = {}
    
    conn = get_db_connection()
    try:
        cur = get_db_cursor(conn)
        
        sql = """SELECT w.*, u.name, u.email, u.phone, u.avatar 
                 FROM workers w 
                 JOIN users u ON w.user_id = u.id 
                 WHERE 1=1"""
        params = []
        
        if filters.get('skill'):
            sql += " AND w.skills ILIKE %s"
            params.append(f"%{filters['skill']}%")
        
        if filters.get('service_area'):
            sql += " AND w.service_area ILIKE %s"
            params.append(f"%{filters['service_area']}%")
        
        if filters.get('min_rating'):
            sql += " AND w.rating >= %s"
            params.append(filters['min_rating'])
        
        if 'is_available' in filters:
            sql += " AND w.is_available = %s"
            params.append(filters['is_available'])
        
        sql += " ORDER BY w.rating DESC, w.total_jobs DESC"
        
        if filters.get('limit'):
            sql += " LIMIT %s"
            params.append(filters['limit'])
        
        cur.execute(sql, params)
        return [dict(row) for row in cur.fetchall()]
    finally:
        cur.close()
        conn.close()

def get_worker(worker_id):
    """Get single worker by ID"""
    conn = get_db_connection()
    try:
        cur = get_db_cursor(conn)
        cur.execute(
            """SELECT w.*, u.name, u.email, u.phone, u.avatar 
               FROM workers w 
               JOIN users u ON w.user_id = u.id 
               WHERE w.id = %s""",
            (worker_id,)
        )
        row = cur.fetchone()
        return dict(row) if row else None
    finally:
        cur.close()
        conn.close()

def get_worker_by_user_id(user_id):
    """Get worker by user_id"""
    conn = get_db_connection()
    try:
        cur = get_db_cursor(conn)
        cur.execute(
            """SELECT w.*, u.name, u.email, u.phone, u.avatar 
               FROM workers w 
               JOIN users u ON w.user_id = u.id 
               WHERE w.user_id = %s""",
            (user_id,)
        )
        row = cur.fetchone()
        return dict(row) if row else None
    finally:
        cur.close()
        conn.close()

# ==================== BOOKING FUNCTIONS ====================

def create_booking(user_id, worker_id, data):
    """Create a new booking"""
    conn = get_db_connection()
    try:
        cur = get_db_cursor(conn)
        
        cur.execute(
            """INSERT INTO bookings (user_id, worker_id, service_category_id, title, description, 
               scheduled_date, scheduled_time, estimated_duration, address, price) 
               VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s) RETURNING id""",
            (
                user_id, worker_id, data.get('service_category_id'), data['title'],
                data['description'], data['scheduled_date'], data['scheduled_time'],
                data.get('estimated_duration', 60), data['address'], data['price']
            )
        )
        booking_id = cur.fetchone()['id']
        conn.commit()
        
        # Create notification for worker
        worker = get_worker(worker_id)
        if worker:
            create_notification(
                worker['user_id'], 'New Job Request',
                f"You have a new booking request: {data['title']}",
                'booking', f"/booking?id={booking_id}"
            )
        
        return {'success': True, 'booking_id': booking_id}
    except Exception as e:
        conn.rollback()
        return {'success': False, 'message': f'Failed to create booking: {str(e)}'}
    finally:
        cur.close()
        conn.close()

def get_user_bookings(user_id, status=None, limit=None):
    """Get bookings for a user (client)"""
    conn = get_db_connection()
    try:
        cur = get_db_cursor(conn)
        
        sql = """SELECT b.*, w.id as worker_id, u.name as worker_name, u.avatar as worker_avatar,
                 sc.name as service_name
                 FROM bookings b 
                 JOIN workers w ON b.worker_id = w.id 
                 JOIN users u ON w.user_id = u.id
                 LEFT JOIN service_categories sc ON b.service_category_id = sc.id
                 WHERE b.user_id = %s"""
        params = [user_id]
        
        if status:
            sql += " AND b.status = %s"
            params.append(status)
        
        sql += " ORDER BY b.scheduled_date DESC, b.scheduled_time DESC"
        
        if limit:
            sql += " LIMIT %s"
            params.append(limit)
        
        cur.execute(sql, params)
        return [dict(row) for row in cur.fetchall()]
    finally:
        cur.close()
        conn.close()

def get_worker_bookings(worker_id, status=None, limit=None):
    """Get bookings for a worker"""
    conn = get_db_connection()
    try:
        cur = get_db_cursor(conn)
        
        sql = """SELECT b.*, u.name as client_name, u.phone as client_phone, u.avatar as client_avatar,
                 sc.name as service_name
                 FROM bookings b 
                 JOIN users u ON b.user_id = u.id
                 LEFT JOIN service_categories sc ON b.service_category_id = sc.id
                 WHERE b.worker_id = %s"""
        params = [worker_id]
        
        if status:
            if isinstance(status, list):
                placeholders = ','.join(['%s'] * len(status))
                sql += f" AND b.status IN ({placeholders})"
                params.extend(status)
            else:
                sql += " AND b.status = %s"
                params.append(status)
        
        sql += " ORDER BY b.scheduled_date ASC, b.scheduled_time ASC"
        
        if limit:
            sql += " LIMIT %s"
            params.append(limit)
        
        cur.execute(sql, params)
        return [dict(row) for row in cur.fetchall()]
    finally:
        cur.close()
        conn.close()

def get_worker_today_schedule(worker_id):
    """Get today's schedule for a worker"""
    conn = get_db_connection()
    try:
        cur = get_db_cursor(conn)
        today = date.today()
        cur.execute(
            """SELECT b.*, u.name as client_name, u.phone as client_phone
               FROM bookings b 
               JOIN users u ON b.user_id = u.id
               WHERE b.worker_id = %s AND b.scheduled_date = %s 
               AND b.status IN ('confirmed', 'in_progress')
               ORDER BY b.scheduled_time ASC""",
            (worker_id, today)
        )
        return [dict(row) for row in cur.fetchall()]
    finally:
        cur.close()
        conn.close()

def update_booking_status(booking_id, status, user_id=None):
    """Update booking status"""
    conn = get_db_connection()
    try:
        cur = get_db_cursor(conn)
        
        cur.execute(
            "UPDATE bookings SET status = %s, updated_at = CURRENT_TIMESTAMP WHERE id = %s",
            (status, booking_id)
        )
        conn.commit()
        
        # Get booking details for notification
        booking = get_booking(booking_id)
        
        if booking:
            # Create notifications
            if status == 'confirmed':
                create_notification(
                    booking['user_id'], 'Booking Confirmed',
                    f"Your booking '{booking['title']}' has been confirmed!",
                    'booking', f"/booking?id={booking_id}"
                )
            elif status == 'completed':
                create_notification(
                    booking['user_id'], 'Service Completed',
                    f"Your booking '{booking['title']}' has been completed. Please leave a review!",
                    'booking', f"/review?booking_id={booking_id}"
                )
            elif status == 'cancelled':
                worker = get_worker(booking['worker_id'])
                create_notification(booking['user_id'], 'Booking Cancelled',
                    f"Your booking '{booking['title']}' has been cancelled.", 'booking')
                if worker:
                    create_notification(worker['user_id'], 'Booking Cancelled',
                        f"A booking '{booking['title']}' has been cancelled.", 'booking')
        
        return {'success': True}
    except Exception as e:
        conn.rollback()
        return {'success': False, 'message': f'Failed to update booking: {str(e)}'}
    finally:
        cur.close()
        conn.close()

def get_booking(booking_id):
    """Get single booking"""
    conn = get_db_connection()
    try:
        cur = get_db_cursor(conn)
        cur.execute(
            """SELECT b.*, 
               u.name as client_name, u.phone as client_phone, u.email as client_email,
               wu.name as worker_name, wu.phone as worker_phone,
               w.skills, w.service_area,
               sc.name as service_name
               FROM bookings b 
               JOIN users u ON b.user_id = u.id
               JOIN workers w ON b.worker_id = w.id
               JOIN users wu ON w.user_id = wu.id
               LEFT JOIN service_categories sc ON b.service_category_id = sc.id
               WHERE b.id = %s""",
            (booking_id,)
        )
        row = cur.fetchone()
        return dict(row) if row else None
    finally:
        cur.close()
        conn.close()

# ==================== STATISTICS FUNCTIONS ====================

def get_user_stats(user_id):
    """Get user statistics"""
    conn = get_db_connection()
    stats = {}
    try:
        cur = get_db_cursor(conn)
        
        # Active bookings
        cur.execute(
            """SELECT COUNT(*) as count FROM bookings 
               WHERE user_id = %s AND status IN ('pending', 'confirmed', 'in_progress')""",
            (user_id,)
        )
        stats['active_bookings'] = cur.fetchone()['count']
        
        # Completed services
        cur.execute(
            "SELECT COUNT(*) as count FROM bookings WHERE user_id = %s AND status = 'completed'",
            (user_id,)
        )
        stats['completed_services'] = cur.fetchone()['count']
        
        # Total spent
        cur.execute(
            """SELECT COALESCE(SUM(price), 0) as total FROM bookings 
               WHERE user_id = %s AND status = 'completed' AND payment_status = 'paid'""",
            (user_id,)
        )
        stats['total_spent'] = float(cur.fetchone()['total'] or 0)
        
        # Reviews given
        cur.execute("SELECT COUNT(*) as count FROM reviews WHERE user_id = %s", (user_id,))
        stats['reviews_given'] = cur.fetchone()['count']
        
        return stats
    finally:
        cur.close()
        conn.close()

def get_worker_stats(worker_id):
    """Get worker statistics"""
    conn = get_db_connection()
    stats = {}
    try:
        cur = get_db_cursor(conn)
        
        # This month's earnings
        first_day = date.today().replace(day=1)
        cur.execute(
            """SELECT COALESCE(SUM(price), 0) as total FROM bookings 
               WHERE worker_id = %s AND status = 'completed' AND scheduled_date >= %s""",
            (worker_id, first_day)
        )
        stats['monthly_earnings'] = float(cur.fetchone()['total'] or 0)
        
        # Pending requests
        cur.execute(
            "SELECT COUNT(*) as count FROM bookings WHERE worker_id = %s AND status = 'pending'",
            (worker_id,)
        )
        stats['pending_requests'] = cur.fetchone()['count']
        
        # Scheduled jobs
        cur.execute(
            """SELECT COUNT(*) as count FROM bookings 
               WHERE worker_id = %s AND status IN ('confirmed', 'in_progress')""",
            (worker_id,)
        )
        stats['scheduled_jobs'] = cur.fetchone()['count']
        
        # Get worker rating info
        worker = get_worker(worker_id)
        if worker:
            stats['rating'] = float(worker.get('rating', 0) or 0)
            stats['total_reviews'] = worker.get('total_reviews', 0) or 0
            stats['total_jobs'] = worker.get('total_jobs', 0) or 0
        else:
            stats['rating'] = 0
            stats['total_reviews'] = 0
            stats['total_jobs'] = 0
        
        return stats
    finally:
        cur.close()
        conn.close()

# ==================== REVIEW FUNCTIONS ====================

def create_review(booking_id, user_id, worker_id, rating, comment):
    """Create a review"""
    conn = get_db_connection()
    try:
        cur = get_db_cursor(conn)
        
        # Check if review already exists
        cur.execute("SELECT id FROM reviews WHERE booking_id = %s", (booking_id,))
        if cur.fetchone():
            return {'success': False, 'message': 'Review already exists for this booking'}
        
        cur.execute(
            """INSERT INTO reviews (booking_id, user_id, worker_id, rating, comment) 
               VALUES (%s, %s, %s, %s, %s)""",
            (booking_id, user_id, worker_id, rating, comment)
        )
        conn.commit()
        
        # Notify worker about the review
        worker = get_worker(worker_id)
        if worker:
            create_notification(
                worker['user_id'], 'New Review',
                f"You received a new {rating}-star review!", 'review'
            )
        
        return {'success': True}
    except Exception as e:
        conn.rollback()
        return {'success': False, 'message': f'Failed to create review: {str(e)}'}
    finally:
        cur.close()
        conn.close()

def get_worker_reviews(worker_id, limit=10):
    """Get reviews for a worker"""
    conn = get_db_connection()
    try:
        cur = get_db_cursor(conn)
        cur.execute(
            """SELECT r.*, u.name as reviewer_name, u.avatar as reviewer_avatar, b.title as booking_title
               FROM reviews r
               JOIN users u ON r.user_id = u.id
               JOIN bookings b ON r.booking_id = b.id
               WHERE r.worker_id = %s
               ORDER BY r.created_at DESC
               LIMIT %s""",
            (worker_id, limit)
        )
        return [dict(row) for row in cur.fetchall()]
    finally:
        cur.close()
        conn.close()

def get_pending_reviews(user_id):
    """Get pending reviews for a user (completed bookings without reviews)"""
    conn = get_db_connection()
    try:
        cur = get_db_cursor(conn)
        cur.execute(
            """SELECT b.*, wu.name as worker_name
               FROM bookings b
               JOIN workers w ON b.worker_id = w.id
               JOIN users wu ON w.user_id = wu.id
               LEFT JOIN reviews r ON b.id = r.booking_id
               WHERE b.user_id = %s AND b.status = 'completed' AND r.id IS NULL
               ORDER BY b.scheduled_date DESC""",
            (user_id,)
        )
        return [dict(row) for row in cur.fetchall()]
    finally:
        cur.close()
        conn.close()

# ==================== NOTIFICATION FUNCTIONS ====================

def create_notification(user_id, title, message, type='system', link=None):
    """Create notification"""
    conn = get_db_connection()
    try:
        cur = get_db_cursor(conn)
        cur.execute(
            "INSERT INTO notifications (user_id, title, message, type, link) VALUES (%s, %s, %s, %s, %s)",
            (user_id, title, message, type, link)
        )
        conn.commit()
        return True
    except Exception:
        conn.rollback()
        return False
    finally:
        cur.close()
        conn.close()

def get_notifications(user_id, unread_only=False, limit=20):
    """Get user notifications"""
    conn = get_db_connection()
    try:
        cur = get_db_cursor(conn)
        sql = "SELECT * FROM notifications WHERE user_id = %s"
        params = [user_id]
        
        if unread_only:
            sql += " AND is_read = FALSE"
        sql += " ORDER BY created_at DESC LIMIT %s"
        params.append(limit)
        
        cur.execute(sql, params)
        return [dict(row) for row in cur.fetchall()]
    finally:
        cur.close()
        conn.close()

def count_unread_notifications(user_id):
    """Count unread notifications"""
    conn = get_db_connection()
    try:
        cur = get_db_cursor(conn)
        cur.execute(
            "SELECT COUNT(*) as count FROM notifications WHERE user_id = %s AND is_read = FALSE",
            (user_id,)
        )
        return cur.fetchone()['count']
    finally:
        cur.close()
        conn.close()

def mark_notification_read(notification_id):
    """Mark notification as read"""
    conn = get_db_connection()
    try:
        cur = get_db_cursor(conn)
        cur.execute("UPDATE notifications SET is_read = TRUE WHERE id = %s", (notification_id,))
        conn.commit()
        return True
    except Exception:
        conn.rollback()
        return False
    finally:
        cur.close()
        conn.close()

# ==================== SERVICE CATEGORIES ====================

def get_service_categories():
    """Get all service categories"""
    conn = get_db_connection()
    try:
        cur = get_db_cursor(conn)
        cur.execute("SELECT * FROM service_categories ORDER BY name")
        return [dict(row) for row in cur.fetchall()]
    finally:
        cur.close()
        conn.close()

# ==================== FAVORITES ====================

def add_favorite(user_id, worker_id):
    """Add favorite worker"""
    conn = get_db_connection()
    try:
        cur = get_db_cursor(conn)
        cur.execute(
            "INSERT INTO favorites (user_id, worker_id) VALUES (%s, %s) ON CONFLICT DO NOTHING",
            (user_id, worker_id)
        )
        conn.commit()
        return True
    except Exception:
        conn.rollback()
        return False
    finally:
        cur.close()
        conn.close()

def remove_favorite(user_id, worker_id):
    """Remove favorite worker"""
    conn = get_db_connection()
    try:
        cur = get_db_cursor(conn)
        cur.execute(
            "DELETE FROM favorites WHERE user_id = %s AND worker_id = %s",
            (user_id, worker_id)
        )
        conn.commit()
        return True
    except Exception:
        conn.rollback()
        return False
    finally:
        cur.close()
        conn.close()

def get_user_favorites(user_id):
    """Get user favorites"""
    conn = get_db_connection()
    try:
        cur = get_db_cursor(conn)
        cur.execute(
            """SELECT w.*, u.name, u.avatar 
               FROM favorites f
               JOIN workers w ON f.worker_id = w.id
               JOIN users u ON w.user_id = u.id
               WHERE f.user_id = %s
               ORDER BY f.created_at DESC""",
            (user_id,)
        )
        return [dict(row) for row in cur.fetchall()]
    finally:
        cur.close()
        conn.close()

def is_favorite(user_id, worker_id):
    """Check if worker is favorite"""
    conn = get_db_connection()
    try:
        cur = get_db_cursor(conn)
        cur.execute(
            "SELECT id FROM favorites WHERE user_id = %s AND worker_id = %s",
            (user_id, worker_id)
        )
        return cur.fetchone() is not None
    finally:
        cur.close()
        conn.close()

# ==================== USER PROFILE ====================

def get_user_by_id(user_id):
    """Get user record by id"""
    conn = get_db_connection()
    try:
        cur = get_db_cursor(conn)
        cur.execute("SELECT * FROM users WHERE id = %s", (user_id,))
        row = cur.fetchone()
        return dict(row) if row else None
    finally:
        cur.close()
        conn.close()

def update_user_profile(user_id, name, phone):
    """Update client/worker account fields"""
    conn = get_db_connection()
    try:
        cur = get_db_cursor(conn)
        cur.execute(
            "UPDATE users SET name = %s, phone = %s, updated_at = CURRENT_TIMESTAMP WHERE id = %s",
            (name, phone, user_id)
        )
        conn.commit()
        return True
    except Exception:
        conn.rollback()
        return False
    finally:
        cur.close()
        conn.close()

def update_worker_profile(user_id, service_area, skills, experience, bio=None):
    """Update worker-specific fields"""
    conn = get_db_connection()
    try:
        cur = get_db_cursor(conn)
        cur.execute(
            """UPDATE workers SET service_area = %s, skills = %s, experience = %s, bio = %s,
               updated_at = CURRENT_TIMESTAMP WHERE user_id = %s""",
            (service_area, skills, int(experience), bio, user_id)
        )
        conn.commit()
        return cur.rowcount > 0
    except Exception:
        conn.rollback()
        return False
    finally:
        cur.close()
        conn.close()

def get_reviews_by_user(user_id, limit=50):
    """Reviews written by a client"""
    conn = get_db_connection()
    try:
        cur = get_db_cursor(conn)
        cur.execute(
            """SELECT r.*, wu.name as worker_name, b.title as booking_title
               FROM reviews r
               JOIN workers w ON r.worker_id = w.id
               JOIN users wu ON w.user_id = wu.id
               JOIN bookings b ON r.booking_id = b.id
               WHERE r.user_id = %s
               ORDER BY r.created_at DESC
               LIMIT %s""",
            (user_id, limit)
        )
        return [dict(row) for row in cur.fetchall()]
    finally:
        cur.close()
        conn.close()

# ==================== MESSAGES ====================

def get_message_contacts(user_id, user_type):
    """People the user can message (from bookings and past chats)"""
    conn = get_db_connection()
    try:
        cur = get_db_cursor(conn)
        if user_type == 'worker':
            worker = get_worker_by_user_id(user_id)
            if not worker:
                return []
            cur.execute(
                """SELECT DISTINCT u.id, u.name, u.user_type
                   FROM users u
                   WHERE u.id != %s AND (
                       u.id IN (SELECT b.user_id FROM bookings b WHERE b.worker_id = %s)
                       OR u.id IN (SELECT sender_id FROM messages WHERE receiver_id = %s)
                       OR u.id IN (SELECT receiver_id FROM messages WHERE sender_id = %s)
                   )
                   ORDER BY u.name""",
                (user_id, worker['id'], user_id, user_id)
            )
        else:
            cur.execute(
                """SELECT DISTINCT u.id, u.name, u.user_type
                   FROM users u
                   WHERE u.id != %s AND (
                       u.id IN (
                           SELECT w.user_id FROM bookings b
                           JOIN workers w ON b.worker_id = w.id
                           WHERE b.user_id = %s
                       )
                       OR u.id IN (SELECT sender_id FROM messages WHERE receiver_id = %s)
                       OR u.id IN (SELECT receiver_id FROM messages WHERE sender_id = %s)
                   )
                   ORDER BY u.name""",
                (user_id, user_id, user_id, user_id)
            )
        return [dict(row) for row in cur.fetchall()]
    finally:
        cur.close()
        conn.close()

def get_messages_between(user_id, other_id, limit=100):
    """Conversation between two users"""
    conn = get_db_connection()
    try:
        cur = get_db_cursor(conn)
        cur.execute(
            """SELECT m.*, s.name as sender_name
               FROM messages m
               JOIN users s ON m.sender_id = s.id
               WHERE (m.sender_id = %s AND m.receiver_id = %s)
                  OR (m.sender_id = %s AND m.receiver_id = %s)
               ORDER BY m.created_at ASC
               LIMIT %s""",
            (user_id, other_id, other_id, user_id, limit)
        )
        return [dict(row) for row in cur.fetchall()]
    finally:
        cur.close()
        conn.close()

def send_message(sender_id, receiver_id, body, booking_id=None):
    """Send a chat message"""
    conn = get_db_connection()
    try:
        cur = get_db_cursor(conn)
        cur.execute(
            """INSERT INTO messages (sender_id, receiver_id, booking_id, message)
               VALUES (%s, %s, %s, %s) RETURNING id""",
            (sender_id, receiver_id, booking_id, body)
        )
        msg_id = cur.fetchone()['id']
        conn.commit()
        create_notification(
            receiver_id, 'New message',
            'You have a new message.',
            'message', '/messages?with=' + str(sender_id)
        )
        return {'success': True, 'message_id': msg_id}
    except Exception as e:
        conn.rollback()
        return {'success': False, 'message': str(e)}
    finally:
        cur.close()
        conn.close()

def mark_messages_read(user_id, other_id):
    """Mark incoming messages from other user as read"""
    conn = get_db_connection()
    try:
        cur = get_db_cursor(conn)
        cur.execute(
            "UPDATE messages SET is_read = TRUE WHERE receiver_id = %s AND sender_id = %s AND is_read = FALSE",
            (user_id, other_id)
        )
        conn.commit()
    finally:
        cur.close()
        conn.close()

def count_unread_messages(user_id):
    """Count unread messages for user"""
    conn = get_db_connection()
    try:
        cur = get_db_cursor(conn)
        cur.execute(
            "SELECT COUNT(*) as count FROM messages WHERE receiver_id = %s AND is_read = FALSE",
            (user_id,)
        )
        return cur.fetchone()['count']
    finally:
        cur.close()
        conn.close()

def mark_all_notifications_read(user_id):
    """Mark all notifications read for user"""
    conn = get_db_connection()
    try:
        cur = get_db_cursor(conn)
        cur.execute(
            "UPDATE notifications SET is_read = TRUE WHERE user_id = %s AND is_read = FALSE",
            (user_id,)
        )
        conn.commit()
    finally:
        cur.close()
        conn.close()

# ==================== HELPER FUNCTIONS ====================

def get_initials(name):
    """Get user initials from name"""
    words = str(name).strip().split()
    initials = ''.join([word[0].upper() for word in words if word])
    return initials[:2]

def format_date(date_val):
    """Format date"""
    if isinstance(date_val, str):
        date_val = datetime.strptime(date_val, '%Y-%m-%d').date()
    return date_val.strftime('%b %d, %Y')

def format_time(time_val):
    """Format time"""
    if isinstance(time_val, str):
        try:
            time_val = datetime.strptime(time_val, '%H:%M:%S').time()
        except:
            time_val = datetime.strptime(time_val, '%H:%M').time()
    return time_val.strftime('%I:%M %p')

def format_price(price):
    """Format price"""
    return f"${float(price):,.2f}"

def time_ago(datetime_val):
    """Get time ago string"""
    if isinstance(datetime_val, str):
        datetime_val = datetime.fromisoformat(datetime_val.replace('Z', '+00:00'))
    
    now = datetime.now()
    diff = now - datetime_val
    
    if diff.days >= 365:
        years = diff.days // 365
        return f"{years} year{'s' if years > 1 else ''} ago"
    elif diff.days >= 30:
        months = diff.days // 30
        return f"{months} month{'s' if months > 1 else ''} ago"
    elif diff.days > 0:
        return f"{diff.days} day{'s' if diff.days > 1 else ''} ago"
    elif diff.seconds >= 3600:
        hours = diff.seconds // 3600
        return f"{hours} hour{'s' if hours > 1 else ''} ago"
    elif diff.seconds >= 60:
        minutes = diff.seconds // 60
        return f"{minutes} minute{'s' if minutes > 1 else ''} ago"
    else:
        return 'Just now'
