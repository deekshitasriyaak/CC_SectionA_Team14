from flask import Flask, redirect, url_for, request, jsonify
from models import db, User, Teacher, Subject, AcceptedFaculty
import random
from sqlalchemy.exc import OperationalError
import time
UPLOAD_FOLDER = 'uploads' 

#BASE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))


# Import all service blueprints
from auth_service import auth_service
from records_service import records_service
from timetable_service import timetable_service
from attendance_service import attendance_service
from notice_service import notice_service
from feedback_service import feedback_service
from dashboard_service import dashboard_service
import os

BASE_DIR = os.path.abspath(os.path.dirname(__file__))

def create_app():
    app = Flask(__name__)
    
    # Change to use the MySQL database from environment variable
    # Change this line in your app.py
    app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://root:password@school:3306/school'
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    app.secret_key = 'your_secret_key'
    app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

    # Initialize database
    db.init_app(app)
    with app.app_context():
        retry_count = 5
        while retry_count > 0:
            try:
                db.create_all()  # Test connection and create tables
                break  # Connection successful
            except OperationalError as e:
                retry_count -= 1
                print(f"Database connection failed. Retrying... {retry_count} attempts left.")
                if retry_count == 0:
                    print("Failed to connect to the database after multiple attempts.")
                    raise e
                time.sleep(10)
    # Register all blueprints
    app.register_blueprint(auth_service)
    app.register_blueprint(records_service)
    app.register_blueprint(timetable_service)
    app.register_blueprint(attendance_service)
    app.register_blueprint(notice_service)
    app.register_blueprint(feedback_service)
    app.register_blueprint(dashboard_service)

    # Root route redirects to auth service home
    @app.route('/')
    def index():
        return redirect(url_for('auth_service.home'))

    # API route to add a teacher
    @app.route('/api/add_teacher', methods=['POST'])
    def add_teacher():
        data = request.json
        name = data['teacher_name']
        role = 'teacher'

        # Create user
        user = User(username=name.lower().replace(" ", "_"), password='default123', role=role)
        db.session.add(user)
        db.session.commit()

        # Create teacher linked to user
        teacher = Teacher(teacher_name=name, teacher_user_id=user.user_id)
        db.session.add(teacher)
        db.session.commit()

        # Optionally assign subject
        subjects = Subject.query.filter_by(teacher_id=None).all()
        if subjects:
            subject = random.choice(subjects)
            subject.teacher_id = teacher.teacher_id
            db.session.commit()

        return jsonify({"message": f"Teacher {name} added"}), 201
    from datetime import datetime


    @app.template_filter('file_basename')
    def file_basename_filter(path):
        """Extract the file name from a full path."""
        return os.path.basename(path) if path else ""

    @app.template_filter('datetime')
    def format_datetime(value, format='%Y-%m-%d %H:%M:%S'):
        """Format a datetime object."""
        if value is None:
            return ""
        if isinstance(value, str):
            try:
                value = datetime.strptime(value, '%Y-%m-%d %H:%M:%S')
            except ValueError:
                return value
        return value.strftime(format)
    # API route to remove a teacher
    @app.route('/api/remove_teacher/<string:name>', methods=['DELETE'])
    def remove_teacher(name):
        teacher = Teacher.query.filter_by(teacher_name=name).first()
        if teacher:
            # Remove subject ownership
            Subject.query.filter_by(teacher_id=teacher.teacher_id).update({"teacher_id": None})
            
            # Delete teacher and associated user
            db.session.delete(teacher)
            user = User.query.get(teacher.teacher_user_id)
            if user:
                db.session.delete(user)
            
            db.session.commit()
            return jsonify({"message": f"Teacher {name} removed"}), 200

        return jsonify({"error": "Teacher not found"}), 404

    # Add a custom 404 handler
    @app.errorhandler(404)
    def page_not_found(e):
        return jsonify({"error": "URL not found"}), 404
    


    return app

# In your_main_app/app.py or dashboard_service.py



app = create_app()

if __name__ == '__main__':
    with app.app_context():
        db.create_all()  # Create all database tables if they don't exist
        app.run(host='0.0.0.0', port=5000, debug=True)