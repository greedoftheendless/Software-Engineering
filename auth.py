import sqlite3
import os
from werkzeug.security import generate_password_hash, check_password_hash

DB_PATH = os.path.join(os.path.dirname(__file__), "users.db")


def register_user(username, email, password):
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    hashed_password = generate_password_hash(password, method='pbkdf2:sha256')
    try:
        c.execute("INSERT INTO users (username, email, password) VALUES (?, ?, ?)",
                  (username, email, hashed_password))
        conn.commit()
    except sqlite3.IntegrityError:
        return False  # Username or email already exists
    finally:
        conn.close()
    return True


def login_user(username, password):
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute("SELECT password FROM users WHERE username = ?", (username,))
    user = c.fetchone()
    conn.close()

    if user and check_password_hash(user[0], password):
        return True
    return False
