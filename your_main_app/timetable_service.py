from flask import Blueprint, render_template, request, redirect, session, url_for, flash
from models import db, Student, Teacher, Subject, Timetable
import random

timetable_service = Blueprint('timetable_service', __name__, url_prefix='/timetable')

# Adapted timetable generation function
def generate_timetable(year):
    # Fetch subjects for the given year
    subjects = Subject.query.filter_by(subject_year=year).all()
    
    # Create a list of subject-teacher pairs
    teaching_assignments = []
    for subject in subjects:
        teacher = Teacher.query.get(subject.teacher_id)
        teaching_assignments.append({
            "teacher_id": teacher.teacher_id,
            "teacher_name": teacher.teacher_name,
            "subject_id": subject.subject_id,
            "subject_name": subject.subject_name
        })
    
    # Initialize a 6x6 timetable grid
    timetable = [[None for _ in range(6)] for _ in range(6)]
    
    # Ensure each subject gets some slots in the timetable
    # First, assign at least one slot to each subject
    for assignment in teaching_assignments:
        assigned = False
        for day in range(6):
            for period in range(6):
                if not timetable[day][period]:
                    timetable[day][period] = {
                        "subject_id": assignment["subject_id"],
                        "teacher_id": assignment["teacher_id"]
                    }
                    assigned = True
                    break
            if assigned:
                break
    
    # Fill remaining slots randomly
    for day in range(6):
        for period in range(6):
            if not timetable[day][period]:
                # Pick a random subject-teacher pair
                if teaching_assignments:
                    random_assignment = random.choice(teaching_assignments)
                    timetable[day][period] = {
                        "subject_id": random_assignment["subject_id"],
                        "teacher_id": random_assignment["teacher_id"]
                    }
    
    # Save the generated timetable to the database
    for day, periods in enumerate(timetable):
        for period, entry in enumerate(periods):
            if entry:
                new_entry = Timetable(
                    day=day,
                    period=period,
                    subject_id=entry["subject_id"],
                    teacher_id=entry["teacher_id"],
                    year=year
                )
                db.session.add(new_entry)
    db.session.commit()
# Create these utility functions in a new file (e.g., timetable_utils.py)

def get_teacher_timetable(teacher_id):
    """Get timetable data for a specific teacher"""
    from models import db, Teacher, Subject, Timetable
    
    # Get the teacher and subjects they teach
    teacher = Teacher.query.get(teacher_id)
    subjects = Subject.query.filter_by(teacher_id=teacher_id).all()
    
    # Extract subject IDs for querying the timetable
    subject_ids = [subject.subject_id for subject in subjects]
    
    # Get timetable entries for the teacher's subjects
    timetable_entries = Timetable.query.filter(Timetable.subject_id.in_(subject_ids)).all()
    
    # Organize timetable into a 6x6 grid (6 days x 6 periods)
    timetable_data = [[None for _ in range(6)] for _ in range(6)]
    for entry in timetable_entries:
        day = entry.day
        period = entry.period
        
        # Fetch subject details
        subject = Subject.query.get(entry.subject_id)
        
        timetable_data[day][period] = {
            "subject": subject.subject_name,
            "year": subject.subject_year,
            "subject_id": subject.subject_id
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
# Route to generate timetable
@timetable_service.route('/admin/generate', methods=['POST'])
def generate_timetable_route():
    if session.get('role') != 'admin':
        return redirect(url_for('auth_service.home'))

    # Check if timetables already exist
    existing_timetables = Timetable.query.first()
    
    if existing_timetables:
        from flask import flash
        flash('Timetable already generated!', 'info')
        # Redirect back to admin dashboard instead of timetable view
        return redirect(url_for('dashboard_service.admin_dashboard'))
    else:
        # Get all unique years from the Subject table
        years = db.session.query(Subject.subject_year).distinct().all()
        years = [year[0] for year in years]  # Extract years from tuples

        # Generate timetables for each year
        for year in years:
            generate_timetable(year)
        
        from flask import flash
        flash('Timetables successfully generated for all years.', 'success')
        # Only redirect to timetable view when new timetables are generated
        return redirect(url_for('dashboard_service.admin_dashboard'))

@timetable_service.route('/admin/view')
def admin_view_timetable():
    if session.get('role') != 'admin':
        return redirect(url_for('auth_service.home'))

    # Fetch all timetable entries
    timetable_entries = Timetable.query.all()

    # Organize timetable data by year
    timetables = {}  # Use 'timetables' to match template expectation
    for entry in timetable_entries:
        year = entry.year
        day = entry.day
        period = entry.period

        # Fetch subject and teacher details
        subject = Subject.query.get(entry.subject_id)
        teacher = Teacher.query.get(entry.teacher_id)

        if year not in timetables:
            timetables[year] = [[None for _ in range(6)] for _ in range(6)]

        timetables[year][day][period] = {
            "subject": subject.subject_name if subject else "N/A",
            "teacher": teacher.teacher_name if teacher else "N/A"
        }

    return render_template(
        'admin_timetable.html',
        timetables=timetables  # Use 'timetables' to match template expectation
    )
@timetable_service.route('/teacher/view')
def teacher_view_timetable():
    if session.get('role') != 'teacher':
        return redirect(url_for('auth_service.home'))

    # Get the logged-in teacher
    teacher = Teacher.query.filter_by(teacher_user_id=session.get('user_id')).first()
    
    # Get timetable data using the utility function
    timetable_data = get_teacher_timetable(teacher.teacher_id)

    return render_template(
        'teacher_timetable.html',
        teacher=teacher,
        timetable=timetable_data
    )

@timetable_service.route('/student/view')
def student_view_timetable():
    if session.get('role') != 'student':
        return redirect(url_for('auth_service.home'))

    # Get the logged-in student
    student = Student.query.filter_by(student_user_id=session.get('user_id')).first()
    
    # Get timetable data using the utility function
    timetable_data = get_student_timetable(student.student_year)

    return render_template(
        'student_timetable.html',
        student=student,
        timetable=timetable_data
    )