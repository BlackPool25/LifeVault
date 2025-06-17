import sqlite3
import datetime

conn = sqlite3.connect("vault.db")
cursor = conn.cursor()

# Users table for authentication
cursor.execute('''
CREATE TABLE IF NOT EXISTS users (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    username TEXT UNIQUE NOT NULL,
    password_hash TEXT NOT NULL,
    email TEXT,
    emergency_pin TEXT NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
)
''')

# Vault table with user association
cursor.execute('''
CREATE TABLE IF NOT EXISTS vault (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER NOT NULL,
    category TEXT NOT NULL,
    title TEXT NOT NULL,
    encrypted_data TEXT NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users (id)
)
''')

# Emergency contacts with user association
cursor.execute('''
CREATE TABLE IF NOT EXISTS emergency_contacts (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER NOT NULL,
    name TEXT NOT NULL,
    phone TEXT NOT NULL,
    email TEXT,
    allowed_categories TEXT NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users (id)
)
''')

# Security logs for failed attempts
cursor.execute('''
CREATE TABLE IF NOT EXISTS security_logs (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER,
    action TEXT NOT NULL,
    ip_address TEXT,
    timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    details TEXT,
    FOREIGN KEY (user_id) REFERENCES users (id)
)
''')

# Failed PIN attempts tracking
cursor.execute('''
CREATE TABLE IF NOT EXISTS failed_attempts (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER NOT NULL,
    attempt_type TEXT NOT NULL,
    ip_address TEXT,
    timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users (id)
)
''')

conn.commit()

def get_cursor():
    return cursor

def get_connection():
    return conn

def close_db():
    conn.close()

def log_security_event(user_id, action, ip_address="localhost", details=""):
    """Log security events for audit trail"""
    cursor.execute(
        "INSERT INTO security_logs (user_id, action, ip_address, details) VALUES (?, ?, ?, ?)",
        (user_id, action, ip_address, details)
    )
    conn.commit()

def get_failed_attempts(user_id, attempt_type, hours=2):
    """Get failed attempts in the last N hours"""
    cursor.execute(
        """SELECT COUNT(*) FROM failed_attempts 
           WHERE user_id = ? AND attempt_type = ? 
           AND timestamp > datetime('now', '-{} hours')""".format(hours),
        (user_id, attempt_type)
    )
    return cursor.fetchone()[0]

def log_failed_attempt(user_id, attempt_type, ip_address="localhost"):
    """Log a failed attempt"""
    cursor.execute(
        "INSERT INTO failed_attempts (user_id, attempt_type, ip_address) VALUES (?, ?, ?)",
        (user_id, attempt_type, ip_address)
    )
    conn.commit()

def is_account_locked(user_id, attempt_type="pin"):
    """Check if account is locked due to too many failed attempts"""
    failed_count = get_failed_attempts(user_id, attempt_type)
    return failed_count >= 3  # Lock after 3 failed attempts