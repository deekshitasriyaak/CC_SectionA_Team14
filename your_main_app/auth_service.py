from flask import Blueprint, render_template, request, redirect, session, url_for
from models import User

auth_service = Blueprint('auth_service', __name__, url_prefix='/auth')

@auth_service.route('/')
def home():
    return render_template('login.html')

@auth_service.route('/login', methods=['POST'])
def login():
    username = request.form['username']
    password = request.form['password']

    user = User.query.filter_by(username=username, password=password).first()
    if user:
        session['user_id'] = user.user_id
        session['role'] = user.role

        if user.role == 'admin':
            return redirect(url_for('dashboard_service.admin_dashboard'))
        elif user.role == 'teacher':
            return redirect(url_for('dashboard_service.teacher_dashboard'))
        elif user.role == 'student':
            return redirect(url_for('dashboard_service.student_dashboard'))

    return 'Invalid credentials'

@auth_service.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('auth_service.home'))