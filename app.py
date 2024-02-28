import sqlite3
from datetime import datetime as dt
from flask import Flask, render_template, request, session, redirect, url_for, flash
from flask_cors import CORS
from waitress import serve

app = Flask(__name__)
app.secret_key = "fh5;.&*2Vp/)_&4wCN,..hgVdGJKxBjbfvghHNIyUye45%90O[:O)6]"
CORS(app)

# Create a hardcoded username and password
username = 'TechFest'
password = 'TechFest*321'


no_t = 12  # team+1


conn = sqlite3.connect('feedback.db')
cursor = conn.cursor()
cursor.execute('''
                    CREATE TABLE IF NOT EXISTS review (
                      rev_id INTEGER PRIMARY KEY AUTOINCREMENT,
                      reviewer_name VARCHAR(50),
                      review_time DATETIME
                    );
''')
for x in range(1, no_t):
    cursor.execute('''
                    CREATE TABLE IF NOT EXISTS team'''+str(x)+''' (
                      team1_id INTEGER PRIMARY KEY AUTOINCREMENT,
                      rev_id INT,
                      field1 INT,
                      field2 INT,
                      field3 INT,
                      field4 INT,
                      average REAL,
                      msg VARCHAR(255),
                      FOREIGN KEY (rev_id) REFERENCES review(rev_id)
                    );
    ''')
cursor.execute('''
                    CREATE TABLE IF NOT EXISTS avg_table (
                      team_id INTEGER,
                      team_name VARCHAR(50),
                      team_average REAL,
                      calc_time DATETIME
                    );
   ''')
cursor.close()
conn.commit()
conn.close()


@app.route('/', methods=['GET'])
def index():
    return render_template('index.html', no_t=no_t)


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


@app.route('/dashboard')
def dashboard():
    if not session.get('logged_in'):
        return redirect(url_for('login'))

    conn = sqlite3.connect('feedback.db')
    cursor = conn.cursor()
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
    tables = cursor.fetchall()
    table_data = []
    for table_name in tables:
        table_name = table_name[0]
        cursor.execute(f"SELECT * FROM {table_name}")
        rows = cursor.fetchall()
        table_data.append({'name': table_name, 'rows': rows})
    cursor.close()
    conn.close()
    return render_template('dashboard.html', tables=table_data, no_t=no_t)


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

    for tno in range(1, no_t):
        tno = str(tno)
        avg = (int(copy_data['myRange'+str(tno)+'A']) + int(copy_data['myRange'+str(
            tno)+'B']) + int(copy_data['myRange'+str(tno)+'C']) + int(copy_data['myRange'+str(tno)+'D'])*2)/5
        cursor.execute(
            '''INSERT INTO team'''+tno +
            '''(rev_id, field1, field2, field3, field4, average, msg) VALUES(?, ?, ?, ?, ?, ?, ?);''',
            (reve_id, copy_data['myRange'+str(tno)+'A'], copy_data['myRange'+str(tno)+'B'], copy_data['myRange'+str(tno)+'C'], copy_data['myRange'+str(tno)+'D'], avg, copy_data['msg'+tno]))

    cursor.close()
    conn.commit()
    conn.close()

    return render_template('success.html')


@app.route('/calculate', methods=['GET'])
def calculate():
    if not session.get('logged_in'):
        return redirect(url_for('login'))

    conn = sqlite3.connect('feedback.db')
    c = conn.cursor()
    c.execute("DELETE FROM avg_table")

    for i in range(1, no_t):
        table_name = 'team{}'.format(i)

        c.execute('SELECT AVG(average) FROM {}'.format(table_name))
        team_avg = c.fetchone()[0]
        c.execute('INSERT INTO avg_table (team_id, team_name, team_average, calc_time) VALUES (?, ?, ?, ?)',
                  (i, 'Team {}'.format(i), team_avg, dt.now()))

    c.execute('''CREATE TEMPORARY TABLE temp_table AS
         SELECT * FROM avg_table ORDER BY team_average DESC''')
    c.execute('''DELETE FROM avg_table''')
    c.execute('''INSERT INTO avg_table SELECT * FROM temp_table''')
    c.execute('''DROP TABLE temp_table''')

    conn.commit()
    conn.close()

    return redirect(url_for('dashboard'))


if __name__ == '__main__':
    print("Server started")
    serve(app, host='0.0.0.0', port=1234, threads=4, url_scheme='https')
