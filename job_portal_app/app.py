from flask import Flask, render_template, request, redirect, url_for, flash, send_from_directory
from flask_mysqldb import MySQL
from flask_login import LoginManager, UserMixin, login_user, logout_user, login_required
from werkzeug.utils import secure_filename
from datetime import datetime
import os

app = Flask(__name__)
app.secret_key = 'cloudcomputing'

# MySQL Config
app.config['MYSQL_HOST'] = 'db' 
app.config['MYSQL_USER'] = 'root'
app.config['MYSQL_PASSWORD'] = 'chandu@123S'
app.config['MYSQL_DB'] = 'job_portal'


# Add these imports at the top of your app.py file
import pymysql
import os

# Replace the existing PyMySQL connection setup with this function-based approach
def get_job_db_connection():
    return pymysql.connect(
        host=os.getenv("JOB_DB_HOST", "job_db"),
        user=os.getenv("JOB_DB_USER", "root"),
        password=os.getenv("JOB_DB_PASSWORD", "chandu@123S"),
        db=os.getenv("JOB_DB_NAME", "job_portal"),
        cursorclass=pymysql.cursors.DictCursor
    )

def get_school_db_connection():
    return pymysql.connect(
        host=os.getenv("SCHOOL_DB_HOST", "school"),
        user=os.getenv("SCHOOL_DB_USER", "root"),
        password=os.getenv("SCHOOL_DB_PASSWORD", "password"),
        db=os.getenv("SCHOOL_DB_NAME", "school"),
        cursorclass=pymysql.cursors.DictCursor
    )

# Replace the existing connection objects with function calls when needed
# Example: Instead of using job_conn, use get_job_db_connection()
UPLOAD_FOLDER = 'uploads'
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

mysql = MySQL(app)

# Admin login setup
login_manager = LoginManager()
login_manager.init_app(app)

class Admin(UserMixin):
    def __init__(self, id):
        self.id = id

@login_manager.user_loader
def load_user(user_id):
    return Admin(user_id)

@app.route('/')
def home():
    return render_template('home.html')

@app.route('/user')
def user_dashboard():
    return render_template('user_dashboard.html')

@app.route('/apply')
def apply():
    cur = mysql.connection.cursor()
    cur.execute("SELECT id, title FROM jobs")
    jobs = cur.fetchall()
    cur.close()
    return render_template('apply.html', jobs=jobs)

@app.route('/submit_application', methods=['POST'])
def submit_application():
    data = request.form
    resume = request.files['resume']
    job_id = request.form['job_id']
    filename = secure_filename(resume.filename)
    filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
    resume.save(filepath)

    status = 'Pending'
    experience = int(data['experience'])
    if experience >= 3 and any(kw in data['skills'].lower() for kw in ['phd', 'ai', 'machine learning']):
        status = 'Accepted'

    cur = mysql.connection.cursor()
    cur.execute("""
        INSERT INTO candidates (name, email, phone, resume, skills, experience, status, applied_on, job_id)
        VALUES (%s, %s, %s, %s, %s, %s, %s, NOW(), %s)
    """, (data['name'], data['email'], data['phone'], filepath, data['skills'], data['experience'], status, job_id))
    mysql.connection.commit()
    cur.close()

    flash("Application submitted successfully!", "success")
    return redirect(url_for('apply'))

@app.route('/admin', methods=['GET', 'POST'])
def admin_login():
    if request.method == 'POST':
        if request.form['username'] == 'admin' and request.form['password'] == 'admin123':
            login_user(Admin(1))
            return redirect(url_for('admin_dashboard'))
        flash("Invalid credentials!", "danger")
    return render_template('admin_login.html')

