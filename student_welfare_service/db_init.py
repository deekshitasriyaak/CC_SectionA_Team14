# File: db_init.py

import sqlite3
import os

DB_PATH = 'student_welfare.db'
SCHEMA_PATH = 'init_student_db.sql'

def initialize_database():
    if os.path.exists(DB_PATH):
        print("Database already exists. Skipping initialization.")
        return

    with sqlite3.connect(DB_PATH) as conn:
        with open(SCHEMA_PATH, 'r') as f:
            schema_sql = f.read()
            conn.executescript(schema_sql)
        print("Database initialized successfully.")

        # Insert students as users
        students_data = [
            {"username": "student1", "password": "pass123", "name": "Alice Brown", "year": 1},
            {"username": "student2", "password": "pass123", "name": "Bob Miller", "year": 1},
            {"username": "student3", "password": "pass123", "name": "Charlie Davis", "year": 2},
            {"username": "student4", "password": "pass123", "name": "Diana Wilson", "year": 2},
            {"username": "student5", "password": "pass123", "name": "Edward Thomas", "year": 3},
            {"username": "student6", "password": "pass123", "name": "Fiona Martin", "year": 3}
        ]

        for student in students_data:
            email = f"{student['username']}@example.com"
            try:
                conn.execute("""
                    INSERT INTO users (email, password, user_type)
                    VALUES (?, ?, ?)
                """, (email, student["password"], "user"))
            except sqlite3.IntegrityError:
                print(f"User {email} already exists. Skipping.")

        conn.commit()
        print("Student users inserted successfully.")

if __name__ == '__main__':
    initialize_database()
