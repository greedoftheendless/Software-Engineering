import sqlite3

# Connect to SQLite database (it will create users.db if it doesn't exist)
conn = sqlite3.connect("users.db")
c = conn.cursor()

# Drop old table if it exists (to prevent schema issues)
c.execute("DROP TABLE IF EXISTS users")

# Create a new users table with email column
c.execute('''
    CREATE TABLE users (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        username TEXT UNIQUE NOT NULL,
        email TEXT UNIQUE NOT NULL,
        password TEXT NOT NULL
    )
''')

conn.commit()
conn.close()

print("Database and users table created successfully.")
