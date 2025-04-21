from flask import Blueprint, render_template, request, redirect, session, url_for
from models import db, Student, Teacher, Subject, Attendance
from datetime import datetime, timedelta

attendance_service = Blueprint('attendance_service', __name__, url_prefix='/attendance')

@attendance_service.route('/teacher/manage/<int:subject_id>', methods=['GET', 'POST'])
def manage_attendance(subject_id):
    if session.get('role') != 'teacher':
        return redirect(url_for('auth_service.home'))

    # Get the logged-in teacher
    teacher = Teacher.query.filter_by(teacher_user_id=session.get('user_id')).first()

    # Get the subject
    subject = Subject.query.get(subject_id)
    if not subject or subject.teacher_id != teacher.teacher_id:
        return "Unauthorized", 403

    # Generate class dates for the year (assuming 10 weeks, 6 days/week)
    start_date = datetime(2023, 1, 1)  # Example start date
    class_dates = [start_date + timedelta(days=i) for i in range(10 * 6)]  # 10 weeks, 6 days/week

    # Fetch students for the subject's year
    students = Student.query.filter_by(student_year=subject.subject_year).all()

    if request.method == 'POST':
        # Process attendance submission
        date_str = request.form.get('date')
        date = datetime.strptime(date_str, '%Y-%m-%d').date()

        for student in students:
            status_key = f'student{student.student_id}'  # Match the name attribute in the form
            status = request.form.get(status_key)
            attendance_record = Attendance.query.filter_by(
                student_id=student.student_id,
                subject_id=subject_id,
                date=date
            ).first()

            if attendance_record:
                # Update existing record
                attendance_record.status = status
            else:
                # Create new record
                new_attendance = Attendance(
                    student_id=student.student_id,
                    subject_id=subject_id,
                    date=date,
                    status=status
                )
                db.session.add(new_attendance)

        db.session.commit()
        return redirect(url_for('attendance_service.manage_attendance', subject_id=subject_id))

    return render_template(
        'attendance_management.html',
        teacher=teacher,
        subject=subject,
        class_dates=class_dates,
        students=students
    )

@attendance_service.route('/student/view')
def student_attendance_summary():
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

    return render_template(
        'student_attendance_summary.html',
        student=student,
        attendance_summary=attendance_summary
    )

@attendance_service.route('/student/view/<string:subject_name>')
def student_view_attendance(subject_name):
    if session.get('role') != 'student':
        return redirect(url_for('auth_service.home'))

    # Get the logged-in student
    student = Student.query.filter_by(student_user_id=session.get('user_id')).first()

    # Get the subject
    subject = Subject.query.filter_by(subject_name=subject_name).first()
    if not subject:
        return "Subject not found", 404

    # Fetch attendance records for the student and subject
    attendance_records = Attendance.query.filter_by(
        student_id=student.student_id,
        subject_id=subject.subject_id
    ).order_by(Attendance.date).all()

    return render_template(
        'student_attendance_detail.html',
        student=student,
        subject=subject,
        attendance_records=attendance_records
    )

@attendance_service.route('/teacher/subjects')
def teacher_subjects():
    if session.get('role') != 'teacher':
        return redirect(url_for('auth_service.home'))

    # Get the logged-in teacher
    teacher = Teacher.query.filter_by(teacher_user_id=session.get('user_id')).first()

    # Get subjects taught by the teacher
    subjects = Subject.query.filter_by(teacher_id=teacher.teacher_id).all()

    # Fetch students for each subject
    subject_students = {}
    for subject in subjects:
        students = Student.query.filter_by(student_year=subject.subject_year).all()
        subject_students[subject.subject_name] = students

    return render_template(
        'teacher_subjects.html',
        teacher=teacher,
        subjects=subjects,
        subject_students=subject_students
    )