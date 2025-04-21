-- MySQL version of init_student_db.sql
CREATE TABLE IF NOT EXISTS grievances (
    id INT AUTO_INCREMENT PRIMARY KEY,
    student_name VARCHAR(255),
    email VARCHAR(255),
    category VARCHAR(100),
    message TEXT,
    submitted_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS appointments (
    id INT AUTO_INCREMENT PRIMARY KEY,
    name VARCHAR(255),
    email VARCHAR(255),
    appointment_date DATE,
    time_slot VARCHAR(100),
    submitted_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS wellbeing_resources (
    id INT AUTO_INCREMENT PRIMARY KEY,
    title VARCHAR(255),
    description TEXT,
    link VARCHAR(255),
    added_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS admin_details (
    id INT AUTO_INCREMENT PRIMARY KEY,
    username VARCHAR(255) UNIQUE,
    password VARCHAR(255)
);

CREATE TABLE IF NOT EXISTS users (
    id INT AUTO_INCREMENT PRIMARY KEY,
    email VARCHAR(255) NOT NULL UNIQUE,
    password VARCHAR(255) NOT NULL,
    user_type ENUM('admin', 'user') NOT NULL
);

-- Insert sample users
INSERT INTO users (email, password, user_type) VALUES
('student1@example.com', 'pass123', 'user'),
('student2@example.com', 'pass123', 'user'),
('student3@example.com', 'pass123', 'user'),
('student4@example.com', 'pass123', 'user'),
('student5@example.com', 'pass123', 'user'),
('student6@example.com', 'pass123', 'user'),
('admin@example.com', 'admin123', 'admin');