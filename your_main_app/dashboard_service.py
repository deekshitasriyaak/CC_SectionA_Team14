from flask import Blueprint, render_template, request, redirect, session, url_for, current_app, abort, send_from_directory
from models import db, Student, Teacher, Subject, Timetable, Attendance, Feedback, Notice
dashboard_service = Blueprint('dashboard_service', __name__, url_prefix='/dashboard')

# Add this route to your dashboard_service.py

from models import AcceptedFaculty
from flask import render_template, flash, redirect, url_for, send_file
import os

# Define absolute upload folder path
BASE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
UPLOAD_FOLDER = 'uploads' 

@dashboard_service.route('/admin/accepted_faculty')

def accepted_faculty():
    faculty = AcceptedFaculty.query.order_by(AcceptedFaculty.imported_on.desc()).all()
    return render_template('admin/accepted_faculty.html', faculty=faculty)

@dashboard_service.route('/admin/faculty/<int:id>')

def view_faculty_details(id):
    faculty = AcceptedFaculty.query.get_or_404(id)
    return render_template('view_faculty_details.html', faculty=faculty)

from flask import send_from_directory

@dashboard_service.route('/admin/faculty/resume/<path:filename>')
def download_faculty_resume(filename):
    # Construct the full file path
    file_path = os.path.join(current_app.config['UPLOAD_FOLDER'], filename)
    
    # Check if the file exists
    if not os.path.exists(file_path):
        abort(404, description="File not found")
    
    # Serve the file securely
    return send_from_directory(
        current_app.config['UPLOAD_FOLDER'],
        filename,
        as_attachment=True
    )

@dashboard_service.route('/admin')
def admin_dashboard():
    if session.get('role') != 'admin':
        return redirect(url_for('auth_service.home'))

    # Fetch all students, teachers, and subjects
    students = Student.query.all()
    teachers = Teacher.query.all()
    subjects = Subject.query.all()
    pending_feedback_count = Feedback.query.filter_by(status='Pending').count() or 0
    timetable_entries = Timetable.query.all()
    recent_notices = Notice.query.order_by(Notice.timestamp.desc()).limit(3).all()

    # Timetable logic
    timetables_by_year = {}
    for entry in timetable_entries:
        year = entry.year
        day = entry.day
        period = entry.period
        subject = Subject.query.get(entry.subject_id)
        teacher = Teacher.query.get(entry.teacher_id)
        if year not in timetables_by_year:
            timetables_by_year[year] = [[None for _ in range(6)] for _ in range(6)]
        timetables_by_year[year][day][period] = {
            "subject": subject.subject_name if subject else "N/A",
            "teacher": teacher.teacher_name if teacher else "N/A"
        }

    # 🔥 Add this:
    faculty = AcceptedFaculty.query.order_by(AcceptedFaculty.imported_on.desc()).all()

    return render_template(
        'admin_dashboard.html',
        students=students,
        teachers=teachers,
        subjects=subjects,
        pending_feedback_count=pending_feedback_count,
        timetables_by_year=timetables_by_year,
        recent_notices=recent_notices,
        faculty=faculty  # 👈 passed to template
    )

        
    return render_template('faculty_details.html', faculty=faculty)
def get_teacher_timetable(teacher_id):
    """Get timetable data for a specific teacher"""
    from models import db, Teacher, Subject, Timetable
    
    # Get the teacher
    teacher = Teacher.query.get(teacher_id)
    
    # IMPORTANT: Query timetable entries directly by teacher_id instead of subject_ids
    timetable_entries = Timetable.query.filter_by(teacher_id=teacher_id).all()
    
    # Organize timetable into a 6x6 grid (6 days x 6 periods)
    timetable_data = [[None for _ in range(6)] for _ in range(6)]
    for entry in timetable_entries:
        day = entry.day
        period = entry.period
        
        # Fetch subject details
        subject = Subject.query.get(entry.subject_id)
        
        timetable_data[day][period] = {
            "subject": subject.subject_name if subject else "N/A",
            "year": subject.subject_year if subject else "N/A",
            "subject_id": subject.subject_id if subject else None
        }
    
    return timetable_data

