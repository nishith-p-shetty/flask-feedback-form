import sqlite3
from flask import Flask, render_template, request, session, redirect, url_for, flash
from flask_cors import CORS
import json
from datetime import datetime

app = Flask(__name__)
app.secret_key = '!#!kl41234lkasdfsdjfa'  # set a secret key for session management
CORS(app)

# Create a hardcoded username and password
username = 'admin'
password = 'password'

conn = sqlite3.connect('feedback.db')
cursor = conn.cursor()
cursor.execute('''
    CREATE TABLE IF NOT EXISTS feedbackInfo (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT,
        stars INTEGER,
        message TEXT
    );
''')
cursor.close()
conn.close()


@app.route('/login', methods=['GET', 'POST'])
def login():
    error = None
    if request.method == 'POST':
        if request.form['username'] != username or request.form['password'] != password:
            error = 'Invalid Credentials. Please try again.'
        else:
            session['logged_in'] = True
            flash('You were logged in')
            return redirect(url_for('dashboard'))
    return render_template('login.html', error=error)


@app.route('/logout')
def logout():
    session.pop('logged_in', None)
    flash('You were logged out')
    return redirect(url_for('login'))


@app.route('/')
def dashboard():
    if not session.get('logged_in'):
        return redirect(url_for('login'))

    conn = sqlite3.connect('feedback.db')
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM feedbackInfo')
    rows = cursor.fetchall()
    cursor.close()
    conn.close()

    return render_template('dashboard.html', rows=rows)


@app.route('/submit', methods=['POST'])
def submit():
    conn = sqlite3.connect('feedback.db')
    cursor = conn.cursor()
    data = request.json
    cursor.execute('''INSERT INTO feedbackInfo (name, stars, message)VALUES (?, ?, ?);''', (data["name"], data["stars"], data["fedbakmsg"]))
    conn.commit()
    cursor.close()
    conn.close()
    return json.dumps({'success': True}), 200, {'ContentType': 'application/json'}


if __name__ == '__main__':
    print("hi")
    app.run()

