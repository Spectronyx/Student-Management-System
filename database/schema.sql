-- ==============================================================================
-- STUDENT MANAGEMENT SYSTEM - DATABASE SCHEMA & INITIAL DEMO DATA
-- Target Engine: MySQL / MariaDB (InnoDB Engine with Foreign Keys)
-- ==============================================================================

-- 1. Create Database if not exists
CREATE DATABASE IF NOT EXISTS student_management CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
USE student_management;

-- Disable Foreign Key Checks during schema rebuild
SET FOREIGN_KEY_CHECKS = 0;

-- 2. Drop existing tables if re-initializing
DROP TABLE IF EXISTS payments;
DROP TABLE IF EXISTS fees;
DROP TABLE IF EXISTS marks;
DROP TABLE IF EXISTS examinations;
DROP TABLE IF EXISTS attendance;
DROP TABLE IF EXISTS enrollments;
DROP TABLE IF EXISTS subjects;
DROP TABLE IF EXISTS students;
DROP TABLE IF EXISTS teachers;
DROP TABLE IF EXISTS courses;
DROP TABLE IF EXISTS departments;
DROP TABLE IF EXISTS users;

SET FOREIGN_KEY_CHECKS = 1;

-- ==============================================================================
-- TABLE CREATION
-- ==============================================================================