def get_student_timetable(student_year):
    """Get timetable data for a specific student year"""
    from models import db, Student, Subject, Teacher, Timetable
    
    # Get timetable entries for the student's year
    timetable_entries = Timetable.query.filter_by(year=student_year).all()
    
    # Organize timetable into a 6x6 grid (6 days x 6 periods)
    timetable_data = [[None for _ in range(6)] for _ in range(6)]
    for entry in timetable_entries:
        day = entry.day
        period = entry.period
        
        # Fetch subject and teacher details
        subject = Subject.query.get(entry.subject_id)
        teacher = Teacher.query.get(entry.teacher_id)
        
        timetable_data[day][period] = {
            "subject": subject.subject_name if subject else "N/A",
            "teacher": teacher.teacher_name if teacher else "N/A",
            "subject_id": subject.subject_id if subject else None
        }
    
    return timetable_data
@dashboard_service.route('/teacher')
def teacher_dashboard():
    if session.get('role') != 'teacher':
        return redirect(url_for('auth_service.home'))

    # Get the logged-in teacher
    teacher = Teacher.query.filter_by(teacher_user_id=session.get('user_id')).first()

    # Get subjects taught by the teacher
    subjects = Subject.query.filter_by(teacher_id=teacher.teacher_id).all()

    # Get timetable data using the utility function
    timetable_data = get_teacher_timetable(teacher.teacher_id)

    # Fetch students for each subject
    subject_students = {}
    for subject in subjects:
        students = Student.query.filter_by(student_year=subject.subject_year).all()
        subject_students[subject.subject_name] = students

    # Fetch recent notices
    recent_notices = Notice.query.order_by(Notice.timestamp.desc()).limit(5).all()

    # Get feedback responses
    feedback_responses = Feedback.query.filter_by(
        teacher_id=teacher.teacher_id,
        user_role='teacher'
    ).filter(Feedback.admin_response != None).order_by(Feedback.feedback_date.desc()).limit(3).all()

    return render_template(
        'teacher_dashboard.html',
        teacher=teacher,
        subjects=subjects,
        timetable=timetable_data,
        subject_students=subject_students,
        recent_notices=recent_notices,
        feedback_responses=feedback_responses
    )

@dashboard_service.route('/student')
def student_dashboard():
    if session.get('role') != 'student':
        return redirect(url_for('auth_service.home'))

    # Get the logged-in student
    student = Student.query.filter_by(student_user_id=session.get('user_id')).first()

    # Get subjects based on the student's year
    subjects = Subject.query.filter_by(subject_year=student.student_year).all()

    # Calculate attendance summary for each subject
    attendance_summary = []
    for subject in subjects:
        # Count total marked classes for the subject
        total_marked_classes = Attendance.query.filter_by(
            student_id=student.student_id,
            subject_id=subject.subject_id
        ).count()

        # Count present classes for the subject
        present_classes = Attendance.query.filter_by(
            student_id=student.student_id,
            subject_id=subject.subject_id,
            status="Present"
        ).count()

        attendance_summary.append({
            "subject_name": subject.subject_name,
            "present_classes": present_classes,
            "total_marked_classes": total_marked_classes
        })

    # Get timetable data using the utility function
    timetable_data = get_student_timetable(student.student_year)

    # Fetch recent notices
    recent_notices = Notice.query.order_by(Notice.timestamp.desc()).limit(5).all()

    # Get feedback responses
    feedback_responses = Feedback.query.filter_by(
        student_id=student.student_id,
        user_role='student'
    ).filter(Feedback.admin_response != None).order_by(Feedback.feedback_date.desc()).limit(3).all()

    return render_template(
        'student_dashboard.html',
        student=student,
        subjects=subjects,
        timetable=timetable_data,
        attendance_summary=attendance_summary,
        recent_notices=recent_notices,
        feedback_responses=feedback_responses
    )

# In your_main_app/app.py or dashboard_service.py


