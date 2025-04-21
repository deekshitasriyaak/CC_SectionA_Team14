CC SECTION A - TEAM 14 Phase 2 
README.TXT

Team 14 
Arushi Prakash - PES1UG22AM033
Bhoomika Hegde - PES1UG22AM042
Deekshita Sriyaa K  - PES1UG22AM054
Achutha M - PES1UG22AM907	

PROJECT OVERVIEW:
This project is an Academic Management Service designed to streamline administrative, academic, and feedback-related tasks for universities. The platform supports three types of users:
1. Admin
2. Student
3. Teacher

Each user role has access to a customized dashboard and set of services. The platform is composed of the following microservices:

MICROSERVICES:

1. Records Service:
Admins can view records of students, teachers, and subjects, timetables .
Central data repository for user and course information.

2. Timetable Generation Service:
 Admins can generate subject-wise timetables based on teacher allocations.
Teachers and students can view their personalized schedules on their dashboards.

3. Attendance Service:
Teachers can view the students of their class and mark student attendance for each class.
Students can view their attendance records per subject on their dashboards.

4. Notice Board Service:
 Admins can publish university-wide notices.
 Notices are automatically displayed on teacher and student dashboards.

5. Feedback Service:
 Teachers and students can submit feedback to the admin.
Admins can respond to feedback, which becomes visible to the original sender.

EXTERNAL MICROSERVICE INTEGRATIONS:
All microservices have been pushed into docker containers and communicate via bridges and api calls 

1. Faculty Job Portal
 Allows external users to apply for faculty job positions at the university. Admins review applications and approve candidates via the Faculty Job Portal.
Integration 
  Upon approval, faculty details (name, subject, email, resume link, etc.) are automatically inserted into our main database and this can be viewed on the admin dashboard.


2.Student Grievance Portal
 Provides mental health support and issue reporting for students. Students can submit issues which are categorized and addressed separately by counselors and relevant departments.
Integration Details
Student personal and academic details are fetched from the main app database to the Grievance Portal on student sign-up. This reduces redundancy and ensures synchronization of student identity across systems.



TECHNOLOGIES USED:

Backend: Flask + SQLAlchemy
Database: SQLite (for dev), PostgreSQL (for production)
Frontend: HTML/CSS + JS (rendered templates)
Microservice Communication: REST APIs (JSON format)
Authentication: Role-based login system