@app.route('/admin_dashboard')
def admin_dashboard():
    cur = mysql.connection.cursor()

    # Fetch candidates with job titles
    cur.execute("""
        SELECT c.id, c.name, c.skills, c.experience, c.resume, c.status, j.title 
        FROM candidates c 
        LEFT JOIN jobs j ON c.job_id = j.id
    """)
    candidates = cur.fetchall()

    # Application status count
    cur.execute("SELECT status, COUNT(*) FROM candidates GROUP BY status")
    stats = cur.fetchall()

    # Applications per job/subject
    cur.execute("""
        SELECT j.title, COUNT(*) 
        FROM candidates c 
        LEFT JOIN jobs j ON c.job_id = j.id 
        GROUP BY j.title
    """)
    applications_per_job = cur.fetchall()

    cur.close()

    return render_template(
        'dashboard.html',
        candidates=candidates,
        stats=stats,
        applications_per_job=applications_per_job
    )

@app.route('/update_status/<int:id>/<string:status>')
def update_status(id, status):
    cur = mysql.connection.cursor()
    cur.execute("UPDATE candidates SET status = %s WHERE id = %s", (status, id))
    mysql.connection.commit()
    cur.close()
    
    # If status is Accepted, notify main app
    if status == 'Accepted':
        notify_main_app(id)
        
    flash(f"Candidate has been {status} ", "info")
    return redirect(url_for('admin_dashboard'))

@app.route('/schedule_interview/<int:candidate_id>', methods=['GET', 'POST'])
def schedule_interview(candidate_id):
    if request.method == 'POST':
        interview_date_str = request.form['interview_date']
        panel = request.form['panel']
        link = request.form['link']
        message = request.form['message']

        # Convert string to datetime object for the 'interview_date' column
        interview_datetime = datetime.strptime(interview_date_str, '%Y-%m-%dT%H:%M')

        cursor = mysql.connection.cursor()
        cursor.execute("SELECT * FROM interviews WHERE candidate_id=%s", [candidate_id])
        existing = cursor.fetchone()

        if existing:
            cursor.execute("""
                UPDATE interviews 
                SET date=%s, interview_date=%s, panel=%s, link=%s, message=%s 
                WHERE candidate_id=%s
            """, (interview_date_str, interview_datetime, panel, link, message, candidate_id))
        else:
            cursor.execute("""
                INSERT INTO interviews (candidate_id, date, interview_date, panel, link, message) 
                VALUES (%s, %s, %s, %s, %s, %s)
            """, (candidate_id, interview_date_str, interview_datetime, panel, link, message))

        mysql.connection.commit()
        cursor.close()
        flash('Interview scheduled successfully!', 'success')
        return redirect(url_for('admin_dashboard'))

    cursor = mysql.connection.cursor()
    cursor.execute("SELECT * FROM candidates WHERE id=%s", (candidate_id,))
    candidate = cursor.fetchone()
    cursor.close()
    return render_template('schedule_interview.html', candidate=candidate)

@app.route('/view_resume/<path:filename>')
def view_resume(filename):
    return send_from_directory(app.config['UPLOAD_FOLDER'], filename)

@app.route('/check_status', methods=['GET', 'POST'])
def check_status():
    if request.method == 'POST':
        email = request.form['email']
        cur = mysql.connection.cursor()
        cur.execute("SELECT id, name, status FROM candidates WHERE email=%s", [email])
        candidate = cur.fetchone()

        name = None
        status = None
        interview_date_str = None
        interview_panel = None
        interview_link = None
        interview_message = None

        if candidate:
            candidate_id, name, status = candidate

            cur.execute("""SELECT interview_date, panel, link, message 
                   FROM interviews WHERE candidate_id = %s""", [candidate_id]) 
            interview = cur.fetchone()

            if interview:
                interview_date, interview_panel, interview_link, interview_message = interview

        # Format date safely
                try:
                    interview_date_str = interview_date.strftime('%d %B %Y, %I:%M %p')
                except (AttributeError, TypeError):
                    interview_date_str = "No interview scheduled"

                interview_panel = interview_panel or "No panel assigned"
                interview_link = interview_link or "No link provided"
                interview_message = interview_message or "No message provided"


@app.route('/logout')
def logout():
    logout_user()
    return redirect(url_for('admin_login'))

