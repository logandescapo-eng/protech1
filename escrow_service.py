"""
Escrow payment service — holds client funds securely until job completion.

This is a platform ledger (simulated bank). For real card/bank payments,
integrate Stripe (Payment Intents + Connect) and map webhooks to these functions.
"""

from decimal import Decimal, ROUND_HALF_UP
from config import ESCROW_PLATFORM_FEE_PERCENT, ESCROW_DEMO_DEPOSIT_MAX
from db_connection import get_db_connection
from psycopg2 import extras

PLATFORM_FEE_RATE = Decimal(str(ESCROW_PLATFORM_FEE_PERCENT)) / Decimal('100')


def _money(value):
    return Decimal(str(value)).quantize(Decimal('0.01'), rounding=ROUND_HALF_UP)


def ensure_wallet(user_id, cur=None):
    """Create wallet row if missing."""
    own_conn = cur is None
    conn = get_db_connection() if own_conn else cur.connection
    try:
        if own_conn:
            cur = conn.cursor(cursor_factory=extras.RealDictCursor)
        cur.execute(
            """INSERT INTO user_wallets (user_id, available_balance)
               VALUES (%s, 0) ON CONFLICT (user_id) DO NOTHING""",
            (user_id,),
        )
        if own_conn:
            conn.commit()
    finally:
        if own_conn:
            cur.close()
            conn.close()


def get_wallet(user_id):
    ensure_wallet(user_id)
    conn = get_db_connection()
    try:
        cur = conn.cursor(cursor_factory=extras.RealDictCursor)
        cur.execute(
            "SELECT user_id, available_balance, updated_at FROM user_wallets WHERE user_id = %s",
            (user_id,),
        )
        row = cur.fetchone()
        return dict(row) if row else {'user_id': user_id, 'available_balance': Decimal('0')}
    finally:
        cur.close()
        conn.close()


def get_escrow_vault_summary():
    conn = get_db_connection()
    try:
        cur = conn.cursor(cursor_factory=extras.RealDictCursor)
        cur.execute("SELECT total_held, total_released, updated_at FROM escrow_vault WHERE id = 1")
        row = cur.fetchone()
        return dict(row) if row else {'total_held': 0, 'total_released': 0}
    finally:
        cur.close()
        conn.close()


def get_wallet_transactions(user_id, limit=30):
    conn = get_db_connection()
    try:
        cur = conn.cursor(cursor_factory=extras.RealDictCursor)
        cur.execute(
            """SELECT wt.*, b.title as booking_title
               FROM wallet_transactions wt
               LEFT JOIN bookings b ON wt.booking_id = b.id
               WHERE wt.user_id = %s
               ORDER BY wt.created_at DESC
               LIMIT %s""",
            (user_id, limit),
        )
        return [dict(r) for r in cur.fetchall()]
    finally:
        cur.close()
        conn.close()


def get_escrow_for_booking(booking_id):
    conn = get_db_connection()
    try:
        cur = conn.cursor(cursor_factory=extras.RealDictCursor)
        cur.execute("SELECT * FROM escrow_holds WHERE booking_id = %s", (booking_id,))
        row = cur.fetchone()
        return dict(row) if row else None
    finally:
        cur.close()
        conn.close()


def _ledger(cur, user_id, tx_type, amount, balance_after, booking_id=None, escrow_id=None, description=None):
    cur.execute(
        """INSERT INTO wallet_transactions
           (user_id, booking_id, escrow_id, transaction_type, amount, balance_after, description)
           VALUES (%s, %s, %s, %s, %s, %s, %s)""",
        (user_id, booking_id, escrow_id, tx_type, amount, balance_after, description),
    )


