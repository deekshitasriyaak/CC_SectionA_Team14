#!/bin/bash
set -e

echo "Waiting for MySQL to be available..."
MAX_TRIES=30
COUNTER=0

while ! mysql -h$JOB_DB_HOST -u$JOB_DB_USER -p$JOB_DB_PASSWORD -e "SELECT 1" >/dev/null 2>&1; do
    COUNTER=$((COUNTER+1))
    if [ $COUNTER -ge $MAX_TRIES ]; then
        echo "Error: Couldn't connect to MySQL after $MAX_TRIES attempts."
        exit 1
    fi
    echo "MySQL is unavailable - sleeping ($COUNTER/$MAX_TRIES)"
    sleep 3
done

echo "MySQL is up - executing schema"

# Create database if it doesn't exist
mysql -h$JOB_DB_HOST -u$JOB_DB_USER -p$JOB_DB_PASSWORD -e "CREATE DATABASE IF NOT EXISTS $JOB_DB_NAME;"

# Create all tables with your exact schema
mysql -h$JOB_DB_HOST -u$JOB_DB_USER -p$JOB_DB_PASSWORD $JOB_DB_NAME -e "
-- Jobs table
CREATE TABLE IF NOT EXISTS jobs (
    id INT AUTO_INCREMENT PRIMARY KEY,
    title VARCHAR(255) NOT NULL
);

-- Candidates table
CREATE TABLE IF NOT EXISTS candidates (
    id INT AUTO_INCREMENT PRIMARY KEY,
    name VARCHAR(100) NOT NULL,
    email VARCHAR(100) NOT NULL,
    phone VARCHAR(15),
    resume VARCHAR(255),  -- File path to uploaded resume
    skills TEXT,
    experience INT,
    status ENUM('Pending', 'Accepted', 'Rejected') DEFAULT 'Pending',
    applied_on DATETIME DEFAULT CURRENT_TIMESTAMP,
    job_id INT,
    FOREIGN KEY (job_id) REFERENCES jobs(id) ON DELETE SET NULL
);

-- Interviews table
CREATE TABLE IF NOT EXISTS interviews (
    id INT AUTO_INCREMENT PRIMARY KEY,
    candidate_id INT NOT NULL,
    date DATETIME NOT NULL,  -- User-selected datetime
    interview_date DATETIME, -- For formatting + logic
    panel VARCHAR(100),
    link TEXT,
    message TEXT,
    FOREIGN KEY (candidate_id) REFERENCES candidates(id) ON DELETE CASCADE
);

-- Subjects table
CREATE TABLE IF NOT EXISTS subjects (
    id INT AUTO_INCREMENT PRIMARY KEY,
    name VARCHAR(100) NOT NULL
);

-- Candidate-Subject junction table
CREATE TABLE IF NOT EXISTS candidate_subjects (
    candidate_id INT,
    subject_id INT,
    PRIMARY KEY (candidate_id, subject_id),
    FOREIGN KEY (candidate_id) REFERENCES candidates(id) ON DELETE CASCADE,
    FOREIGN KEY (subject_id) REFERENCES subjects(id) ON DELETE CASCADE
);

-- Insert initial subjects based on the provided data
INSERT INTO subjects (name) VALUES
    ('Mathematics'),
    ('Physics'),
    ('Computer Science'),
    ('Advanced Mathematics'),
    ('Electronics'),
    ('Programming'),
    ('Applied Mathematics'),
    ('Quantum Physics'),
    ('Data Structures');

-- Insert some sample jobs
INSERT INTO jobs (title) VALUES
    ('Mathematics Teacher'),
    ('Physics Instructor'),
    ('Computer Science Lecturer'),
    ('Lab Assistant'),
    ('Department Coordinator');
"

echo "Database schema imported successfully!"