import sqlite3
from datetime import datetime as dt
from flask import Flask, render_template, request, session, redirect, url_for, flash
from flask_cors import CORS

app = Flask(__name__)
# set a secret key for session management
app.secret_key = "!/!kl41234lkasdfsdjfa"
CORS(app)

# Create a hardcoded username and password
username = 'admin'
password = 'password'

conn = sqlite3.connect('feedback.db')
cursor = conn.cursor()
cursor.execute('''
                    CREATE TABLE IF NOT EXISTS review (
                      rev_id INTEGER PRIMARY KEY AUTOINCREMENT,
                      reviewer_name VARCHAR(50),
                      review_time DATETIME
                    );
''')
for x in range(1, 16):
    cursor.execute('''
                    CREATE TABLE IF NOT EXISTS team'''+str(x)+''' (
                      team1_id INTEGER PRIMARY KEY AUTOINCREMENT,
                      rev_id INT,
                      field1 INT,
                      field2 INT,
                      field3 INT,
                      field4 INT,
                      msg VARCHAR(255),
                      FOREIGN KEY (rev_id) REFERENCES review(rev_id)
                    );
    ''')
cursor.close()
conn.commit()
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
    form_data = request.form
    copy_data = {}
    for key, value in form_data.items():
        copy_data[key] = value

    conn = sqlite3.connect('feedback.db')
    cursor = conn.cursor()

    cursor.execute('''INSERT INTO review(reviewer_name, review_time) VALUES(?, ?); ''',
                   (copy_data['usrname'], dt.now()))
    cursor.execute(''' SELECT MAX(rev_id) FROM review; ''')
    reve_id = cursor.fetchone()
    reve_id = reve_id[0]

    for tno in range(1, 16):
        tno = str(tno)
        cursor.execute(
            '''INSERT INTO team'''+tno +
            '''(rev_id, field1, field2, field3, field4, msg) VALUES(?, ?, ?, ?, ?, ?);''',
            (reve_id, copy_data['myRange'+str(tno)+'A'], copy_data['myRange'+str(tno)+'B'], copy_data['myRange'+str(tno)+'C'], copy_data['myRange'+str(tno)+'D'], copy_data['msg'+tno]))

    cursor.close()
    conn.commit()
    conn.close()

    return render_template('success.html')


if __name__ == '__main__':
    print("hi")
    app.run()