from flask import jsonify, request
from datetime import datetime

# --- JOB LISTINGS ---
@app.route('/api/jobs', methods=['GET'])
def get_jobs():
    cur = mysql.connection.cursor()
    cur.execute("SELECT id, title FROM jobs")
    jobs = cur.fetchall()
    cur.close()
    return jsonify([{'id': j[0], 'title': j[1]} for j in jobs])


# --- APPLY FOR JOB ---
@app.route('/api/candidates/apply', methods=['POST'])
def api_apply():
    data = request.form
    resume = request.files['resume']
    filename = secure_filename(resume.filename)
    filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
    resume.save(filepath)

    experience = int(data['experience'])
    status = 'Accepted' if experience >= 3 and any(kw in data['skills'].lower() for kw in ['phd', 'ai', 'machine learning']) else 'Pending'

    cur = mysql.connection.cursor()
    cur.execute("""
        INSERT INTO candidates (name, email, phone, resume, skills, experience, status, applied_on, job_id)
        VALUES (%s, %s, %s, %s, %s, %s, %s, NOW(), %s)
    """, (data['name'], data['email'], data['phone'], filepath, data['skills'], experience, status, data['job_id']))
    mysql.connection.commit()
    cur.close()

    return jsonify({'message': 'Application submitted successfully', 'status': status})


# --- GET CANDIDATE INFO ---
@app.route('/api/candidates/<int:id>', methods=['GET'])
def get_candidate(id):
    cur = mysql.connection.cursor()
    cur.execute("""
        SELECT c.name, c.skills, c.status, j.title 
        FROM candidates c 
        LEFT JOIN jobs j ON c.job_id = j.id 
        WHERE c.id = %s
    """, (id,))
    result = cur.fetchone()
    cur.close()
    if result:
        name, skills, status, job_title = result
        return jsonify({'name': name, 'skills': skills, 'status': status, 'job_title': job_title})
    return jsonify({'error': 'Candidate not found'}), 404


# --- UPDATE STATUS ---
@app.route('/api/candidates/<int:id>/status', methods=['PUT'])
def update_candidate_status(id):
    status = request.json.get('status')
    cur = mysql.connection.cursor()
    cur.execute("UPDATE candidates SET status = %s WHERE id = %s", (status, id))
    mysql.connection.commit()
    cur.close()
    
    # If status is Accepted, notify main app
    if status == 'Accepted':
        success = notify_main_app(id)
        if success:
            return jsonify({'message': f'Status updated to {status} and synced with main app'})
    
    return jsonify({'message': f'Status updated to {status}'})
# --- SCHEDULE INTERVIEW ---
@app.route('/api/interviews/<int:candidate_id>', methods=['POST'])
def schedule(candidate_id):
    data = request.json
    interview_date = datetime.strptime(data['interview_date'], '%Y-%m-%dT%H:%M')
    panel = data['panel']
    link = data['link']
    message = data['message']

    cur = mysql.connection.cursor()
    cur.execute("SELECT id FROM interviews WHERE candidate_id = %s", (candidate_id,))
    exists = cur.fetchone()

    if exists:
        cur.execute("""UPDATE interviews SET date=%s, interview_date=%s, panel=%s, link=%s, message=%s 
                       WHERE candidate_id=%s""",
                       (data['interview_date'], interview_date, panel, link, message, candidate_id))
    else:
        cur.execute("""INSERT INTO interviews (candidate_id, date, interview_date, panel, link, message)
                       VALUES (%s, %s, %s, %s, %s, %s)""",
                       (candidate_id, data['interview_date'], interview_date, panel, link, message))
    mysql.connection.commit()
    cur.close()
    return jsonify({'message': 'Interview scheduled successfully'})


