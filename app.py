import psycopg2
from datetime import datetime as dt
from flask import Flask, render_template, request, session, redirect, url_for, flash
from flask_cors import CORS
from typing import List, Dict


ADMIN_USERNAME = 'TechFest'
ADMIN_PASSWORD = 'TechFest*321'
SECRET_KEY = 'fh5;.&*2Vp/)_&4wCN,..hgVdGJKxBjbfvghHNIyUye45%90O[:O)6'
DB_HOST = "ep-sparkling-resonance-a1x5k0je-pooler.ap-southeast-1.aws.neon.tech"
DB_NAME = "verceldb"
DB_USER = "default"
DB_PASSWORD = "isG18BYMawPt"
NO_OF_TEAMS = 3


conn = psycopg2.connect(
    host=DB_HOST, user=DB_USER, password=DB_PASSWORD, database=DB_NAME)


cursor = conn.cursor()

cursor.execute('''
    CREATE TABLE IF NOT EXISTS reviewer (
        reviewer_id SERIAL PRIMARY KEY,
        reviewer_name VARCHAR(30),
        review_time TIMESTAMP
    );
''')

cursor.execute('''
    CREATE TABLE IF NOT EXISTS team (
        team_id SERIAL PRIMARY KEY,
        team_number INTEGER UNIQUE
    );
''')

cursor.execute('''
    CREATE TABLE IF NOT EXISTS feedbacks (
        feedback_id SERIAL PRIMARY KEY,
        reviewer_id INTEGER,
        team_id INTEGER,
        field1_rating SMALLINT,
        field2_rating SMALLINT,
        field3_rating SMALLINT,
        field4_rating SMALLINT,
        average_rating REAL,
        feedback VARCHAR(255),
        FOREIGN KEY (reviewer_id) REFERENCES reviewer(reviewer_id),
        FOREIGN KEY (team_id) REFERENCES team(team_id)
    );
''')

for team_id in range(1, NO_OF_TEAMS+1):
    cursor.execute(
        ''' INSERT INTO team (team_number) VALUES (%s) ON CONFLICT (team_number) DO NOTHING''', (team_id,))

cursor.close()
conn.commit()
conn.close()

app = Flask(__name__, template_folder='public/templates',
            static_folder='public/static')
app.secret_key = SECRET_KEY
CORS(app)


@app.route('/', methods=['GET'])
def index():
    return render_template('index.html', no_t=NO_OF_TEAMS)


@app.route('/submit', methods=['POST'])
def submit():
    form_data = request.form

    conn = psycopg2.connect(
        host=DB_HOST, user=DB_USER, password=DB_PASSWORD, database=DB_NAME)
    cursor = conn.cursor()

    cursor.execute('INSERT INTO reviewer (reviewer_name, review_time) VALUES (%s, %s) RETURNING reviewer_id',
                   (form_data['reviewer_name'], dt.now()))
    reviewer_row = cursor.fetchone()
    reviewer_id = reviewer_row[0] if reviewer_row is not None else None

    print(form_data, reviewer_id)
    feedbacks = []
    for team_id in range(1, NO_OF_TEAMS+1):
        field1_rating = int(form_data.get(
            f'team_id{team_id}_field1_rating', 1))
        field2_rating = int(form_data.get(
            f'team_id{team_id}_field2_rating', 1))
        field3_rating = int(form_data.get(
            f'team_id{team_id}_field3_rating', 1))
        field4_rating = int(form_data.get(
            f'team_id{team_id}_field4_rating', 1))
        feedback = form_data.get('feedback')

        feedbacks.append((reviewer_id, team_id, field1_rating, field2_rating, field3_rating,
                         field4_rating, field1_rating, field2_rating, field3_rating, field4_rating, feedback))

    print(feedbacks)
    cursor.executemany('''INSERT INTO feedbacks 
                       (reviewer_id, team_id, field1_rating, field2_rating, field3_rating, field4_rating, average_rating, feedback)
                        VALUES (%s, %s, %s, %s, %s, %s, (SELECT AVG(s) FROM UNNEST(ARRAY[%s, %s, %s, %s]) s), %s)''',
                       feedbacks)
    conn.commit()
    cursor.close()
    conn.close()

    return render_template('success.html', name=form_data['reviewer_name'])


@app.route('/login', methods=['GET', 'POST'])
def login():
    error = None
    if request.method == 'POST':
        if request.form['username'] != ADMIN_USERNAME or request.form['password'] != ADMIN_PASSWORD:
            error = 'Invalid Credentials. Please try again.'
        else:
            session['logged_in'] = True
            flash('Login Successful')
            return redirect(url_for('dashboard'))

    return render_template('login.html', error=error)


@app.route('/logout')
def logout():
    session.pop('logged_in', None)
    flash('Logout Successful')
    return redirect(url_for('login'))


@app.route('/dashboard')
def dashboard():
    if not session.get('logged_in'):
        return redirect(url_for('login'))

    conn = mysql.connector.connect(
        host=DB_HOST, user=DB_USER, password=DB_PASSWORD, database=DB_NAME, port=DB_PORT)
    cursor: MySQLCursorAbstract = conn.cursor()
    cursor.execute(operation="SHOW TABLES")
    tables: List[RowType | Dict[str, RowItemType]] = cursor.fetchall()
    table_data = []

    for table_name in tables:
        table_name: RowType | Dict[str, RowItemType] = table_name
        cursor.execute(operation=f"SELECT * FROM {table_name}")
        rows: List[RowType | Dict[str, RowItemType]] = cursor.fetchall()
        table_data.append({'name': table_name, 'rows': rows})
    cursor.close()
    conn.commit()
    conn.close()

    return render_template(template_name_or_list='dashboard.html', tables=table_data, no_t=NO_OF_TEAMS)


@app.route('/calculate', methods=['GET'])
def calculate():
    if not session.get('logged_in'):
        return redirect(url_for('login'))

    conn = mysql.connector.connect(
        host=DB_HOST, user=DB_USER, password=DB_PASSWORD, database=DB_NAME, port=DB_PORT)
    cursor = conn.cursor()
    cursor.execute("DELETE FROM avg_table")

    for i in range(1, NO_OF_TEAMS):
        table_name = 'team{}'.format(i)

        cursor.execute('SELECT AVG(average) FROM {}'.format(table_name))
        team_avg = cursor.fetchone()
        cursor.execute('INSERT INTO avg_table (team_id, team_name, team_average, calc_time) VALUES (%s, %s, %s, %s)',
                       (i, 'Team {}'.format(i), team_avg, dt.now()))

    cursor.execute('''CREATE TEMPORARY TABLE temp_table AS
         SELECT * FROM avg_table ORDER BY team_average DESC''')
    cursor.execute('''DELETE FROM avg_table''')
    cursor.execute('''INSERT INTO avg_table SELECT * FROM temp_table''')
    cursor.execute('''DROP TABLE temp_table''')
    cursor.close()
    conn.commit()
    conn.close()

    return redirect(location=url_for(endpoint='dashboard'))


if __name__ == '__main__':
    app.run()