def deposit_demo_funds(user_id, amount):
    """Simulated bank deposit (demo / testing)."""
    amount = _money(amount)
    if amount <= 0:
        return {'success': False, 'message': 'Amount must be positive'}
    if amount > _money(ESCROW_DEMO_DEPOSIT_MAX):
        return {'success': False, 'message': f'Max deposit ${ESCROW_DEMO_DEPOSIT_MAX} per transaction'}

    conn = get_db_connection()
    try:
        cur = conn.cursor(cursor_factory=extras.RealDictCursor)
        ensure_wallet(user_id, cur)
        cur.execute(
            "SELECT available_balance FROM user_wallets WHERE user_id = %s FOR UPDATE",
            (user_id,),
        )
        row = cur.fetchone()
        new_bal = _money(row['available_balance']) + amount
        cur.execute(
            "UPDATE user_wallets SET available_balance = %s, updated_at = CURRENT_TIMESTAMP WHERE user_id = %s",
            (new_bal, user_id),
        )
        _ledger(cur, user_id, 'deposit', amount, new_bal, description='Demo bank deposit')
        conn.commit()
        return {'success': True, 'balance': float(new_bal)}
    except Exception as e:
        conn.rollback()
        return {'success': False, 'message': str(e)}
    finally:
        cur.close()
        conn.close()


def fund_escrow(client_id, booking_id):
    """Move funds from client wallet into platform escrow for a booking."""
    conn = get_db_connection()
    try:
        cur = conn.cursor(cursor_factory=extras.RealDictCursor)
        cur.execute(
            """SELECT b.*, w.user_id as worker_user_id
               FROM bookings b
               JOIN workers w ON b.worker_id = w.id
               WHERE b.id = %s FOR UPDATE""",
            (booking_id,),
        )
        booking = cur.fetchone()
        if not booking:
            return {'success': False, 'message': 'Booking not found'}
        if booking['user_id'] != client_id:
            return {'success': False, 'message': 'Unauthorized'}
        if booking['payment_status'] not in ('pending',):
            return {'success': False, 'message': 'Payment already processed for this booking'}

        amount = _money(booking['price'])
        if amount <= 0:
            return {'success': False, 'message': 'Invalid booking amount'}

        ensure_wallet(client_id, cur)
        ensure_wallet(booking['worker_user_id'], cur)

        cur.execute(
            "SELECT available_balance FROM user_wallets WHERE user_id = %s FOR UPDATE",
            (client_id,),
        )
        wallet = cur.fetchone()
        balance = _money(wallet['available_balance'])
        if balance < amount:
            return {
                'success': False,
                'message': f'Insufficient wallet balance. Need ${amount}, you have ${balance}.',
            }

        new_client_bal = balance - amount
        cur.execute(
            "UPDATE user_wallets SET available_balance = %s, updated_at = CURRENT_TIMESTAMP WHERE user_id = %s",
            (new_client_bal, client_id),
        )

        fee = (amount * PLATFORM_FEE_RATE).quantize(Decimal('0.01'), rounding=ROUND_HALF_UP)
        worker_payout = amount - fee

        cur.execute(
            """INSERT INTO escrow_holds
               (booking_id, client_id, worker_user_id, amount, platform_fee, worker_payout, status)
               VALUES (%s, %s, %s, %s, %s, %s, 'held') RETURNING id""",
            (booking_id, client_id, booking['worker_user_id'], amount, fee, worker_payout),
        )
        escrow_id = cur.fetchone()['id']

        cur.execute(
            "UPDATE escrow_vault SET total_held = total_held + %s, updated_at = CURRENT_TIMESTAMP WHERE id = 1",
            (amount,),
        )
        cur.execute(
            "UPDATE bookings SET payment_status = 'escrow_held', updated_at = CURRENT_TIMESTAMP WHERE id = %s",
            (booking_id,),
        )

        _ledger(
            cur, client_id, 'escrow_hold', -amount, new_client_bal,
            booking_id=booking_id, escrow_id=escrow_id,
            description=f'Escrow hold for booking #{booking_id}',
        )
        conn.commit()
        return {'success': True, 'escrow_id': escrow_id, 'amount': float(amount)}
    except Exception as e:
        conn.rollback()
        return {'success': False, 'message': str(e)}
    finally:
        cur.close()
        conn.close()


