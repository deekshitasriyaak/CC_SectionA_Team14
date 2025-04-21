from flask_sqlalchemy import SQLAlchemy
from datetime import datetime

db = SQLAlchemy()

class User(db.Model):
    user_id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(50), unique=True, nullable=False)
    password = db.Column(db.String(100), nullable=False)
    role = db.Column(db.String(20), nullable=False)

class Student(db.Model):
    student_id = db.Column(db.Integer, primary_key=True)
    student_name = db.Column(db.String(100), nullable=False)
    student_year = db.Column(db.Integer, nullable=False)
    student_user_id = db.Column(db.Integer, db.ForeignKey('user.user_id'), nullable=False)
    
    # Relationship with feedback
    feedbacks = db.relationship('Feedback', backref='student', lazy=True, foreign_keys='Feedback.student_id')

class Teacher(db.Model):
    teacher_id = db.Column(db.Integer, primary_key=True)
    teacher_name = db.Column(db.String(100), nullable=False)
    teacher_user_id = db.Column(db.Integer, db.ForeignKey('user.user_id'), nullable=False)

    # One teacher can have many subjects
    subjects = db.relationship('Subject', backref='teacher', lazy=True)
    
    # Relationship with feedback
    feedbacks = db.relationship('Feedback', backref='teacher', lazy=True, foreign_keys='Feedback.teacher_id')

class Subject(db.Model):
    subject_id = db.Column(db.Integer, primary_key=True)
    subject_name = db.Column(db.String(100), nullable=False)
    subject_year = db.Column(db.Integer, nullable=False)

    # Foreign key to Teacher
    teacher_id = db.Column(db.Integer, db.ForeignKey('teacher.teacher_id'), nullable=False)

class Timetable(db.Model):
    timetable_id = db.Column(db.Integer, primary_key=True)
    day = db.Column(db.Integer)
    period = db.Column(db.Integer)
    subject_id = db.Column(db.Integer, db.ForeignKey('subject.subject_id'))
    teacher_id = db.Column(db.Integer, db.ForeignKey('teacher.teacher_id'))
    year = db.Column(db.Integer)

class Attendance(db.Model):
    attendance_id = db.Column(db.Integer, primary_key=True)
    student_id = db.Column(db.Integer, db.ForeignKey('student.student_id'), nullable=False)
    subject_id = db.Column(db.Integer, db.ForeignKey('subject.subject_id'), nullable=False)
    date = db.Column(db.Date, nullable=False)  # Date of the class
    status = db.Column(db.String(10), nullable=False)  # 'Present' or 'Absent'

class Feedback(db.Model):
    feedback_id = db.Column(db.Integer, primary_key=True)
    feedback_text = db.Column(db.Text, nullable=False)
    feedback_date = db.Column(db.DateTime, default=datetime.utcnow)
    status = db.Column(db.String(20), default='Pending')  # Pending, Reviewed, Resolved
    admin_response = db.Column(db.Text, nullable=True)  # Optional admin response
    
    # User type and ID
    user_role = db.Column(db.String(20), nullable=False)  # 'student' or 'teacher'
    
    # Foreign keys - only one will be used based on user_role
    student_id = db.Column(db.Integer, db.ForeignKey('student.student_id'), nullable=True)
    teacher_id = db.Column(db.Integer, db.ForeignKey('teacher.teacher_id'), nullable=True)

class Notice(db.Model):
    notice_id = db.Column(db.Integer, primary_key=True)  # Auto-incrementing primary key
    title = db.Column(db.String(200), nullable=False)  # Title of the notice
    content = db.Column(db.Text, nullable=False)  # Content of the notice
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)  # Timestamp of notice creation

# Add this class to your models.py file

class AcceptedFaculty(db.Model):
    __tablename__ = 'accepted_faculty'
    
    id = db.Column(db.Integer, primary_key=True)
    original_id = db.Column(db.Integer, nullable=False)
    name = db.Column(db.String(255), nullable=False)
    email = db.Column(db.String(255), nullable=False)
    phone = db.Column(db.String(20))
    skills = db.Column(db.Text)
    experience = db.Column(db.Integer)
    subject = db.Column(db.String(255))
    resume_path = db.Column(db.String(512))
    interview_date = db.Column(db.DateTime)
    imported_on = db.Column(db.DateTime, default=datetime.utcnow)
    
    def __repr__(self):
        return f'<AcceptedFaculty {self.name}>'
