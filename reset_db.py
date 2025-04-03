import sqlite3
import os

def reset_database():
    # Remove existing database file if it exists
    if os.path.exists('odms.db'):
        os.remove('odms.db')
    
    # Create new database and tables
    conn = sqlite3.connect('odms.db')
    c = conn.cursor()
    
    # Recreate users table
    c.execute('''
        CREATE TABLE users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT NOT NULL UNIQUE,
            email TEXT NOT NULL UNIQUE,
            password TEXT NOT NULL
        )
    ''')
    
    # Recreate sheets table
    c.execute('''
        CREATE TABLE sheets (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            sheet_name TEXT NOT NULL,
            creator TEXT NOT NULL
        )
    ''')
    
    # Recreate entries table
    c.execute('''
        CREATE TABLE entries (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            sheet_id INTEGER NOT NULL,
            name TEXT NOT NULL,
            roll_number TEXT NOT NULL,
            time_slots TEXT NOT NULL,
            user TEXT NOT NULL
        )
    ''')
    
    conn.commit()
    conn.close()
    print("Database has been reset successfully!")

if __name__ == "__main__":
    reset_database()