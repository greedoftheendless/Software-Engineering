import os
import csv
import sqlite3
from flask import Flask, render_template, request, redirect, url_for, flash, session, send_file
from werkzeug.security import generate_password_hash, check_password_hash

# Initialize Flask app
app = Flask(__name__)
app.secret_key = 'your_secure_random_key'

# Database connection function
def get_db_connection():
    conn = sqlite3.connect('odms.db', timeout=20)
    conn.row_factory = sqlite3.Row
    return conn

def register_user(username, email, password):
    try:
        conn = get_db_connection()
        c = conn.cursor()
        hashed_password = generate_password_hash(password)
        c.execute('INSERT INTO users (username, email, password) VALUES (?, ?, ?)', 
                 (username, email, hashed_password))
        conn.commit()
        conn.close()
        return True
    except sqlite3.IntegrityError:
        return False
    finally:
        if 'conn' in locals():
            conn.close()

def login_user(username, password):
    try:
        conn = get_db_connection()
        c = conn.cursor()
        c.execute('SELECT password FROM users WHERE username=?', (username,))
        row = c.fetchone()
        return bool(row and check_password_hash(row[0], password))
    finally:
        if 'conn' in locals():
            conn.close()

@app.route('/dashboard')
def dashboard():
    if 'username' not in session:
        flash('Please log in first!', 'warning')
        return redirect(url_for('login'))
    
    try:
        conn = get_db_connection()
        c = conn.cursor()
        c.execute('SELECT id, sheet_name, creator FROM sheets')
        sheets = c.fetchall()
        
        # Convert to list of tuples for easier template handling
        sheet_list = []
        for sheet in sheets:
            sheet_list.append((sheet['id'], sheet['sheet_name'], sheet['creator']))
        
        return render_template('dashboard.html', user_name=session['username'], sheets=sheet_list)
    except Exception as e:
        flash(f'Error loading dashboard: {str(e)}', 'danger')
        return render_template('dashboard.html', user_name=session['username'], sheets=[])
    finally:
        if 'conn' in locals():
            conn.close()

@app.route('/create_sheet', methods=['GET', 'POST'])
def create_sheet():
    if 'username' not in session:
        flash('Please log in first!', 'warning')
        return redirect(url_for('login'))
    if request.method == 'POST':
        sheet_name = request.form['sheet_name']
        creator = session['username']
        conn = sqlite3.connect('odms.db')
        c = conn.cursor()
        c.execute('INSERT INTO sheets (sheet_name, creator) VALUES (?, ?)', (sheet_name, creator))
        conn.commit()
        conn.close()
        flash('New sheet created!', 'success')
        return redirect(url_for('dashboard'))
    return render_template('create_sheet.html')

@app.route('/sheet/<int:sheet_id>', methods=['GET', 'POST'])
def sheet_detail(sheet_id):
    if 'username' not in session:
        flash('Please log in first!', 'warning')
        return redirect(url_for('login'))
    conn = sqlite3.connect('odms.db')
    c = conn.cursor()
    c.execute('SELECT sheet_name, creator FROM sheets WHERE id=?', (sheet_id,))
    row = c.fetchone()
    if not row:
        conn.close()
        flash('Sheet not found!', 'danger')
        return redirect(url_for('dashboard'))
    sheet_name, creator = row

    if request.method == 'POST':
        name = request.form['name']
        roll = request.form['roll_number']
        slots = request.form.getlist('time_slots')
        user = session['username']
        c.execute('SELECT user FROM entries WHERE sheet_id=? AND user=?', (sheet_id, user))
        existing = c.fetchone()
        # Only one entry for non-creator
        if user != creator and existing:
            flash('You already submitted an entry!', 'danger')
        else:
            c.execute('INSERT INTO entries (sheet_id, name, roll_number, time_slots, user) VALUES (?,?,?,?,?)',
                      (sheet_id, name, roll, ','.join(slots), user))
            flash('Entry added!', 'success')
        conn.commit()

    c.execute('SELECT id, name, roll_number, time_slots, user FROM entries WHERE sheet_id=?', (sheet_id,))
    entries = c.fetchall()
    conn.close()
    return render_template('sheet.html',
                           sheet_id=sheet_id,
                           sheet_name=sheet_name,
                           creator=creator,
                           entries=entries,
                           current_user=session['username'])

@app.route('/sheet/<int:sheet_id>/delete_entry/<int:entry_id>', methods=['POST'])
def delete_entry(sheet_id, entry_id):
    if 'username' not in session:
        return redirect(url_for('login'))
    user = session['username']
    conn = sqlite3.connect('odms.db')
    c = conn.cursor()
    c.execute('SELECT creator FROM sheets WHERE id=?', (sheet_id,))
    sheet_creator = c.fetchone()
    if sheet_creator and user == sheet_creator[0]:
        c.execute('DELETE FROM entries WHERE id=?', (entry_id,))
        conn.commit()
        flash('Entry deleted!', 'info')
    conn.close()
    return redirect(url_for('sheet_detail', sheet_id=sheet_id))

@app.route('/sheet/<int:sheet_id>/download')
def download_sheet(sheet_id):
    if 'username' not in session:
        return redirect(url_for('login'))
    conn = sqlite3.connect('odms.db')
    c = conn.cursor()
    c.execute('SELECT name, roll_number, time_slots, user FROM entries WHERE sheet_id=?', (sheet_id,))
    rows = c.fetchall()
    conn.close()
    csv_path = f"sheet_{sheet_id}.csv"
    with open(csv_path, 'w', newline='', encoding='utf-8') as f:
        writer = csv.writer(f)
        writer.writerow(['Name', 'Roll Number', 'Time Slots', 'Submitted By'])
        for r in rows:
            writer.writerow(r)
    return send_file(csv_path, as_attachment=True)

# Add this function before the if __name__ == '__main__': block

def init_db():
    conn = get_db_connection()
    c = conn.cursor()
    # Table for users
    c.execute('''
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT NOT NULL UNIQUE,
            email TEXT NOT NULL UNIQUE,
            password TEXT NOT NULL
        )
    ''')
    # Table for sheets
    c.execute('''
        CREATE TABLE IF NOT EXISTS sheets (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            sheet_name TEXT NOT NULL,
            creator TEXT NOT NULL
        )
    ''')
    # Table for entries in each sheet
    c.execute('''
        CREATE TABLE IF NOT EXISTS entries (
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

# Add this route after the login_user function and before the dashboard route

@app.route('/')
def index():
    return redirect(url_for('login'))

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        action = request.form.get('action')
        if action == 'signup':
            username = request.form['username']
            email = request.form['email']
            password = request.form['password']
            if register_user(username, email, password):
                flash('Registration successful! You can now log in.', 'success')
            else:
                flash('Username or email already exists!', 'danger')
        elif action == 'login':
            username = request.form['username']
            password = request.form['password']
            if login_user(username, password):
                session['username'] = username
                flash('Login successful!', 'success')
                return redirect(url_for('dashboard'))
            else:
                flash('Invalid credentials! Try again.', 'danger')
    return render_template('login.html')

# Add this route after the login route

@app.route('/logout')
def logout():
    # Remove username from session
    session.pop('username', None)
    flash('You have been logged out successfully!', 'success')
    return redirect(url_for('login'))

@app.route('/contact')
def contact():
    return render_template('contact.html')

if __name__ == '__main__':
    init_db()
    app.run(debug=True, port=8000)