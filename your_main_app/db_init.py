from app import create_app
from models import db, User, Student, Teacher, Subject, Notice, AcceptedFaculty 
from datetime import datetime
import time

def initialize_database():
    app = create_app()
    
    with app.app_context():
        # Reset database
        db.drop_all()
        db.create_all()
        
        print("Creating sample users...")
        # Create admin user
        admin = User(username="admin", password="admin123", role="admin")
        db.session.add(admin)
        
        # Create sample teachers
        teachers_data = [
            {"username": "teacher1", "password": "pass123", "name": "John Smith"},
            {"username": "teacher2", "password": "pass123", "name": "Jane Doe"},
            {"username": "teacher3", "password": "pass123", "name": "Robert Johnson"}
        ]
        
        for t_data in teachers_data:
            user = User(username=t_data["username"], password=t_data["password"], role="teacher")
            db.session.add(user)
            db.session.flush()  # Flush to get the user_id
            
            teacher = Teacher(teacher_name=t_data["name"], teacher_user_id=user.user_id)
            db.session.add(teacher)
        
        db.session.commit()
        
        # Get all teachers
        teachers = Teacher.query.all()
        
        print("Creating sample students...")
        # Create sample students
        students_data = [
            {"username": "student1", "password": "pass123", "name": "Alice Brown", "year": 1},
            {"username": "student2", "password": "pass123", "name": "Bob Miller", "year": 1},
            {"username": "student3", "password": "pass123", "name": "Charlie Davis", "year": 2},
            {"username": "student4", "password": "pass123", "name": "Diana Wilson", "year": 2},
            {"username": "student5", "password": "pass123", "name": "Edward Thomas", "year": 3},
            {"username": "student6", "password": "pass123", "name": "Fiona Martin", "year": 3}
        ]
        
        for s_data in students_data:
            user = User(username=s_data["username"], password=s_data["password"], role="student")
            db.session.add(user)
            db.session.flush()  # Flush to get the user_id
            
            student = Student(
                student_name=s_data["name"], 
                student_year=s_data["year"], 
                student_user_id=user.user_id
            )
            db.session.add(student)
        
        db.session.commit()
        
        print("Creating sample subjects...")
        # Create sample subjects for each year
        subjects_data = [
            {"name": "Mathematics", "year": 1, "teacher_id": teachers[0].teacher_id},
            {"name": "Physics", "year": 1, "teacher_id": teachers[1].teacher_id},
            {"name": "Computer Science", "year": 1, "teacher_id": teachers[2].teacher_id},
            {"name": "Advanced Mathematics", "year": 2, "teacher_id": teachers[0].teacher_id},
            {"name": "Electronics", "year": 2, "teacher_id": teachers[1].teacher_id},
            {"name": "Programming", "year": 2, "teacher_id": teachers[2].teacher_id},
            {"name": "Applied Mathematics", "year": 3, "teacher_id": teachers[0].teacher_id},
            {"name": "Quantum Physics", "year": 3, "teacher_id": teachers[1].teacher_id},
            {"name": "Data Structures", "year": 3, "teacher_id": teachers[2].teacher_id}
        ]
        
        for subj_data in subjects_data:
            subject = Subject(
                subject_name=subj_data["name"],
                subject_year=subj_data["year"],
                teacher_id=subj_data["teacher_id"]
            )
            db.session.add(subject)
        
        print("Creating sample notices...")
        # Create sample notices
        notices_data = [
            {
                "title": "Welcome to the New Academic Year",
                "content": "We are excited to welcome all students to the new academic year. Please check your timetables and attend all classes."
            },
            {
                "title": "Mid-term Examinations",
                "content": "Mid-term examinations will be held from 15th to 25th of next month. Please prepare accordingly."
            },
            {
                "title": "Annual Sports Day",
                "content": "The annual sports day will be held on the 30th of next month. All students are encouraged to participate."
            }
        ]
        
        for notice_data in notices_data:
            notice = Notice(
                title=notice_data["title"],
                content=notice_data["content"],
                timestamp=datetime.utcnow()
            )
            db.session.add(notice)
        
        db.session.commit()
        print("Database initialized successfully!")

if __name__ == "__main__":
    initialize_database()