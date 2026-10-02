from flask import Flask, render_template, request, redirect, session
import sqlite3

app = Flask(__name__)
app.secret_key = 'student_feedback_secret_key'


# ---------------- DATABASE INITIALIZATION ----------------

def init_db():
    conn = sqlite3.connect('feedback.db')
    cursor = conn.cursor()

    # Feedback table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS feedback (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            student_name TEXT NOT NULL,
            subject TEXT NOT NULL,
            rating INTEGER NOT NULL,
            feedback TEXT NOT NULL
        )
    ''')

    # Students table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS students (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT UNIQUE NOT NULL,
            password TEXT NOT NULL
        )
    ''')

    conn.commit()
    conn.close()


init_db()


# ---------------- HOME PAGE ----------------

@app.route('/')
def home():
    return render_template('index.html')


# ---------------- ADMIN LOGIN ----------------

@app.route('/admin_login', methods=['GET', 'POST'])
def admin_login():

    if request.method == 'POST':

        username = request.form['username']
        password = request.form['password']

        if username == 'admin' and password == 'admin1234':

            session.clear()
            session['admin_logged_in'] = True

            return redirect('/admin_dashboard')

        else:
            return 'Invalid admin username or password'

    return render_template('admin_login.html')


# ---------------- ADMIN DASHBOARD ----------------

@app.route('/admin_dashboard')
def admin_dashboard():

    if session.get('admin_logged_in') != True:
        return redirect('/admin_login')

    return render_template('admin.html')


# ---------------- STUDENT REGISTRATION ----------------

@app.route('/register', methods=['GET', 'POST'])
def register():

    if request.method == 'POST':

        username = request.form['username']
        password = request.form['password']

        conn = sqlite3.connect('feedback.db')
        cursor = conn.cursor()

        try:

            cursor.execute(
                'INSERT INTO students (username, password) VALUES (?, ?)',
                (username, password)
            )

            conn.commit()
            conn.close()

            return '''
                <h1>Registration Successful!</h1>
                <p>Your student account has been created.</p>
                <br>
                <a href="/student_login">Go to Student Login</a>
            '''

        except sqlite3.IntegrityError:

            conn.close()

            return '''
                <h1>Username Already Exists!</h1>
                <p>Please choose a different username.</p>
                <br>
                <a href="/register">Try Again</a>
            '''

    return render_template('register.html')


# ---------------- STUDENT LOGIN ----------------

@app.route('/student_login', methods=['GET', 'POST'])
def student_login():

    if request.method == 'POST':

        username = request.form['username']
        password = request.form['password']

        conn = sqlite3.connect('feedback.db')
        cursor = conn.cursor()

        cursor.execute(
            'SELECT * FROM students WHERE username = ? AND password = ?',
            (username, password)
        )

        student = cursor.fetchone()

        conn.close()

        # Temporary fixed login also kept
        if username == 'student' and password == 'student123':

            session.clear()
            session['student_logged_in'] = True
            session['student_username'] = username

            return redirect('/student_dashboard')

        # Registered student login
        elif student:

            session.clear()
            session['student_logged_in'] = True
            session['student_username'] = username

            return redirect('/student_dashboard')

        else:
            return 'Invalid student username or password'

    return render_template('student_login.html')


# ---------------- STUDENT DASHBOARD ----------------

@app.route('/student_dashboard')
def student_dashboard():

    if session.get('student_logged_in') != True:
        return redirect('/student_login')

    return render_template('student_dashboard.html')


# ---------------- SUBMIT FEEDBACK ----------------

@app.route('/feedback', methods=['POST'])
def feedback():

    if session.get('student_logged_in') != True:
        return redirect('/student_login')

    student_name = request.form['student_name']
    subject = request.form['subject']
    rating = request.form['rating']
    feedback_text = request.form['feedback']

    conn = sqlite3.connect('feedback.db')
    cursor = conn.cursor()

    cursor.execute('''
        INSERT INTO feedback
        (student_name, subject, rating, feedback)
        VALUES (?, ?, ?, ?)
    ''', (
        student_name,
        subject,
        rating,
        feedback_text
    ))

    conn.commit()
    conn.close()

    return f'''
        <h1>Feedback Submitted Successfully!</h1>

        <p>Thank you, {student_name}.</p>

        <p>Your feedback has been saved.</p>

        <br>

        <a href="/student_dashboard">
            Back to Student Dashboard
        </a>
    '''


# ---------------- VIEW STUDENT FEEDBACK ----------------

@app.route('/view_feedback')
def view_feedback():

    if session.get('admin_logged_in') != True:
        return redirect('/admin_login')

    conn = sqlite3.connect('feedback.db')
    conn.row_factory = sqlite3.Row

    cursor = conn.cursor()

    cursor.execute('SELECT * FROM feedback')

    feedbacks = cursor.fetchall()

    conn.close()

    return render_template(
        'view_feedback.html',
        feedbacks=feedbacks
    )


# ---------------- DELETE FEEDBACK ----------------

@app.route('/delete_feedback/<int:feedback_id>')
def delete_feedback(feedback_id):

    if session.get('admin_logged_in') != True:
        return redirect('/admin_login')

    conn = sqlite3.connect('feedback.db')

    cursor = conn.cursor()

    cursor.execute(
        'DELETE FROM feedback WHERE id = ?',
        (feedback_id,)
    )

    conn.commit()
    conn.close()

    return redirect('/view_feedback')


# ---------------- LOGOUT ----------------

@app.route('/logout')
def logout():

    session.clear()

    return redirect('/')


# ---------------- RUN APPLICATION ----------------

if __name__ == '__main__':
    app.run(debug=True)