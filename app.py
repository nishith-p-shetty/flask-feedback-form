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

# ADMIN_USERNAME = os.environ.get('FEEDBACK_FORM_ADMIN_USERNAME')
# SECRET_KEY = os.environ.get('FEEDBACK_FORM_SECRET_KEY')
# DB_USER = "default"
# DB_HOST = "ep-sparkling-resonance-a1x5k0je-pooler.ap-southeast-1.aws.neon.tech"
# DB_PASSWORD = "GI8YseR5UJZV"
# DB_NAME = "verceldb"

# print(ADMIN_USERNAME, ADMIN_PASSWORD, SECRET_KEY,
#   DB_HOST, DB_NAME, DB_USER, DB_PASSWORD)

NO_OF_TEAMS = 35


conn = psycopg2.connect(
    host=DB_HOST, user=DB_USER, password=DB_PASSWORD, database=DB_NAME,
    sslmode='prefer')


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
        field5_rating SMALLINT,
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
        field5_rating = int(form_data.get(
            f'team_id{team_id}_field5_rating', 1))

        feedback = form_data.get(f'team_id{ team_id }_feedback')

        # cursor.execute('''''')

        feedbacks.append((reviewer_id, team_id, field1_rating, field2_rating, field3_rating,
                         field4_rating, field5_rating, field1_rating, field2_rating, field3_rating, field4_rating, field5_rating, feedback))

    cursor.executemany('''INSERT INTO feedbacks 
                       (reviewer_id, team_id, field1_rating, field2_rating, field3_rating, field4_rating, field5_rating, average_rating, feedback)
                        VALUES (%s, %s, %s, %s, %s, %s, %s, (SELECT AVG(s) FROM UNNEST(ARRAY[%s, %s, %s, %s, %s]) s), %s)''',
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


@app.route('/dashboard', methods=['GET', 'POST'])
def dashboard():
    page = request.args.get('page', 1, type=int)
    search = request.args.get('search', '', type=str).strip().lower()

    conn = psycopg2.connect(database=DB_NAME, user=DB_USER,
                            password=DB_PASSWORD, host=DB_HOST)
    cursor = conn.cursor()

    # Caluculate the total number of pages
    cursor.execute('''SELECT COUNT(*) FROM feedbacks JOIN reviewer 
                    ON
                    feedbacks.reviewer_id = reviewer.reviewer_id
                    WHERE LOWER(reviewer_name) LIKE %s''',
                   ('%' + search + '%',))
    total_feedbacks = cursor.fetchone()
    total_feedbacks = total_feedbacks[0] if total_feedbacks is not None else 0
    total_pages = (total_feedbacks // 5) + 1

    # Fetch 5 feedbacks with reviewer and team details
    cursor.execute('''
        SELECT 
            feedbacks.feedback_id,
            reviewer.reviewer_name,
            team.team_number,
            feedbacks.field1_rating,
            feedbacks.field2_rating,
            feedbacks.field3_rating,
            feedbacks.field4_rating,
            feedbacks.field5_rating,
            feedbacks.average_rating,
            reviewer.review_time,
            feedbacks.feedback
        FROM feedbacks
        INNER JOIN reviewer ON feedbacks.reviewer_id = reviewer.reviewer_id
        INNER JOIN team ON feedbacks.team_id = team.team_id
        WHERE LOWER(reviewer.reviewer_name) LIKE %s
        ORDER BY reviewer.review_time DESC 
        LIMIT 5 OFFSET %s;
    ''', ('%' + search + '%', (page-1)*5))

    data = cursor.fetchall()

    cursor.execute('''
        (SELECT 'average_rating' AS rating_type, team_id, AVG(average_rating) AS rating
        FROM feedbacks
        GROUP BY team_id
        ORDER BY rating DESC)
        UNION ALL
        (SELECT 'field1_rating' AS rating_type, team_id, AVG(field1_rating) AS rating
        FROM feedbacks
        GROUP BY team_id
        ORDER BY rating DESC)
        UNION ALL
        (SELECT 'field2_rating' AS rating_type, team_id, AVG(field2_rating) AS rating
        FROM feedbacks
        GROUP BY team_id
        ORDER BY rating DESC)
        UNION ALL
        (SELECT 'field3_rating' AS rating_type, team_id, AVG(field3_rating) AS rating
        FROM feedbacks
        GROUP BY team_id
        ORDER BY rating DESC)
        UNION ALL
        (SELECT 'field4_rating' AS rating_type, team_id, AVG(field4_rating) AS rating
        FROM feedbacks
        GROUP BY team_id
        ORDER BY rating DESC)
        UNION ALL
        (SELECT 'field5_rating' AS rating_type, team_id, AVG(field5_rating) AS rating
        FROM feedbacks
        GROUP BY team_id
        ORDER BY rating DESC);
    ''')
    best_teams = cursor.fetchall()

    cursor.close()
    conn.close()

    return render_template(
        'dashboard.html',
        best_teams=best_teams,
        data=data,
        total_pages=total_pages,
        page=page,
        search=search,
        no_of_teams=NO_OF_TEAMS
    )


@app.route('/logout')
def logout():
    session.pop('logged_in', None)
    flash('Logout Successful')
    return redirect(url_for('login'))


@app.route('/delete_feedback/<int:feedback_id>', methods=['GET'])
def delete_feedback(feedback_id):
    if not session.get('logged_in'):
        flash('Please login to delete feedback.')
        return redirect(url_for('login'))

    conn = psycopg2.connect(database=DB_NAME, user=DB_USER,
                            password=DB_PASSWORD, host=DB_HOST)
    cursor = conn.cursor()

    cursor.execute(
        'DELETE FROM feedbacks WHERE feedback_id = %s', (feedback_id,))
    conn.commit()
    cursor.close()
    conn.close()

    flash('Feedback deleted successfully.')
    return redirect(url_for('dashboard'))


@app.route('/favicon.ico')
def favicon():
    # return redirect(url_for('static', filename='images/favicon.ico'))
    return redirect(url_for('static', filename='favicon.ico'))


if __name__ == '__main__':
    app.run()