-- 1. USERS TABLE (Role-based authentication)
CREATE TABLE users (
    user_id INT AUTO_INCREMENT PRIMARY KEY,
    username VARCHAR(50) NOT NULL UNIQUE,
    password_hash VARCHAR(128) NOT NULL,
    role ENUM('Admin', 'Teacher', 'Student') NOT NULL,
    email VARCHAR(100) NOT NULL UNIQUE,
    is_active TINYINT(1) DEFAULT 1,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    INDEX idx_user_username (username),
    INDEX idx_user_role (role)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- 2. DEPARTMENTS TABLE
CREATE TABLE departments (
    department_id INT AUTO_INCREMENT PRIMARY KEY,
    department_code VARCHAR(20) NOT NULL UNIQUE,
    department_name VARCHAR(100) NOT NULL,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    INDEX idx_dept_code (department_code)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- 3. COURSES TABLE
CREATE TABLE courses (
    course_id INT AUTO_INCREMENT PRIMARY KEY,
    course_code VARCHAR(20) NOT NULL UNIQUE,
    course_name VARCHAR(100) NOT NULL,
    department_id INT NOT NULL,
    credits INT NOT NULL DEFAULT 3,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (department_id) REFERENCES departments(department_id) ON DELETE RESTRICT,
    INDEX idx_course_code (course_code),
    INDEX idx_course_dept (department_id)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- 4. TEACHERS TABLE
CREATE TABLE teachers (
    teacher_id INT AUTO_INCREMENT PRIMARY KEY,
    user_id INT NOT NULL UNIQUE,
    first_name VARCHAR(50) NOT NULL,
    last_name VARCHAR(50) NOT NULL,
    email VARCHAR(100) NOT NULL UNIQUE,
    phone VARCHAR(20) NOT NULL,
    department_id INT NOT NULL,
    hire_date DATE NOT NULL,
    FOREIGN KEY (user_id) REFERENCES users(user_id) ON DELETE CASCADE,
    FOREIGN KEY (department_id) REFERENCES departments(department_id) ON DELETE RESTRICT,
    INDEX idx_teacher_dept (department_id)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- 5. STUDENTS TABLE
CREATE TABLE students (
    student_id INT AUTO_INCREMENT PRIMARY KEY,
    user_id INT NOT NULL UNIQUE,
    roll_number VARCHAR(30) NOT NULL UNIQUE,
    first_name VARCHAR(50) NOT NULL,
    last_name VARCHAR(50) NOT NULL,
    dob DATE NOT NULL,
    gender ENUM('Male', 'Female', 'Other') NOT NULL,
    email VARCHAR(100) NOT NULL UNIQUE,
    phone VARCHAR(20) NOT NULL,
    address TEXT NOT NULL,
    department_id INT NOT NULL,
    course_id INT NOT NULL,
    semester INT NOT NULL DEFAULT 1,
    admission_date DATE NOT NULL,
    FOREIGN KEY (user_id) REFERENCES users(user_id) ON DELETE CASCADE,
    FOREIGN KEY (department_id) REFERENCES departments(department_id) ON DELETE RESTRICT,
    FOREIGN KEY (course_id) REFERENCES courses(course_id) ON DELETE RESTRICT,
    INDEX idx_student_roll (roll_number),
    INDEX idx_student_dept (department_id),
    INDEX idx_student_course (course_id)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- 6. SUBJECTS TABLE
CREATE TABLE subjects (
    subject_id INT AUTO_INCREMENT PRIMARY KEY,
    subject_code VARCHAR(20) NOT NULL UNIQUE,
    subject_name VARCHAR(100) NOT NULL,
    course_id INT NOT NULL,
    semester INT NOT NULL DEFAULT 1,
    credits INT NOT NULL DEFAULT 3,
    FOREIGN KEY (course_id) REFERENCES courses(course_id) ON DELETE CASCADE,
    INDEX idx_subject_course (course_id, semester)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- 7. ENROLLMENTS TABLE
CREATE TABLE enrollments (
    enrollment_id INT AUTO_INCREMENT PRIMARY KEY,
    student_id INT NOT NULL,
    course_id INT NOT NULL,
    semester INT NOT NULL,
    enrollment_date DATE NOT NULL,
    status ENUM('Active', 'Completed', 'Dropped') DEFAULT 'Active',
    UNIQUE KEY uk_student_course_sem (student_id, course_id, semester),
    FOREIGN KEY (student_id) REFERENCES students(student_id) ON DELETE CASCADE,
    FOREIGN KEY (course_id) REFERENCES courses(course_id) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- 8. ATTENDANCE TABLE
CREATE TABLE attendance (
    attendance_id INT AUTO_INCREMENT PRIMARY KEY,
    student_id INT NOT NULL,
    course_id INT NOT NULL,
    date DATE NOT NULL,
    status ENUM('Present', 'Absent', 'Late', 'Excused') NOT NULL DEFAULT 'Present',
    remarks VARCHAR(255) DEFAULT NULL,
    UNIQUE KEY uk_student_course_date (student_id, course_id, date),
    FOREIGN KEY (student_id) REFERENCES students(student_id) ON DELETE CASCADE,
    FOREIGN KEY (course_id) REFERENCES courses(course_id) ON DELETE CASCADE,
    INDEX idx_att_date (date),
    INDEX idx_att_student (student_id)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- 9. EXAMINATIONS TABLE
CREATE TABLE examinations (
    exam_id INT AUTO_INCREMENT PRIMARY KEY,
    exam_name VARCHAR(100) NOT NULL,
    course_id INT NOT NULL,
    semester INT NOT NULL,
    exam_date DATE NOT NULL,
    total_marks DECIMAL(5,2) NOT NULL DEFAULT 100.00,
    FOREIGN KEY (course_id) REFERENCES courses(course_id) ON DELETE CASCADE,
    INDEX idx_exam_course (course_id, semester)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- 10. MARKS TABLE
CREATE TABLE marks (
    mark_id INT AUTO_INCREMENT PRIMARY KEY,
    exam_id INT NOT NULL,
    subject_id INT NOT NULL,
    student_id INT NOT NULL,
    marks_obtained DECIMAL(5,2) NOT NULL,
    grade VARCHAR(5) NOT NULL,
    remarks VARCHAR(255) DEFAULT NULL,
    UNIQUE KEY uk_exam_subject_student (exam_id, subject_id, student_id),
    FOREIGN KEY (exam_id) REFERENCES examinations(exam_id) ON DELETE CASCADE,
    FOREIGN KEY (subject_id) REFERENCES subjects(subject_id) ON DELETE CASCADE,
    FOREIGN KEY (student_id) REFERENCES students(student_id) ON DELETE CASCADE,
    INDEX idx_marks_student (student_id)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- 11. FEES TABLE
CREATE TABLE fees (
    fee_id INT AUTO_INCREMENT PRIMARY KEY,
    student_id INT NOT NULL,
    semester INT NOT NULL,
    academic_year VARCHAR(20) NOT NULL,
    total_amount DECIMAL(10,2) NOT NULL,
    due_date DATE NOT NULL,
    status ENUM('Pending', 'Partial', 'Paid') NOT NULL DEFAULT 'Pending',
    FOREIGN KEY (student_id) REFERENCES students(student_id) ON DELETE CASCADE,
    INDEX idx_fee_student (student_id)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- 12. PAYMENTS TABLE
CREATE TABLE payments (
    payment_id INT AUTO_INCREMENT PRIMARY KEY,
    fee_id INT NOT NULL,
    amount_paid DECIMAL(10,2) NOT NULL,
    payment_date DATETIME DEFAULT CURRENT_TIMESTAMP,
    payment_method VARCHAR(50) NOT NULL DEFAULT 'Online',
    transaction_ref VARCHAR(100) NOT NULL UNIQUE,
    FOREIGN KEY (fee_id) REFERENCES fees(fee_id) ON DELETE CASCADE,
    INDEX idx_payment_fee (fee_id)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;


-- ==============================================================================
-- SAMPLE DEMO DATA
-- Passwords below are PBKDF2 hashed with salt 'sms_salt_2026':
-- admin / admin123 ➔ 0f95ec8d1cdcd93ce344dfe1c63227b015618a7763eebe5b3bde4e22783a1aa0
-- teacher1 / teacher123 ➔ fa29e32dc273d4c2dccf810263e6eefe4bdc68057b2581c2353e3c5a5e201796
-- student1 / student123 ➔ 6d4e0bd2329864cfe7668d7638beed0c20269503beae3389725030d543d3441b
-- ==============================================================================

INSERT INTO users (username, password_hash, role, email) VALUES
('admin', '0f95ec8d1cdcd93ce344dfe1c63227b015618a7763eebe5b3bde4e22783a1aa0', 'Admin', 'admin@school.edu'),
('prof_sharma', 'fa29e32dc273d4c2dccf810263e6eefe4bdc68057b2581c2353e3c5a5e201796', 'Teacher', 'rsharma@school.edu'),
('prof_gupta', 'fa29e32dc273d4c2dccf810263e6eefe4bdc68057b2581c2353e3c5a5e201796', 'Teacher', 'mgupta@school.edu'),
('student1', '6d4e0bd2329864cfe7668d7638beed0c20269503beae3389725030d543d3441b', 'Student', 'rahul.sharma@student.edu'),
('student2', '6d4e0bd2329864cfe7668d7638beed0c20269503beae3389725030d543d3441b', 'Student', 'priya.singh@student.edu'),
('student3', '6d4e0bd2329864cfe7668d7638beed0c20269503beae3389725030d543d3441b', 'Student', 'aman.verma@student.edu'),
('student4', '6d4e0bd2329864cfe7668d7638beed0c20269503beae3389725030d543d3441b', 'Student', 'neha.kumari@student.edu');

INSERT INTO departments (department_code, department_name) VALUES
('CS', 'Computer Science & Engineering'),
('BA', 'Business Administration'),
('EC', 'Electronics & Communication');

INSERT INTO courses (course_code, course_name, department_id, credits) VALUES
('BCA', 'Bachelor of Computer Applications', 1, 120),
('BCS', 'B.Tech Computer Science', 1, 160),
('MBA', 'Master of Business Administration', 2, 90);

INSERT INTO teachers (user_id, first_name, last_name, email, phone, department_id, hire_date) VALUES
(2, 'Rajesh', 'Sharma', 'rsharma@school.edu', '+919876543210', 1, '2020-01-15'),
(3, 'Meena', 'Gupta', 'mgupta@school.edu', '+919876543211', 2, '2021-06-01');

INSERT INTO students (user_id, roll_number, first_name, last_name, dob, gender, email, phone, address, department_id, course_id, semester, admission_date) VALUES
(4, 'BCA2025001', 'Rahul', 'Sharma', '2004-05-15', 'Male', 'rahul.sharma@student.edu', '+919811122233', '123 Park Street, Delhi', 1, 1, 1, '2025-08-01'),
(5, 'BCA2025002', 'Priya', 'Singh', '2004-08-20', 'Female', 'priya.singh@student.edu', '+919811122234', '45 MG Road, Mumbai', 1, 1, 1, '2025-08-01'),
(6, 'BCA2025003', 'Aman', 'Verma', '2003-12-10', 'Male', 'aman.verma@student.edu', '+919811122235', '78 Sector 15, Noida', 1, 1, 1, '2025-08-01'),
(7, 'BCS2025001', 'Neha', 'Kumari', '2004-02-28', 'Female', 'neha.kumari@student.edu', '+919811122236', '89 Ring Road, Bangalore', 1, 2, 1, '2025-08-01');

INSERT INTO subjects (subject_code, subject_name, course_id, semester, credits) VALUES
('BCA101', 'Programming in Python', 1, 1, 4),
('BCA102', 'Database Management Systems', 1, 1, 4),
('BCA103', 'Discrete Mathematics', 1, 1, 3),
('BCS101', 'Data Structures & Algorithms', 2, 1, 4);

INSERT INTO enrollments (student_id, course_id, semester, enrollment_date, status) VALUES
(1, 1, 1, '2025-08-01', 'Active'),
(2, 1, 1, '2025-08-01', 'Active'),
(3, 1, 1, '2025-08-01', 'Active'),
(4, 2, 1, '2025-08-01', 'Active');

INSERT INTO attendance (student_id, course_id, date, status, remarks) VALUES
(1, 1, '2026-02-01', 'Present', 'On time'),
(1, 1, '2026-02-02', 'Present', 'On time'),
(1, 1, '2026-02-03', 'Present', 'On time'),
(1, 1, '2026-02-04', 'Absent', 'Medical leave'),
(2, 1, '2026-02-01', 'Present', 'On time'),
(2, 1, '2026-02-02', 'Absent', 'Unexcused'),
(2, 1, '2026-02-03', 'Absent', 'Unexcused'),
(2, 1, '2026-02-04', 'Absent', 'Unexcused'),
(3, 1, '2026-02-01', 'Present', 'On time'),
(3, 1, '2026-02-02', 'Present', 'On time'),
(3, 1, '2026-02-03', 'Late', 'Arrived 15 mins late'),
(3, 1, '2026-02-04', 'Present', 'On time');

INSERT INTO examinations (exam_name, course_id, semester, exam_date, total_marks) VALUES
('Mid-Semester Examination 2026', 1, 1, '2026-02-15', 100.00);

INSERT INTO marks (exam_id, subject_id, student_id, marks_obtained, grade, remarks) VALUES
(1, 1, 1, 88.50, 'A', 'Excellent performance'),
(1, 2, 1, 92.00, 'A+', 'Outstanding'),
(1, 1, 2, 62.00, 'C', 'Needs improvement'),
(1, 2, 2, 58.50, 'D', 'Below average'),
(1, 1, 3, 78.00, 'B+', 'Good effort');

INSERT INTO fees (student_id, semester, academic_year, total_amount, due_date, status) VALUES
(1, 1, '2025-2026', 45000.00, '2025-09-01', 'Paid'),
(2, 1, '2025-2026', 45000.00, '2025-09-01', 'Partial'),
(3, 1, '2025-2026', 45000.00, '2025-09-01', 'Pending'),
(4, 1, '2025-2026', 55000.00, '2025-09-01', 'Paid');

INSERT INTO payments (fee_id, amount_paid, payment_date, payment_method, transaction_ref) VALUES
(1, 45000.00, '2025-08-15 10:30:00', 'UPI', 'TXN20250815001'),
(2, 20000.00, '2025-08-20 14:15:00', 'Credit Card', 'TXN20250820002'),
(4, 55000.00, '2025-08-10 11:00:00', 'Net Banking', 'TXN20250810003');
