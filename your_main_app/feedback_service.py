from flask import Blueprint, render_template, request, redirect, session, url_for, flash
from models import db, Student, Teacher, Feedback
from datetime import datetime

feedback_service = Blueprint('feedback_service', __name__, url_prefix='/feedback')

@feedback_service.route('/submit', methods=['GET', 'POST'])
def submit_feedback():
    user_id = session.get('user_id')
    role = session.get('role')
    
    if not user_id or role not in ['student', 'teacher']:
        return redirect(url_for('auth_service.home'))
    
    # Get the user based on role
    if role == 'student':
        user = Student.query.filter_by(student_user_id=user_id).first()
        user_id_field = user.student_id
        user_name = user.student_name
    else:  # role == 'teacher'
        user = Teacher.query.filter_by(teacher_user_id=user_id).first()
        user_id_field = user.teacher_id
        user_name = user.teacher_name
    
    if request.method == 'POST':
        feedback_text = request.form.get('feedback_text')
        
        if feedback_text:
            # Create new feedback
            new_feedback = Feedback(
                feedback_text=feedback_text,
                feedback_date=datetime.utcnow(),
                status='Pending',
                user_role=role
            )
            
            # Set the appropriate ID based on role
            if role == 'student':
                new_feedback.student_id = user_id_field
            else:  # role == 'teacher'
                new_feedback.teacher_id = user_id_field
                
            db.session.add(new_feedback)
            db.session.commit()
            
            flash('Your feedback has been submitted successfully!', 'success')
            
            # Redirect based on role
            if role == 'student':
                return redirect(url_for('dashboard_service.student_dashboard'))
            else:  # role == 'teacher'
                return redirect(url_for('dashboard_service.teacher_dashboard'))
        else:
            flash('Feedback cannot be empty!', 'error')
    
    # Get existing feedback from this user
    if role == 'student':
        previous_feedbacks = Feedback.query.filter_by(student_id=user_id_field).order_by(Feedback.feedback_date.desc()).all()
    else:  # role == 'teacher'
        previous_feedbacks = Feedback.query.filter_by(teacher_id=user_id_field).order_by(Feedback.feedback_date.desc()).all()
    
    return render_template(
        'feedback_form.html',
        user_name=user_name,
        role=role,
        previous_feedbacks=previous_feedbacks
    )

@feedback_service.route('/admin/view')
def admin_view_feedback():
    if session.get('role') != 'admin':
        return redirect(url_for('auth_service.home'))
    
    # Get all feedback with user info
    student_feedback = db.session.query(
        Feedback, Student.student_name
    ).join(
        Student, Feedback.student_id == Student.student_id
    ).filter(
        Feedback.user_role == 'student'
    ).all()
    
    teacher_feedback = db.session.query(
        Feedback, Teacher.teacher_name
    ).join(
        Teacher, Feedback.teacher_id == Teacher.teacher_id
    ).filter(
        Feedback.user_role == 'teacher'
    ).all()
    
    # Format data for template
    student_feedback_data = [(f, name, 'Student') for f, name in student_feedback]
    teacher_feedback_data = [(f, name, 'Teacher') for f, name in teacher_feedback]
    
    # Combine and sort by date
    all_feedback = student_feedback_data + teacher_feedback_data
    all_feedback.sort(key=lambda x: x[0].feedback_date, reverse=True)
    


    
    return render_template(
        'admin_feedback.html',
        all_feedback=all_feedback
    )

@feedback_service.route('/admin/respond/<int:feedback_id>', methods=['POST'])
def admin_respond_feedback(feedback_id):
    if session.get('role') != 'admin':
        return redirect(url_for('auth_service.home'))
    
    feedback = Feedback.query.get_or_404(feedback_id)
    response = request.form.get('admin_response')
    status = request.form.get('status')
    
    if response:
        feedback.admin_response = response
    
    if status:
        feedback.status = status
    
    db.session.commit()
    flash('Response submitted successfully!', 'success')
    return redirect(url_for('feedback_service.admin_view_feedback'))