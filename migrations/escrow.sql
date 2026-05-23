-- ProTech Escrow & Wallet System
-- Run once on existing databases: python migrate_escrow.py <DATABASE_URL>

-- Wallets (available balance per user)
CREATE TABLE IF NOT EXISTS user_wallets (
    user_id INTEGER PRIMARY KEY REFERENCES users(id) ON DELETE CASCADE,
    available_balance DECIMAL(12,2) NOT NULL DEFAULT 0.00 CHECK (available_balance >= 0),
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Platform escrow vault (funds held until job completion)
CREATE TABLE IF NOT EXISTS escrow_vault (
    id INTEGER PRIMARY KEY DEFAULT 1 CHECK (id = 1),
    total_held DECIMAL(14,2) NOT NULL DEFAULT 0.00 CHECK (total_held >= 0),
    total_released DECIMAL(14,2) NOT NULL DEFAULT 0.00 CHECK (total_released >= 0),
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

INSERT INTO escrow_vault (id, total_held, total_released) VALUES (1, 0, 0)
ON CONFLICT (id) DO NOTHING;

-- Escrow hold per booking (one active hold per booking)
CREATE TABLE IF NOT EXISTS escrow_holds (
    id SERIAL PRIMARY KEY,
    booking_id INTEGER NOT NULL UNIQUE REFERENCES bookings(id) ON DELETE CASCADE,
    client_id INTEGER NOT NULL REFERENCES users(id),
    worker_user_id INTEGER NOT NULL REFERENCES users(id),
    amount DECIMAL(12,2) NOT NULL CHECK (amount > 0),
    platform_fee DECIMAL(12,2) NOT NULL DEFAULT 0.00,
    worker_payout DECIMAL(12,2),
    status VARCHAR(20) NOT NULL DEFAULT 'held'
        CHECK (status IN ('held', 'released', 'refunded')),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    released_at TIMESTAMP
);

-- Immutable ledger for audit trail
CREATE TABLE IF NOT EXISTS wallet_transactions (
    id SERIAL PRIMARY KEY,
    user_id INTEGER NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    booking_id INTEGER REFERENCES bookings(id) ON DELETE SET NULL,
    escrow_id INTEGER REFERENCES escrow_holds(id) ON DELETE SET NULL,
    transaction_type VARCHAR(32) NOT NULL,
    amount DECIMAL(12,2) NOT NULL,
    balance_after DECIMAL(12,2) NOT NULL,
    description TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX IF NOT EXISTS idx_wallet_tx_user ON wallet_transactions(user_id, created_at DESC);
CREATE INDEX IF NOT EXISTS idx_escrow_holds_status ON escrow_holds(status);

-- Expand booking payment_status for escrow lifecycle
ALTER TABLE bookings DROP CONSTRAINT IF EXISTS bookings_payment_status_check;
ALTER TABLE bookings ADD CONSTRAINT bookings_payment_status_check
    CHECK (payment_status IN ('pending', 'escrow_held', 'released', 'refunded', 'paid'));

-- Legacy 'paid' treated as released in application code
UPDATE bookings SET payment_status = 'released' WHERE payment_status = 'paid';

-- Wallets for existing users
INSERT INTO user_wallets (user_id, available_balance)
SELECT id, 0 FROM users
ON CONFLICT (user_id) DO NOTHING;

-- Demo starter balance for sample client (optional)
UPDATE user_wallets SET available_balance = 500.00
WHERE user_id = (SELECT id FROM users WHERE email = 'john@example.com' LIMIT 1);