def release_escrow(booking_id):
    """Release escrow to worker when job is completed."""
    conn = get_db_connection()
    try:
        cur = conn.cursor(cursor_factory=extras.RealDictCursor)
        cur.execute(
            "SELECT * FROM escrow_holds WHERE booking_id = %s AND status = 'held' FOR UPDATE",
            (booking_id,),
        )
        hold = cur.fetchone()
        if not hold:
            return {'success': False, 'message': 'No escrow funds held for this booking'}

        payout = _money(hold['worker_payout'])
        amount = _money(hold['amount'])

        cur.execute(
            "SELECT available_balance FROM user_wallets WHERE user_id = %s FOR UPDATE",
            (hold['worker_user_id'],),
        )
        wrow = cur.fetchone()
        worker_bal = _money(wrow['available_balance']) + payout
        cur.execute(
            "UPDATE user_wallets SET available_balance = %s, updated_at = CURRENT_TIMESTAMP WHERE user_id = %s",
            (worker_bal, hold['worker_user_id']),
        )

        cur.execute(
            """UPDATE escrow_holds SET status = 'released', released_at = CURRENT_TIMESTAMP
               WHERE id = %s""",
            (hold['id'],),
        )
        cur.execute(
            """UPDATE escrow_vault SET total_held = total_held - %s,
               total_released = total_released + %s, updated_at = CURRENT_TIMESTAMP WHERE id = 1""",
            (amount, payout),
        )
        cur.execute(
            "UPDATE bookings SET payment_status = 'released', updated_at = CURRENT_TIMESTAMP WHERE id = %s",
            (booking_id,),
        )

        _ledger(
            cur, hold['worker_user_id'], 'escrow_release', payout, worker_bal,
            booking_id=booking_id, escrow_id=hold['id'],
            description=f'Payment released (fee ${hold["platform_fee"]})',
        )
        conn.commit()
        return {'success': True, 'worker_payout': float(payout)}
    except Exception as e:
        conn.rollback()
        return {'success': False, 'message': str(e)}
    finally:
        cur.close()
        conn.close()


def refund_escrow(booking_id):
    """Return escrowed funds to client on cancellation."""
    conn = get_db_connection()
    try:
        cur = conn.cursor(cursor_factory=extras.RealDictCursor)
        cur.execute(
            "SELECT * FROM escrow_holds WHERE booking_id = %s AND status = 'held' FOR UPDATE",
            (booking_id,),
        )
        hold = cur.fetchone()
        if not hold:
            return {'success': True, 'message': 'No escrow to refund'}

        amount = _money(hold['amount'])
        cur.execute(
            "SELECT available_balance FROM user_wallets WHERE user_id = %s FOR UPDATE",
            (hold['client_id'],),
        )
        crow = cur.fetchone()
        client_bal = _money(crow['available_balance']) + amount
        cur.execute(
            "UPDATE user_wallets SET available_balance = %s, updated_at = CURRENT_TIMESTAMP WHERE user_id = %s",
            (client_bal, hold['client_id']),
        )

        cur.execute(
            "UPDATE escrow_holds SET status = 'refunded', released_at = CURRENT_TIMESTAMP WHERE id = %s",
            (hold['id'],),
        )
        cur.execute(
            "UPDATE escrow_vault SET total_held = total_held - %s, updated_at = CURRENT_TIMESTAMP WHERE id = 1",
            (amount,),
        )
        cur.execute(
            "UPDATE bookings SET payment_status = 'refunded', updated_at = CURRENT_TIMESTAMP WHERE id = %s",
            (booking_id,),
        )

        _ledger(
            cur, hold['client_id'], 'escrow_refund', amount, client_bal,
            booking_id=booking_id, escrow_id=hold['id'],
            description=f'Escrow refund for booking #{booking_id}',
        )
        conn.commit()
        return {'success': True, 'refunded': float(amount)}
    except Exception as e:
        conn.rollback()
        return {'success': False, 'message': str(e)}
    finally:
        cur.close()
        conn.close()
