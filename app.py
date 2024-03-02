import psycopg2
import os
from datetime import datetime as dt
from flask import Flask, render_template, request, session, redirect, url_for, flash
from flask_cors import CORS
from dotenv import load_dotenv

load_dotenv()

ADMIN_USERNAME = os.environ.get('FEEDBACK_FORM_ADMIN_USERNAME')
ADMIN_PASSWORD = os.environ.get('FEEDBACK_FORM_ADMIN_PASSWORD')
SECRET_KEY = os.environ.get('FEEDBACK_FORM_SECRET_KEY')
DB_HOST = os.environ.get('FEEDBACK_FORM_DB_HOST')
DB_NAME = os.environ.get('FEEDBACK_FORM_DB_NAME')
DB_USER = os.environ.get('FEEDBACK_FORM_DB_USER')
DB_PASSWORD = os.environ.get('FEEDBACK_FORM_DB_PASSWORD')

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
        feedback = form_data.get(f'team_id{ team_id }_feedback')

        # cursor.execute('''''')

        feedbacks.append((reviewer_id, team_id, field1_rating, field2_rating, field3_rating,
                         field4_rating, field1_rating, field2_rating, field3_rating, field4_rating, feedback))

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


@app.route('/dashboard')
def dashboard():
    conn = psycopg2.connect(database=DB_NAME, user=DB_USER,
                            password=DB_PASSWORD, host=DB_HOST)
    cursor = conn.cursor()

    # Fetch all feedbacks with reviewer and team details
    cursor.execute('''
        SELECT feedbacks.reviewer_id, reviewer.reviewer_name, team.team_number, feedbacks.field1_rating, feedbacks.field2_rating, feedbacks.field3_rating, feedbacks.field4_rating, feedbacks.average_rating, feedbacks.feedback
        FROM feedbacks
        INNER JOIN reviewer ON feedbacks.reviewer_id = reviewer.reviewer_id
        INNER JOIN team ON feedbacks.team_id = team.team_id
        ORDER BY feedbacks.average_rating LIMIT 5;
    ''')
    data = cursor.fetchall()

    with open('data.txt', 'w') as f:
        for row in data:
            f.write(str(row)+'\n')

    # Fetch the team with the highest average rating
    cursor.execute('''
        SELECT team_id, AVG(average_rating) as avg_rating
        FROM feedbacks
        GROUP BY team_id
        ORDER BY avg_rating DESC
        LIMIT 1;
    ''')
    best_team = cursor.fetchone()

    # Fetch the team with the highest rating in each field
    fields = ['field1_rating', 'field2_rating',
              'field3_rating', 'field4_rating']
    best_in_fields = {}
    for field in fields:
        cursor.execute(f'''
            SELECT team_id, AVG({field}) as avg_rating
            FROM feedbacks
            GROUP BY team_id
            ORDER BY avg_rating DESC
            LIMIT 1;
        ''')
        best_in_fields[field] = cursor.fetchone()

    # Fetch reviewer statistics
    cursor.execute('''
        SELECT reviewer_id, COUNT(*) as review_count, AVG(average_rating) as avg_rating
        FROM feedbacks
        GROUP BY reviewer_id;
    ''')
    reviewer_stats = cursor.fetchall()

    cursor.close()
    conn.close()

    return render_template('dashboard.html', data=data, best_team=best_team, best_in_fields=best_in_fields, reviewer_stats=reviewer_stats)


@app.route('/logout')
def logout():
    session.pop('logged_in', None)
    flash('Logout Successful')
    return redirect(url_for('login'))


if __name__ == '__main__':
    app.run()
