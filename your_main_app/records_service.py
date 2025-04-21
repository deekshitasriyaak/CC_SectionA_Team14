from flask import Blueprint, render_template, request, redirect, session, url_for
from models import db, Student, Teacher, Subject, User
from timetable_service import get_student_timetable
records_service = Blueprint('records_service', __name__, url_prefix='/records')

@records_service.route('/admin/dashboard')
def admin_dashboard():
    if session.get('role') != 'admin':
        return redirect(url_for('auth_service.home'))

    # Fetch all students, teachers, and subjects
    students = Student.query.all()
    teachers = Teacher.query.all()
    subjects = Subject.query.all()

    return render_template(
        'admin_dashboard.html',
        students=students,
        teachers=teachers,
        subjects=subjects
    )