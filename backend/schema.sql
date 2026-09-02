-- MySQL Database Schema for Student Academic Performance Tracker

SET FOREIGN_KEY_CHECKS = 0;

DROP TABLE IF EXISTS attendance;
DROP TABLE IF EXISTS marks;
DROP TABLE IF EXISTS faculty_subjects;
DROP TABLE IF EXISTS subjects;
DROP TABLE IF EXISTS students;
DROP TABLE IF EXISTS faculty;
DROP TABLE IF EXISTS departments;
DROP TABLE IF EXISTS users;

SET FOREIGN_KEY_CHECKS = 1;

-- 1. USERS TABLE
CREATE TABLE IF NOT EXISTS users (
    user_id INT AUTO_INCREMENT PRIMARY KEY,
    username VARCHAR(100) NOT NULL UNIQUE,
    email VARCHAR(150) NOT NULL UNIQUE,
    password_hash VARCHAR(255) NOT NULL,
    role ENUM('Admin', 'Faculty', 'Student') NOT NULL,
    name VARCHAR(150) NOT NULL,
    is_active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    INDEX idx_user_username (username),
    INDEX idx_user_email (email),
    INDEX idx_user_role (role)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- 2. DEPARTMENTS TABLE
CREATE TABLE IF NOT EXISTS departments (
    department_id INT AUTO_INCREMENT PRIMARY KEY,
    department_code VARCHAR(20) NOT NULL UNIQUE,
    department_name VARCHAR(150) NOT NULL,
    INDEX idx_dept_code (department_code)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- 3. FACULTY TABLE
CREATE TABLE IF NOT EXISTS faculty (
    faculty_id INT AUTO_INCREMENT PRIMARY KEY,
    user_id INT NOT NULL UNIQUE,
    employee_id VARCHAR(50) NOT NULL UNIQUE,
    name VARCHAR(150) NOT NULL,
    email VARCHAR(150) NOT NULL UNIQUE,
    phone VARCHAR(30),
    department_id INT NOT NULL,
    hire_date DATE,
    FOREIGN KEY (user_id) REFERENCES users(user_id) ON DELETE CASCADE,
    FOREIGN KEY (department_id) REFERENCES departments(department_id),
    INDEX idx_faculty_emp_id (employee_id)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- 4. STUDENTS TABLE
CREATE TABLE IF NOT EXISTS students (
    student_id INT AUTO_INCREMENT PRIMARY KEY,
    user_id INT NOT NULL UNIQUE,
    enrollment_number VARCHAR(50) NOT NULL UNIQUE,
    first_name VARCHAR(75) NOT NULL,
    last_name VARCHAR(75) NOT NULL,
    email VARCHAR(150) NOT NULL UNIQUE,
    phone VARCHAR(30),
    department_id INT NOT NULL,
    course VARCHAR(100) NOT NULL,
    year INT NOT NULL DEFAULT 1,
    semester INT NOT NULL DEFAULT 1,
    admission_date DATE,
    FOREIGN KEY (user_id) REFERENCES users(user_id) ON DELETE CASCADE,
    FOREIGN KEY (department_id) REFERENCES departments(department_id),
    INDEX idx_student_enrollment (enrollment_number),
    INDEX idx_student_dept (department_id),
    INDEX idx_student_sem (semester)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- 5. SUBJECTS TABLE
CREATE TABLE IF NOT EXISTS subjects (
    subject_id INT AUTO_INCREMENT PRIMARY KEY,
    subject_code VARCHAR(20) NOT NULL UNIQUE,
    subject_name VARCHAR(150) NOT NULL,
    department_id INT NOT NULL,
    semester INT NOT NULL DEFAULT 1,
    credits INT NOT NULL DEFAULT 3,
    FOREIGN KEY (department_id) REFERENCES departments(department_id),
    INDEX idx_subject_code (subject_code),
    INDEX idx_subject_sem (semester)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- 6. FACULTY_SUBJECTS TABLE
CREATE TABLE IF NOT EXISTS faculty_subjects (
    id INT AUTO_INCREMENT PRIMARY KEY,
    faculty_id INT NOT NULL,
    subject_id INT NOT NULL,
    FOREIGN KEY (faculty_id) REFERENCES faculty(faculty_id) ON DELETE CASCADE,
    FOREIGN KEY (subject_id) REFERENCES subjects(subject_id) ON DELETE CASCADE,
    UNIQUE KEY uq_faculty_subject (faculty_id, subject_id)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- 7. MARKS TABLE
CREATE TABLE IF NOT EXISTS marks (
    mark_id INT AUTO_INCREMENT PRIMARY KEY,
    student_id INT NOT NULL,
    subject_id INT NOT NULL,
    semester INT NOT NULL DEFAULT 1,
    internal_marks DECIMAL(5,2) DEFAULT 0.00,
    assignment_marks DECIMAL(5,2) DEFAULT 0.00,
    practical_marks DECIMAL(5,2) DEFAULT 0.00,
    final_exam_marks DECIMAL(5,2) DEFAULT 0.00,
    total_marks DECIMAL(5,2) DEFAULT 0.00,
    grade VARCHAR(5) DEFAULT 'F',
    grade_point INT DEFAULT 0,
    FOREIGN KEY (student_id) REFERENCES students(student_id) ON DELETE CASCADE,
    FOREIGN KEY (subject_id) REFERENCES subjects(subject_id) ON DELETE CASCADE,
    UNIQUE KEY uq_student_subject_marks (student_id, subject_id),
    INDEX idx_marks_student (student_id),
    INDEX idx_marks_subject (subject_id)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- 8. ATTENDANCE TABLE
CREATE TABLE IF NOT EXISTS attendance (
    attendance_id INT AUTO_INCREMENT PRIMARY KEY,
    student_id INT NOT NULL,
    subject_id INT NOT NULL,
    semester INT NOT NULL DEFAULT 1,
    classes_held INT NOT NULL DEFAULT 0,
    classes_attended INT NOT NULL DEFAULT 0,
    attendance_percentage DECIMAL(5,2) DEFAULT 0.00,
    FOREIGN KEY (student_id) REFERENCES students(student_id) ON DELETE CASCADE,
    FOREIGN KEY (subject_id) REFERENCES subjects(subject_id) ON DELETE CASCADE,
    UNIQUE KEY uq_student_subject_attendance (student_id, subject_id),
    INDEX idx_att_student (student_id),
    INDEX idx_att_subject (subject_id)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;