# --- CHECK STATUS ---
@app.route('/api/status/<email>', methods=['GET'])
def check_app_status(email):
    cur = mysql.connection.cursor()
    cur.execute("SELECT id, name, status FROM candidates WHERE email=%s", [email])
    candidate = cur.fetchone()

    if not candidate:
        return jsonify({'error': 'Candidate not found'}), 404

    candidate_id, name, status = candidate
    cur.execute("SELECT interview_date, panel, link, message FROM interviews WHERE candidate_id=%s", [candidate_id])
    interview = cur.fetchone()
    cur.close()

    interview_data = None
    if interview:
        try:
            interview_data = {
                'interview_date': interview[0].strftime('%Y-%m-%d %H:%M'),
                'panel': interview[1],
                'link': interview[2],
                'message': interview[3]
            }
        except:
            interview_data = {}

    return jsonify({
        'name': name,
        'status': status,
        'interview': interview_data
    })


# --- GET RESUME FILE ---
@app.route('/api/resume/<path:filename>', methods=['GET'])
def download_resume(filename):
    return send_from_directory(app.config['UPLOAD_FOLDER'], filename)



@app.route("/accept_faculty/<int:faculty_id>", methods=["POST"])
def accept_faculty(faculty_id):
    with job_conn.cursor() as cur:
        cur.execute("SELECT * FROM faculty WHERE id = %s", (faculty_id,))
        faculty = cur.fetchone()

    if not faculty:
        return jsonify({"error": "Faculty not found"}), 404

    # Mark as accepted
    with job_conn.cursor() as cur:
        cur.execute("UPDATE faculty SET status='accepted' WHERE id=%s", (faculty_id,))
        job_conn.commit()

    # Insert into school DB
    with school_conn.cursor() as cur:
        cur.execute("""
            INSERT INTO teachers (name, email, subject)
            VALUES (%s, %s, %s)
        """, (faculty["name"], faculty["email"], faculty["subject"]))

        school_conn.commit()

@app.route("/applicants/<int:applicant_id>", methods=["PUT"])
def update_applicant(applicant_id):
    applicant = Applicant.query.get_or_404(applicant_id)

    # Update status and other fields based on request
    applicant.status = request.json.get('status', applicant.status)
    
    db.session.commit()

    # If the applicant's status is accepted, notify the admin dashboard
    if applicant.status == 'accepted':
        notify_admin_dashboard(applicant)

    return jsonify({'message': 'Applicant status updated successfully', 'applicant': applicant.to_dict()}), 200


    return jsonify({"message": "Faculty accepted and added to school DB"})
# In job_portal_app/app.py - Add this function

def notify_main_app(candidate_id):
    """Notify the main app when a candidate is accepted by adding them to the school database"""
    try:
        with get_job_db_connection() as job_conn:
            with job_conn.cursor() as job_cur:
                job_cur.execute("""
                    SELECT c.id, c.name, c.email, c.phone, c.resume, c.skills, c.experience, 
                           j.title as subject, i.interview_date 
                    FROM candidates c
                    LEFT JOIN jobs j ON c.job_id = j.id
                    LEFT JOIN interviews i ON c.id = i.candidate_id
                    WHERE c.id = %s AND c.status = 'Accepted'
                """, [candidate_id])
                candidate = job_cur.fetchone()
                
        if not candidate:
            print(f"Candidate {candidate_id} not found or not accepted")
            return False
            
        # Connect to school database and insert the candidate
        with get_school_db_connection() as school_conn:
            with school_conn.cursor() as school_cur:
                school_cur.execute("""
                    INSERT INTO accepted_faculty 
                    (original_id, name, email, phone, skills, experience, subject, resume_path, interview_date)
                    VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
                """, (
                    candidate['id'],
                    candidate['name'],
                    candidate['email'],
                    candidate['phone'],
                    candidate['skills'],
                    candidate['experience'],
                    candidate['subject'],
                    candidate['resume'],
                    candidate['interview_date']
                ))
                school_conn.commit()
                
        print(f"Successfully synced candidate {candidate_id} to main app")
        return True
    except Exception as e:
        print(f"Error syncing with main app: {e}")
        return False
if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0',port=5000)