"""
Student Academic Performance Tracker
Single-file pure Python & MySQL CLI application.
"""

import os
import sys
import re
import logging
from contextlib import contextmanager
from dotenv import load_dotenv
import mysql.connector
from mysql.connector import Error

try:
    import bcrypt
    HAS_BCRYPT = True
except ImportError:
    import hashlib
    HAS_BCRYPT = False

# Load environment variables
load_dotenv()

# Setup logging
logging.basicConfig(
    filename='app_errors.log', 
    level=logging.ERROR,
    format='%(asctime)s - %(levelname)s - %(message)s'
)

# ==============================================================================
# CONFIGURATION & DATABASE CONNECTIVITY
# ==============================================================================

class Config:
    DB_HOST = os.getenv("DB_HOST", "127.0.0.1")
    DB_PORT = int(os.getenv("DB_PORT", 3306))
    DB_NAME = os.getenv("DB_NAME", "student_academic_tracker")
    DB_USER = os.getenv("DB_USER", "root")
    DB_PASSWORD = os.getenv("DB_PASSWORD", "")
    DB_SOCKET = os.getenv("DB_SOCKET", "")

    @classmethod
    def get_db_config(cls, include_db=True):
        cfg = {
            "user": cls.DB_USER,
            "password": cls.DB_PASSWORD,
            "host": cls.DB_HOST,
            "port": cls.DB_PORT,
        }
        if cls.DB_SOCKET and os.path.exists(cls.DB_SOCKET):
            cfg["unix_socket"] = cls.DB_SOCKET
        if include_db:
            cfg["database"] = cls.DB_NAME
        return cfg

@contextmanager
def get_db_connection(include_db=True):
    """Context manager for MySQL connection."""
    conn = None
    try:
        conn = mysql.connector.connect(**Config.get_db_config(include_db=include_db))
        yield conn
    except Error as e:
        logging.error(f"Database Connection Error: {e}")
        raise e
    finally:
        if conn and conn.is_connected():
            conn.close()

@contextmanager
def get_db_cursor(commit=False, dictionary=True):
    """Context manager for database cursor with automatic transaction handling."""
    with get_db_connection(include_db=True) as conn:
        cursor = conn.cursor(dictionary=dictionary)
        try:
            yield cursor, conn
            if commit:
                conn.commit()
        except Error as e:
            if conn and conn.is_connected():
                conn.rollback()
            logging.error(f"Database Cursor Query Error: {e}")
            raise e
        finally:
            cursor.close()

# ==============================================================================
# EMBEDDED SQL SCHEMA & SEED DATA
# ==============================================================================

SCHEMA_SQL = """
CREATE TABLE IF NOT EXISTS departments (
    department_id INT AUTO_INCREMENT PRIMARY KEY,
    department_code VARCHAR(10) NOT NULL UNIQUE,
    department_name VARCHAR(100) NOT NULL
) ENGINE=InnoDB;

CREATE TABLE IF NOT EXISTS users (
    user_id INT AUTO_INCREMENT PRIMARY KEY,
    username VARCHAR(50) NOT NULL UNIQUE,
    email VARCHAR(100) NOT NULL UNIQUE,
    password_hash VARCHAR(255) NOT NULL,
    role ENUM('Admin', 'Faculty', 'Student') NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
) ENGINE=InnoDB;

CREATE TABLE IF NOT EXISTS students (
    student_id INT AUTO_INCREMENT PRIMARY KEY,
    user_id INT UNIQUE,
    enrollment_no VARCHAR(30) NOT NULL UNIQUE,
    name VARCHAR(100) NOT NULL,
    email VARCHAR(100) NOT NULL UNIQUE,
    phone VARCHAR(20),
    department_id INT NOT NULL,
    course VARCHAR(100) NOT NULL,
    year INT NOT NULL CHECK (year >= 1 AND year <= 4),
    semester INT NOT NULL CHECK (semester >= 1 AND semester <= 8),
    FOREIGN KEY (user_id) REFERENCES users(user_id) ON DELETE CASCADE,
    FOREIGN KEY (department_id) REFERENCES departments(department_id) ON DELETE RESTRICT
) ENGINE=InnoDB;

CREATE TABLE IF NOT EXISTS faculty (
    faculty_id INT AUTO_INCREMENT PRIMARY KEY,
    user_id INT UNIQUE,
    faculty_code VARCHAR(30) NOT NULL UNIQUE,
    name VARCHAR(100) NOT NULL,
    email VARCHAR(100) NOT NULL UNIQUE,
    phone VARCHAR(20),
    department_id INT NOT NULL,
    designation VARCHAR(100),
    FOREIGN KEY (user_id) REFERENCES users(user_id) ON DELETE CASCADE,
    FOREIGN KEY (department_id) REFERENCES departments(department_id) ON DELETE RESTRICT
) ENGINE=InnoDB;

CREATE TABLE IF NOT EXISTS subjects (
    subject_id INT AUTO_INCREMENT PRIMARY KEY,
    subject_code VARCHAR(20) NOT NULL UNIQUE,
    subject_name VARCHAR(100) NOT NULL,
    credits INT NOT NULL CHECK (credits > 0),
    semester INT NOT NULL CHECK (semester >= 1 AND semester <= 8),
    department_id INT NOT NULL,
    FOREIGN KEY (department_id) REFERENCES departments(department_id) ON DELETE CASCADE
) ENGINE=InnoDB;

CREATE TABLE IF NOT EXISTS marks (
    mark_id INT AUTO_INCREMENT PRIMARY KEY,
    student_id INT NOT NULL,
    subject_id INT NOT NULL,
    internal_marks DECIMAL(5,2) DEFAULT 0.00 CHECK (internal_marks >= 0 AND internal_marks <= 20),
    assignment_marks DECIMAL(5,2) DEFAULT 0.00 CHECK (assignment_marks >= 0 AND assignment_marks <= 10),
    practical_marks DECIMAL(5,2) DEFAULT 0.00 CHECK (practical_marks >= 0 AND practical_marks <= 20),
    final_marks DECIMAL(5,2) DEFAULT 0.00 CHECK (final_marks >= 0 AND final_marks <= 50),
    total_marks DECIMAL(5,2) DEFAULT 0.00 CHECK (total_marks >= 0 AND total_marks <= 100),
    grade VARCHAR(5) NOT NULL,
    grade_point DECIMAL(4,2) NOT NULL,
    semester INT NOT NULL,
    UNIQUE KEY uq_student_subject_marks (student_id, subject_id),
    FOREIGN KEY (student_id) REFERENCES students(student_id) ON DELETE CASCADE,
    FOREIGN KEY (subject_id) REFERENCES subjects(subject_id) ON DELETE CASCADE
) ENGINE=InnoDB;

CREATE TABLE IF NOT EXISTS attendance (
    attendance_id INT AUTO_INCREMENT PRIMARY KEY,
    student_id INT NOT NULL,
    subject_id INT NOT NULL,
    classes_held INT NOT NULL CHECK (classes_held >= 0),
    classes_attended INT NOT NULL CHECK (classes_attended >= 0),
    attendance_percentage DECIMAL(5,2) NOT NULL CHECK (attendance_percentage >= 0 AND attendance_percentage <= 100),
    semester INT NOT NULL,
    UNIQUE KEY uq_student_subject_att (student_id, subject_id),
    FOREIGN KEY (student_id) REFERENCES students(student_id) ON DELETE CASCADE,
    FOREIGN KEY (subject_id) REFERENCES subjects(subject_id) ON DELETE CASCADE
) ENGINE=InnoDB;

CREATE INDEX idx_students_enrollment ON students(enrollment_no);
CREATE INDEX idx_students_email ON students(email);
CREATE INDEX idx_students_dept_sem ON students(department_id, semester);
CREATE INDEX idx_subjects_code ON subjects(subject_code);
CREATE INDEX idx_marks_student_subject ON marks(student_id, subject_id);
CREATE INDEX idx_attendance_student_subject ON attendance(student_id, subject_id);

CREATE OR REPLACE VIEW student_performance_view AS
SELECT 
    s.student_id,
    s.enrollment_no,
    s.name AS student_name,
    s.email AS student_email,
    d.department_name,
    s.course,
    s.semester AS current_semester,
    sub.subject_code,
    sub.subject_name,
    sub.credits,
    m.internal_marks,
    m.assignment_marks,
    m.practical_marks,
    m.final_marks,
    m.total_marks,
    m.grade,
    m.grade_point,
    a.classes_held,
    a.classes_attended,
    a.attendance_percentage,
    CASE 
        WHEN a.attendance_percentage < 75.0 THEN 'Attendance Warning'
        ELSE 'Normal'
    END AS attendance_status
FROM students s
JOIN departments d ON s.department_id = d.department_id
LEFT JOIN marks m ON s.student_id = m.student_id
LEFT JOIN subjects sub ON m.subject_id = sub.subject_id
LEFT JOIN attendance a ON s.student_id = a.student_id AND sub.subject_id = a.subject_id;

CREATE OR REPLACE VIEW attendance_view AS
SELECT 
    a.attendance_id,
    s.student_id,
    s.enrollment_no,
    s.name AS student_name,
    sub.subject_code,
    sub.subject_name,
    a.classes_held,
    a.classes_attended,
    a.attendance_percentage,
    a.semester,
    CASE 
        WHEN a.attendance_percentage < 75.0 THEN 'Attendance Warning'
        ELSE 'Normal'
    END AS warning_status
FROM attendance a
JOIN students s ON a.student_id = s.student_id
JOIN subjects sub ON a.subject_id = sub.subject_id;
"""

SEED_SQL = """
INSERT INTO departments (department_id, department_code, department_name) VALUES
(1, 'CS', 'Computer Science and Engineering'),
(2, 'ECE', 'Electronics and Communication Engineering'),
(3, 'ME', 'Mechanical Engineering'),
(4, 'IT', 'Information Technology')
ON DUPLICATE KEY UPDATE department_name=VALUES(department_name);

INSERT INTO users (user_id, username, email, password_hash, role) VALUES
(1, 'admin', 'admin@tracker.edu', '$2b$12$EKG4zV9nHop38HTiR/R6ZOt8W.MMMs3Kuw8trLZ/1IzW9KCGLtp32', 'Admin'),
(2, 'prof_rajesh', 'rajesh.sharma@tracker.edu', '$2b$12$U3tRl15fqfNysIyxnw7wNOpzhEqwPlHlhCNw99SUpYpdxxWPSWRSi', 'Faculty'),
(3, 'prof_anita', 'anita.verma@tracker.edu', '$2b$12$U3tRl15fqfNysIyxnw7wNOpzhEqwPlHlhCNw99SUpYpdxxWPSWRSi', 'Faculty'),
(4, 'std_rahul', 'rahul.kumar@tracker.edu', '$2b$12$badaN766SSaijdWR1m4/tucJOTQeGkgmLK5IGznVWaFyOygp7q6.G', 'Student'),
(5, 'std_priya', 'priya.singh@tracker.edu', '$2b$12$badaN766SSaijdWR1m4/tucJOTQeGkgmLK5IGznVWaFyOygp7q6.G', 'Student'),
(6, 'std_amit', 'amit.patel@tracker.edu', '$2b$12$badaN766SSaijdWR1m4/tucJOTQeGkgmLK5IGznVWaFyOygp7q6.G', 'Student'),
(7, 'std_neha', 'neha.sharma@tracker.edu', '$2b$12$badaN766SSaijdWR1m4/tucJOTQeGkgmLK5IGznVWaFyOygp7q6.G', 'Student'),
(8, 'std_rohan', 'rohan.gupta@tracker.edu', '$2b$12$badaN766SSaijdWR1m4/tucJOTQeGkgmLK5IGznVWaFyOygp7q6.G', 'Student'),
(9, 'std_sneha', 'sneha.reddy@tracker.edu', '$2b$12$badaN766SSaijdWR1m4/tucJOTQeGkgmLK5IGznVWaFyOygp7q6.G', 'Student'),
(10, 'std_vikram', 'vikram.aditya@tracker.edu', '$2b$12$badaN766SSaijdWR1m4/tucJOTQeGkgmLK5IGznVWaFyOygp7q6.G', 'Student'),
(11, 'std_pooja', 'pooja.mehta@tracker.edu', '$2b$12$badaN766SSaijdWR1m4/tucJOTQeGkgmLK5IGznVWaFyOygp7q6.G', 'Student'),
(12, 'std_karan', 'karan.josh@tracker.edu', '$2b$12$badaN766SSaijdWR1m4/tucJOTQeGkgmLK5IGznVWaFyOygp7q6.G', 'Student'),
(13, 'std_divya', 'divya.nair@tracker.edu', '$2b$12$badaN766SSaijdWR1m4/tucJOTQeGkgmLK5IGznVWaFyOygp7q6.G', 'Student'),
(14, 'std_sanjay', 'sanjay.dutta@tracker.edu', '$2b$12$badaN766SSaijdWR1m4/tucJOTQeGkgmLK5IGznVWaFyOygp7q6.G', 'Student'),
(15, 'std_ananya', 'ananya.roy@tracker.edu', '$2b$12$badaN766SSaijdWR1m4/tucJOTQeGkgmLK5IGznVWaFyOygp7q6.G', 'Student'),
(16, 'std_manish', 'manish.kumar@tracker.edu', '$2b$12$badaN766SSaijdWR1m4/tucJOTQeGkgmLK5IGznVWaFyOygp7q6.G', 'Student'),
(17, 'std_kavya', 'kavya.srinivasan@tracker.edu', '$2b$12$badaN766SSaijdWR1m4/tucJOTQeGkgmLK5IGznVWaFyOygp7q6.G', 'Student'),
(18, 'std_varun', 'varun.chopra@tracker.edu', '$2b$12$badaN766SSaijdWR1m4/tucJOTQeGkgmLK5IGznVWaFyOygp7q6.G', 'Student'),
(19, 'std_shreya', 'shreya.goswami@tracker.edu', '$2b$12$badaN766SSaijdWR1m4/tucJOTQeGkgmLK5IGznVWaFyOygp7q6.G', 'Student'),
(20, 'std_tarun', 'tarun.bansal@tracker.edu', '$2b$12$badaN766SSaijdWR1m4/tucJOTQeGkgmLK5IGznVWaFyOygp7q6.G', 'Student'),
(21, 'std_megha', 'megha.jain@tracker.edu', '$2b$12$badaN766SSaijdWR1m4/tucJOTQeGkgmLK5IGznVWaFyOygp7q6.G', 'Student'),
(22, 'std_aditya', 'aditya.mishra@tracker.edu', '$2b$12$badaN766SSaijdWR1m4/tucJOTQeGkgmLK5IGznVWaFyOygp7q6.G', 'Student'),
(23, 'std_kriti', 'kriti.sanon@tracker.edu', '$2b$12$badaN766SSaijdWR1m4/tucJOTQeGkgmLK5IGznVWaFyOygp7q6.G', 'Student')
ON DUPLICATE KEY UPDATE email=VALUES(email);

INSERT INTO faculty (faculty_id, user_id, faculty_code, name, email, phone, department_id, designation) VALUES
(1, 2, 'FAC101', 'Dr. Rajesh Sharma', 'rajesh.sharma@tracker.edu', '9876543210', 1, 'Professor & HOD'),
(2, 3, 'FAC102', 'Dr. Anita Verma', 'anita.verma@tracker.edu', '9876543211', 2, 'Associate Professor')
ON DUPLICATE KEY UPDATE name=VALUES(name);

INSERT INTO students (student_id, user_id, enrollment_no, name, email, phone, department_id, course, year, semester) VALUES
(1, 4, 'CS2026001', 'Rahul Kumar', 'rahul.kumar@tracker.edu', '9123456780', 1, 'B.Tech CSE', 3, 6),
(2, 5, 'CS2026002', 'Priya Singh', 'priya.singh@tracker.edu', '9123456781', 1, 'B.Tech CSE', 3, 6),
(3, 6, 'CS2026003', 'Amit Patel', 'amit.patel@tracker.edu', '9123456782', 1, 'B.Tech CSE', 3, 6),
(4, 7, 'CS2026004', 'Neha Sharma', 'neha.sharma@tracker.edu', '9123456783', 1, 'B.Tech CSE', 3, 6),
(5, 8, 'CS2026005', 'Rohan Gupta', 'rohan.gupta@tracker.edu', '9123456784', 1, 'B.Tech CSE', 3, 6),
(6, 9, 'ECE2026001', 'Sneha Reddy', 'sneha.reddy@tracker.edu', '9123456785', 2, 'B.Tech ECE', 3, 6),
(7, 10, 'ECE2026002', 'Vikram Aditya', 'vikram.aditya@tracker.edu', '9123456786', 2, 'B.Tech ECE', 3, 6),
(8, 11, 'ECE2026003', 'Pooja Mehta', 'pooja.mehta@tracker.edu', '9123456787', 2, 'B.Tech ECE', 3, 6),
(9, 12, 'ECE2026004', 'Karan Joshi', 'karan.josh@tracker.edu', '9123456788', 2, 'B.Tech ECE', 3, 6),
(10, 13, 'ECE2026005', 'Divya Nair', 'divya.nair@tracker.edu', '9123456789', 2, 'B.Tech ECE', 3, 6),
(11, 14, 'ME2026001', 'Sanjay Dutta', 'sanjay.dutta@tracker.edu', '9123456790', 3, 'B.Tech ME', 3, 6),
(12, 15, 'ME2026002', 'Ananya Roy', 'ananya.roy@tracker.edu', '9123456791', 3, 'B.Tech ME', 3, 6),
(13, 16, 'ME2026003', 'Manish Kumar', 'manish.kumar@tracker.edu', '9123456792', 3, 'B.Tech ME', 3, 6),
(14, 17, 'ME2026004', 'Kavya Srinivasan', 'kavya.srinivasan@tracker.edu', '9123456793', 3, 'B.Tech ME', 3, 6),
(15, 18, 'ME2026005', 'Varun Chopra', 'varun.chopra@tracker.edu', '9123456794', 3, 'B.Tech ME', 3, 6),
(16, 19, 'IT2026001', 'Shreya Goswami', 'shreya.goswami@tracker.edu', '9123456795', 4, 'B.Tech IT', 3, 6),
(17, 20, 'IT2026002', 'Tarun Bansal', 'tarun.bansal@tracker.edu', '9123456796', 4, 'B.Tech IT', 3, 6),
(18, 21, 'IT2026003', 'Megha Jain', 'megha.jain@tracker.edu', '9123456797', 4, 'B.Tech IT', 3, 6),
(19, 22, 'IT2026004', 'Aditya Mishra', 'aditya.mishra@tracker.edu', '9123456798', 4, 'B.Tech IT', 3, 6),
(20, 23, 'IT2026005', 'Kriti Sanon', 'kriti.sanon@tracker.edu', '9123456799', 4, 'B.Tech IT', 3, 6)
ON DUPLICATE KEY UPDATE name=VALUES(name);

INSERT INTO subjects (subject_id, subject_code, subject_name, credits, semester, department_id) VALUES
(1, 'CS601', 'Data Structures & Algorithms', 4, 6, 1),
(2, 'CS602', 'Database Management Systems', 4, 6, 1),
(3, 'CS603', 'Operating Systems', 3, 6, 1),
(4, 'CS604', 'Computer Networks', 3, 6, 1),
(5, 'EC601', 'Digital Signal Processing', 4, 6, 2),
(6, 'EC602', 'Embedded Systems', 4, 6, 2),
(7, 'ME601', 'Fluid Mechanics', 4, 6, 3),
(8, 'IT601', 'Web Technologies', 4, 6, 4)
ON DUPLICATE KEY UPDATE subject_name=VALUES(subject_name);

INSERT INTO marks (student_id, subject_id, internal_marks, assignment_marks, practical_marks, final_marks, total_marks, grade, grade_point, semester) VALUES
(1, 1, 18.00, 9.00, 18.00, 46.00, 91.00, 'A+', 10.00, 6),
(1, 2, 16.00, 8.00, 16.00, 44.00, 84.00, 'A', 9.00, 6),
(1, 3, 14.00, 7.00, 15.00, 40.00, 76.00, 'B+', 8.00, 6),
(2, 1, 19.00, 10.00, 19.00, 47.00, 95.00, 'A+', 10.00, 6),
(2, 2, 18.00, 9.00, 18.00, 45.00, 90.00, 'A+', 10.00, 6),
(2, 3, 17.00, 8.00, 17.00, 46.00, 88.00, 'A', 9.00, 6),
(3, 1, 12.00, 6.00, 12.00, 32.00, 62.00, 'B', 7.00, 6),
(3, 2, 14.00, 7.00, 14.00, 37.00, 72.00, 'B+', 8.00, 6),
(3, 3, 10.00, 5.00, 11.00, 28.00, 54.00, 'C', 6.00, 6),
(4, 1, 15.00, 8.00, 15.00, 40.00, 78.00, 'B+', 8.00, 6),
(4, 2, 17.00, 9.00, 17.00, 42.00, 85.00, 'A', 9.00, 6),
(5, 1, 8.00, 4.00, 8.00, 18.00, 38.00, 'F', 0.00, 6),
(5, 2, 9.00, 4.00, 10.00, 22.00, 45.00, 'D', 5.00, 6),
(6, 5, 18.00, 9.00, 18.00, 47.00, 92.00, 'A+', 10.00, 6),
(6, 6, 17.00, 9.00, 17.00, 44.00, 87.00, 'A', 9.00, 6),
(7, 5, 14.00, 7.00, 15.00, 36.00, 72.00, 'B+', 8.00, 6),
(7, 6, 13.00, 6.00, 14.00, 35.00, 68.00, 'B', 7.00, 6),
(11, 7, 16.00, 8.00, 16.00, 41.00, 81.00, 'A', 9.00, 6),
(16, 8, 19.00, 9.00, 19.00, 46.00, 93.00, 'A+', 10.00, 6)
ON DUPLICATE KEY UPDATE total_marks=VALUES(total_marks);

INSERT INTO attendance (student_id, subject_id, classes_held, classes_attended, attendance_percentage, semester) VALUES
(1, 1, 50, 44, 88.00, 6),
(1, 2, 45, 41, 91.11, 6),
(1, 3, 50, 36, 72.00, 6),
(2, 1, 50, 48, 96.00, 6),
(2, 2, 45, 43, 95.56, 6),
(2, 3, 50, 46, 92.00, 6),
(3, 1, 50, 40, 80.00, 6),
(3, 2, 45, 34, 75.56, 6),
(3, 3, 50, 33, 66.00, 6),
(4, 1, 50, 42, 84.00, 6),
(4, 2, 45, 39, 86.67, 6),
(5, 1, 50, 25, 50.00, 6),
(5, 2, 45, 28, 62.22, 6),
(6, 5, 48, 45, 93.75, 6),
(6, 6, 48, 44, 91.67, 6),
(7, 5, 48, 35, 72.92, 6),
(7, 6, 48, 38, 79.17, 6),
(11, 7, 50, 42, 84.00, 6),
(16, 8, 40, 38, 95.00, 6)
ON DUPLICATE KEY UPDATE classes_attended=VALUES(classes_attended);
"""

def init_database(run_seed=True):
    """Ensure Database exists, run schema initialization and seed initial records."""
    try:
        base_cfg = Config.get_db_config(include_db=False)
        conn = mysql.connector.connect(**base_cfg)
        cursor = conn.cursor()
        cursor.execute(f"CREATE DATABASE IF NOT EXISTS {Config.DB_NAME}")
        cursor.close()
        conn.close()

        with get_db_connection(include_db=True) as conn:
            cursor = conn.cursor()
            for cmd in SCHEMA_SQL.split(';'):
                c = cmd.strip()
                if c:
                    try:
                        cursor.execute(c)
                    except Error as e:
                        if e.errno == 1061: # Duplicate key name index
                            pass
                        else:
                            logging.warning(f"Schema note: {e}")
            conn.commit()
            cursor.close()

        if run_seed:
            with get_db_connection(include_db=True) as conn:
                cursor = conn.cursor()
                for cmd in SEED_SQL.split(';'):
                    c = cmd.strip()
                    if c:
                        try:
                            cursor.execute(c)
                        except Error as e:
                            if e.errno != 1062: # Ignore duplicate entry
                                logging.warning(f"Seed note: {e}")
                conn.commit()
                cursor.close()
        return True, "Database initialized successfully."
    except Exception as e:
        logging.error(f"Init DB Error: {e}")
        return False, str(e)

# ==============================================================================
# SECURITY & AUTHENTICATION
# ==============================================================================

def hash_password(password: str) -> str:
    if HAS_BCRYPT:
        return bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')
    else:
        return hashlib.sha256(password.encode('utf-8')).hexdigest()

def verify_password(password: str, stored_hash: str) -> bool:
    if HAS_BCRYPT and stored_hash.startswith('$2b$'):
        try:
            return bcrypt.checkpw(password.encode('utf-8'), stored_hash.encode('utf-8'))
        except Exception:
            return False
    else:
        return hashlib.sha256(password.encode('utf-8')).hexdigest() == stored_hash

def authenticate_user(username_or_email, password):
    query = "SELECT user_id, username, email, password_hash, role FROM users WHERE username = %s OR email = %s"
    try:
        with get_db_cursor(commit=False) as (cursor, conn):
            cursor.execute(query, (username_or_email, username_or_email))
            user = cursor.fetchone()
            if not user:
                return False, "User account not found."
            if verify_password(password, user['password_hash']):
                linked_id = None
                if user['role'] == 'Student':
                    cursor.execute("SELECT student_id FROM students WHERE user_id = %s", (user['user_id'],))
                    res = cursor.fetchone()
                    if res: linked_id = res['student_id']
                elif user['role'] == 'Faculty':
                    cursor.execute("SELECT faculty_id FROM faculty WHERE user_id = %s", (user['user_id'],))
                    res = cursor.fetchone()
                    if res: linked_id = res['faculty_id']
                user['linked_id'] = linked_id
                del user['password_hash']
                return True, user
            else:
                return False, "Invalid password."
    except Error as e:
        return False, f"Database error during authentication: {e}"

def create_user_account(username, email, password, role):
    pwd_hash = hash_password(password)
    query = "INSERT INTO users (username, email, password_hash, role) VALUES (%s, %s, %s, %s)"
    try:
        with get_db_cursor(commit=True) as (cursor, conn):
            cursor.execute(query, (username, email, pwd_hash, role))
            return True, cursor.lastrowid
    except Error as e:
        if e.errno == 1062:
            return False, "Username or email already exists."
        return False, f"Database error: {e}"

def change_user_password(user_id, old_password, new_password):
    try:
        with get_db_cursor(commit=True) as (cursor, conn):
            cursor.execute("SELECT password_hash FROM users WHERE user_id = %s", (user_id,))
            user = cursor.fetchone()
            if not user or not verify_password(old_password, user['password_hash']):
                return False, "Current password is incorrect."
            new_hash = hash_password(new_password)
            cursor.execute("UPDATE users SET password_hash = %s WHERE user_id = %s", (new_hash, user_id))
            return True, "Password updated successfully."
    except Error as e:
        return False, f"Error updating password: {e}"

# ==============================================================================
# GRADING & CALCULATIONS UTILITIES
# ==============================================================================

def calculate_grade_and_point(total_marks):
    """Centralized grading function based on total marks (0-100)."""
    if total_marks < 0 or total_marks > 100:
        raise ValueError("Total marks must be between 0 and 100.")
    if total_marks >= 90: return 'A+', 10.0
    elif total_marks >= 80: return 'A', 9.0
    elif total_marks >= 70: return 'B+', 8.0
    elif total_marks >= 60: return 'B', 7.0
    elif total_marks >= 50: return 'C', 6.0
    elif total_marks >= 40: return 'D', 5.0
    else: return 'F', 0.0

def calculate_attendance_percentage(classes_held, classes_attended):
    held = int(classes_held)
    attended = int(classes_attended)
    if held < 0 or attended < 0:
        raise ValueError("Classes count cannot be negative.")
    if attended > held:
        raise ValueError("Classes attended cannot exceed classes held.")
    if held == 0:
        return 0.0
    return round((attended / held) * 100.0, 2)

def calculate_gpa(records):
    """Calculate weighted GPA: SUM(grade_point * credits) / SUM(credits)."""
    if not records: return 0.0
    tot_points = 0.0
    tot_credits = 0
    for r in records:
        gp = float(r.get('grade_point', 0))
        cr = int(r.get('credits', 0))
        if cr > 0:
            tot_points += (gp * cr)
            tot_credits += cr
    if tot_credits == 0: return 0.0
    return round(tot_points / tot_credits, 2)

def determine_performance_status(gpa, att_pct, has_failed=False):
    if has_failed or gpa < 4.0 or att_pct < 60.0: return "At Risk"
    elif gpa >= 9.0 and att_pct >= 85.0: return "Excellent"
    elif gpa >= 8.0 and att_pct >= 75.0: return "Good"
    elif gpa >= 6.0 and att_pct >= 75.0: return "Average"
    else: return "Needs Improvement"

# ==============================================================================
# VALIDATORS & SAFE CLI PROMPT HELPERS
# ==============================================================================

def validate_email(email):
    if not email or not re.match(r"^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$", email.strip()):
        return False, "Invalid email format (e.g. user@domain.com)."
    return True, "Valid"

def prompt_string(prompt_text, required=True):
    while True:
        val = input(prompt_text).strip()
        if required and not val:
            print("❌ Input cannot be empty. Try again.")
            continue
        return val

def prompt_int(prompt_text, min_val=None, max_val=None, default=None):
    while True:
        val_str = input(prompt_text).strip()
        if not val_str and default is not None:
            return default
        try:
            val = int(val_str)
            if min_val is not None and val < min_val:
                print(f"❌ Must be at least {min_val}.")
                continue
            if max_val is not None and val > max_val:
                print(f"❌ Cannot exceed {max_val}.")
                continue
            return val
        except ValueError:
            print("❌ Please enter a valid integer.")

def prompt_float(prompt_text, min_val=None, max_val=None, default=None):
    while True:
        val_str = input(prompt_text).strip()
        if not val_str and default is not None:
            return default
        try:
            val = float(val_str)
            if min_val is not None and val < min_val:
                print(f"❌ Must be at least {min_val}.")
                continue
            if max_val is not None and val > max_val:
                print(f"❌ Cannot exceed {max_val}.")
                continue
            return val
        except ValueError:
            print("❌ Please enter a valid numeric value.")

# ==============================================================================
# ASCII TABLE FORMATTER
# ==============================================================================

def print_table(data, headers, title=None):
    """Pure Python clean ASCII table renderer."""
    if title:
        print("\n" + "=" * 65)
        print(f"  {title.upper()}")
        print("=" * 65)
        
    if not data:
        print("ℹ️ No records found.")
        return

    # Convert all values to string
    str_data = [[str(cell) for cell in row] for row in data]
    col_widths = [len(h) for h in headers]
    for row in str_data:
        for i, cell in enumerate(row):
            if i < len(col_widths):
                col_widths[i] = max(col_widths[i], len(cell))

    header_line = " | ".join(h.ljust(col_widths[i]) for i, h in enumerate(headers))
    sep_line = "-+-".join("-" * col_widths[i] for i in range(len(headers)))
    
    print("+" + "-" * (len(header_line) + 2) + "+")
    print("| " + header_line + " |")
    print("+" + sep_line + "+")
    for row in str_data:
        line = " | ".join(row[i].ljust(col_widths[i]) for i in range(len(headers)))
        print("| " + line + " |")
    print("+" + "-" * (len(header_line) + 2) + "+")

# ==============================================================================
# CORE BUSINESS LOGIC (STUDENTS, FACULTY, SUBJECTS, MARKS, ATTENDANCE)
# ==============================================================================

# --- STUDENT SERVICES ---
def add_student(enrollment_no, name, email, phone, department_id, course, year, semester, username=None, password=None):
    is_valid, msg = validate_email(email)
    if not is_valid: return False, msg
    user_id = None
    if username and password:
        s, r = create_user_account(username, email, password, role='Student')
        if not s: return False, f"Failed user account creation: {r}"
        user_id = r

    query = """INSERT INTO students (user_id, enrollment_no, name, email, phone, department_id, course, year, semester)
               VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)"""
    try:
        with get_db_cursor(commit=True) as (cursor, conn):
            cursor.execute(query, (user_id, enrollment_no.upper(), name, email, phone, department_id, course, year, semester))
            return True, f"Student '{name}' added with ID {cursor.lastrowid}."
    except Error as e:
        if e.errno == 1062: return False, "Duplicate enrollment number or email."
        return False, f"Database error: {e}"

def get_all_students():
    q = """SELECT s.student_id, s.enrollment_no, s.name, s.email, s.phone, d.department_name, s.course, s.year, s.semester
           FROM students s JOIN departments d ON s.department_id = d.department_id ORDER BY s.student_id"""
    with get_db_cursor() as (cursor, conn):
        cursor.execute(q)
        return cursor.fetchall()

def search_students(kw):
    q = """SELECT s.student_id, s.enrollment_no, s.name, s.email, d.department_name, s.course, s.semester
           FROM students s JOIN departments d ON s.department_id = d.department_id
           WHERE s.enrollment_no LIKE %s OR s.name LIKE %s OR s.course LIKE %s ORDER BY s.student_id"""
    p = f"%{kw.strip()}%"
    with get_db_cursor() as (cursor, conn):
        cursor.execute(q, (p, p, p))
        return cursor.fetchall()

def get_student_by_id(student_id):
    q = """SELECT s.*, d.department_name FROM students s JOIN departments d ON s.department_id = d.department_id WHERE s.student_id = %s"""
    with get_db_cursor() as (cursor, conn):
        cursor.execute(q, (student_id,))
        return cursor.fetchone()

def update_student(student_id, name, email, phone, department_id, course, year, semester):
    q = "UPDATE students SET name=%s, email=%s, phone=%s, department_id=%s, course=%s, year=%s, semester=%s WHERE student_id=%s"
    try:
        with get_db_cursor(commit=True) as (cursor, conn):
            cursor.execute(q, (name, email, phone, department_id, course, year, semester, student_id))
            return True, "Student updated successfully."
    except Error as e:
        return False, f"Database error: {e}"

def delete_student(student_id):
    q = "DELETE FROM students WHERE student_id = %s"
    try:
        with get_db_cursor(commit=True) as (cursor, conn):
            cursor.execute(q, (student_id,))
            return True, "Student record deleted."
    except Error as e:
        return False, f"Database error: {e}"

# --- FACULTY & DEPARTMENT & SUBJECT SERVICES ---
def get_all_departments():
    with get_db_cursor() as (cursor, conn):
        cursor.execute("SELECT * FROM departments ORDER BY department_id")
        return cursor.fetchall()

def add_department(code, name):
    try:
        with get_db_cursor(commit=True) as (cursor, conn):
            cursor.execute("INSERT INTO departments (department_code, department_name) VALUES (%s, %s)", (code.upper(), name))
            return True, "Department added."
    except Error as e:
        return False, f"Error: {e}"

def get_all_subjects():
    q = "SELECT s.*, d.department_name FROM subjects s JOIN departments d ON s.department_id = d.department_id ORDER BY s.semester, s.subject_code"
    with get_db_cursor() as (cursor, conn):
        cursor.execute(q)
        return cursor.fetchall()

def add_subject(code, name, credits, semester, dept_id):
    try:
        with get_db_cursor(commit=True) as (cursor, conn):
            cursor.execute("INSERT INTO subjects (subject_code, subject_name, credits, semester, department_id) VALUES (%s, %s, %s, %s, %s)",
                           (code.upper(), name, credits, semester, dept_id))
            return True, "Subject added successfully."
    except Error as e:
        return False, f"Error: {e}"

# --- MARKS SERVICES ---
def add_or_update_marks(student_id, subject_id, internal, assignment, practical, final, update=False):
    total = round(float(internal) + float(assignment) + float(practical) + float(final), 2)
    grade, gp = calculate_grade_and_point(total)
    
    st = get_student_by_id(student_id)
    if not st: return False, "Student not found."
    
    with get_db_cursor() as (cursor, conn):
        cursor.execute("SELECT semester FROM subjects WHERE subject_id = %s", (subject_id,))
        sub = cursor.fetchone()
        if not sub: return False, "Subject not found."
        semester = sub['semester']

    if update:
        q = """UPDATE marks SET internal_marks=%s, assignment_marks=%s, practical_marks=%s, final_marks=%s, total_marks=%s, grade=%s, grade_point=%s
               WHERE student_id=%s AND subject_id=%s"""
        vals = (internal, assignment, practical, final, total, grade, gp, student_id, subject_id)
    else:
        q = """INSERT INTO marks (student_id, subject_id, internal_marks, assignment_marks, practical_marks, final_marks, total_marks, grade, grade_point, semester)
               VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)"""
        vals = (student_id, subject_id, internal, assignment, practical, final, total, grade, gp, semester)

    try:
        with get_db_cursor(commit=True) as (cursor, conn):
            cursor.execute(q, vals)
            return True, f"Marks recorded. Total: {total}, Grade: {grade} ({gp})"
    except Error as e:
        if e.errno == 1062: return False, "Marks already recorded. Use update option."
        return False, f"Database error: {e}"

def get_marks_by_student(student_id):
    q = """SELECT m.*, sub.subject_code, sub.subject_name, sub.credits
           FROM marks m JOIN subjects sub ON m.subject_id = sub.subject_id
           WHERE m.student_id = %s ORDER BY sub.subject_code"""
    with get_db_cursor() as (cursor, conn):
        cursor.execute(q, (student_id,))
        return cursor.fetchall()

# --- ATTENDANCE SERVICES ---
def record_attendance(student_id, subject_id, classes_held, classes_attended, update=False):
    pct = calculate_attendance_percentage(classes_held, classes_attended)
    with get_db_cursor() as (cursor, conn):
        cursor.execute("SELECT semester FROM subjects WHERE subject_id = %s", (subject_id,))
        sub = cursor.fetchone()
        if not sub: return False, "Subject not found."
        semester = sub['semester']

    if update:
        q = "UPDATE attendance SET classes_held=%s, classes_attended=%s, attendance_percentage=%s WHERE student_id=%s AND subject_id=%s"
        vals = (classes_held, classes_attended, pct, student_id, subject_id)
    else:
        q = "INSERT INTO attendance (student_id, subject_id, classes_held, classes_attended, attendance_percentage, semester) VALUES (%s, %s, %s, %s, %s, %s)"
        vals = (student_id, subject_id, classes_held, classes_attended, pct, semester)

    try:
        with get_db_cursor(commit=True) as (cursor, conn):
            cursor.execute(q, vals)
            warn = " ⚠️ [ATTENDANCE WARNING]" if pct < 75.0 else ""
            return True, f"Attendance saved. Percentage: {pct}%{warn}"
    except Error as e:
        return False, f"Database error: {e}"

def get_attendance_by_student(student_id):
    q = """SELECT a.*, sub.subject_code, sub.subject_name FROM attendance a JOIN subjects sub ON a.subject_id = sub.subject_id WHERE a.student_id = %s"""
    with get_db_cursor() as (cursor, conn):
        cursor.execute(q, (student_id,))
        return cursor.fetchall()

# --- PERFORMANCE REPORT CARD ---
def generate_performance_report_card(student_id):
    st = get_student_by_id(student_id)
    if not st:
        print("❌ Student not found.")
        return

    marks = get_marks_by_student(student_id)
    attendance = get_attendance_by_student(student_id)

    print("\n" + "=" * 65)
    print("              STUDENT PERFORMANCE REPORT CARD              ")
    print("=" * 65)
    print(f"Enrollment  : {st['enrollment_no']}")
    print(f"Name        : {st['name']}")
    print(f"Department  : {st['department_name']}")
    print(f"Course      : {st['course']}")
    print(f"Semester    : {st['semester']}")
    print("-" * 65)

    att_map = {a['subject_id']: a['attendance_percentage'] for a in attendance}
    table_rows = []
    warnings = []

    for m in marks:
        att = att_map.get(m['subject_id'], 0.0)
        table_rows.append([m['subject_code'], m['subject_name'], m['credits'], f"{m['total_marks']:.1f}", m['grade'], f"{m['grade_point']:.1f}", f"{att:.1f}%"])
        if att < 75.0:
            warnings.append(f"{m['subject_code']} - {m['subject_name']}: Attendance is {att:.1f}% (< 75%)")

    print_table(table_rows, headers=["Code", "Subject Name", "Credits", "Marks", "Grade", "GP", "Attendance"])
    print("-" * 65)

    gpa = calculate_gpa(marks)
    total_held = sum(a['classes_held'] for a in attendance)
    total_attended = sum(a['classes_attended'] for a in attendance)
    overall_att = round((total_attended / total_held * 100.0), 2) if total_held > 0 else 0.0
    has_failed = any(m['grade'] == 'F' for m in marks)
    status = determine_performance_status(gpa, overall_att, has_failed)

    print(f"Overall CGPA       : {gpa:.2f}")
    print(f"Overall Attendance : {overall_att:.1f}%")
    print(f"Performance Status : {status}")

    if warnings:
        print("\n⚠️  ATTENDANCE WARNINGS:")
        for w in warnings:
            print(f"  • {w}")
    else:
        print("\n✅ Attendance Status: Satisfactory")
    print("=" * 65 + "\n")

# --- RANKINGS & ANALYTICS ---
def get_rankings(mode='overall', target_id=None):
    if mode == 'overall':
        q = """SELECT s.enrollment_no, s.name, d.department_code, s.semester,
                      COALESCE(ROUND(SUM(m.grade_point * sub.credits) / NULLIF(SUM(sub.credits), 0), 2), 0.00) AS cgpa,
                      RANK() OVER (ORDER BY COALESCE(SUM(m.grade_point * sub.credits) / NULLIF(SUM(sub.credits), 0), 0) DESC) AS rank_no
               FROM students s JOIN departments d ON s.department_id = d.department_id
               LEFT JOIN marks m ON s.student_id = m.student_id LEFT JOIN subjects sub ON m.subject_id = sub.subject_id
               GROUP BY s.student_id HAVING COUNT(m.mark_id) > 0 ORDER BY rank_no ASC"""
        params = ()
    elif mode == 'dept':
        q = """SELECT s.enrollment_no, s.name, d.department_code,
                      COALESCE(ROUND(SUM(m.grade_point * sub.credits) / NULLIF(SUM(sub.credits), 0), 2), 0.00) AS cgpa,
                      RANK() OVER (PARTITION BY s.department_id ORDER BY COALESCE(SUM(m.grade_point * sub.credits) / NULLIF(SUM(sub.credits), 0), 0) DESC) AS rank_no
               FROM students s JOIN departments d ON s.department_id = d.department_id
               LEFT JOIN marks m ON s.student_id = m.student_id LEFT JOIN subjects sub ON m.subject_id = sub.subject_id
               WHERE s.department_id = %s GROUP BY s.student_id HAVING COUNT(m.mark_id) > 0 ORDER BY rank_no ASC"""
        params = (target_id,)
    with get_db_cursor() as (cursor, conn):
        cursor.execute(q, params)
        return cursor.fetchall()

def print_subject_analytics():
    q = """SELECT sub.subject_code, sub.subject_name, COUNT(m.mark_id) AS total_std,
                  ROUND(AVG(m.total_marks), 1) AS avg_m, ROUND(MAX(m.total_marks), 1) AS max_m,
                  ROUND(MIN(m.total_marks), 1) AS min_m,
                  SUM(CASE WHEN m.grade != 'F' THEN 1 ELSE 0 END) AS passed,
                  ROUND((SUM(CASE WHEN m.grade != 'F' THEN 1 ELSE 0 END) / COUNT(m.mark_id)) * 100, 1) AS pass_pct
           FROM subjects sub LEFT JOIN marks m ON sub.subject_id = m.subject_id
           GROUP BY sub.subject_id HAVING total_std > 0 ORDER BY sub.subject_code"""
    with get_db_cursor() as (cursor, conn):
        cursor.execute(q)
        res = cursor.fetchall()
        rows = [[r['subject_code'], r['subject_name'], r['total_std'], r['avg_m'], r['max_m'], r['min_m'], r['passed'], f"{r['pass_pct']}%"] for r in res]
        print_table(rows, headers=["Code", "Subject", "Students", "Avg", "Max", "Min", "Passed", "Pass %"], title="SUBJECT ANALYTICS")

# ==============================================================================
# TERMINAL USER INTERFACES & DASHBOARDS
# ==============================================================================

def pause():
    input("\nPress [Enter] to return to menu...")

def display_menu(title, options):
    print("\n" + "=" * 60)
    print(f"  {title.upper()}")
    print("=" * 60)
    for k, v in options:
        print(f"  {k}. {v}")
    print("=" * 60)

def admin_dashboard(user):
    while True:
        opts = [
            ("1", "Student Management (Add/View/Search/Update/Delete)"),
            ("2", "Subject Management (Add/View)"),
            ("3", "Department Management (Add/View)"),
            ("4", "Marks Management (Add/Update/View)"),
            ("5", "Attendance Management (Record/Update/View)"),
            ("6", "Generate Student Performance Report Card"),
            ("7", "Student Rankings (Overall & Department)"),
            ("8", "Academic Analytics"),
            ("9", "Create User Account"),
            ("0", "Logout")
        ]
        display_menu("ADMIN DASHBOARD", opts)
        ch = input("Select option: ").strip()

        if ch == "1":
            print("\n1. Add Student | 2. View All | 3. Search | 4. Update | 5. Delete")
            c = input("Choice: ").strip()
            if c == "1":
                en = prompt_string("Enrollment No: ")
                nm = prompt_string("Name: ")
                em = prompt_string("Email: ")
                ph = prompt_string("Phone: ", required=False)
                dp = prompt_int("Dept ID: ")
                cs = prompt_string("Course: ")
                yr = prompt_int("Year (1-4): ", 1, 4)
                sm = prompt_int("Semester (1-8): ", 1, 8)
                un = prompt_string("Login Username (optional): ", required=False)
                pw = prompt_string("Login Password (optional): ", required=False)
                s, msg = add_student(en, nm, em, ph, dp, cs, yr, sm, un if un else None, pw if pw else None)
                print("✅" if s else "❌", msg)
            elif c == "2":
                stds = get_all_students()
                rows = [[s['student_id'], s['enrollment_no'], s['name'], s['department_name'], s['course'], s['semester']] for s in stds]
                print_table(rows, headers=["ID", "Enrollment", "Name", "Department", "Course", "Sem"], title="ALL STUDENTS")
            elif c == "3":
                kw = prompt_string("Search Keyword: ")
                stds = search_students(kw)
                rows = [[s['student_id'], s['enrollment_no'], s['name'], s['department_name'], s['course'], s['semester']] for s in stds]
                print_table(rows, headers=["ID", "Enrollment", "Name", "Department", "Course", "Sem"], title=f"SEARCH RESULTS FOR '{kw}'")
            elif c == "4":
                sid = prompt_int("Student ID to Update: ")
                st = get_student_by_id(sid)
                if st:
                    nm = prompt_string(f"Name [{st['name']}]: ", False) or st['name']
                    em = prompt_string(f"Email [{st['email']}]: ", False) or st['email']
                    ph = prompt_string(f"Phone [{st['phone']}]: ", False) or st['phone']
                    dp = prompt_int(f"Dept ID [{st['department_id']}]: ", default=st['department_id'])
                    cs = prompt_string(f"Course [{st['course']}]: ", False) or st['course']
                    yr = prompt_int(f"Year [{st['year']}]: ", 1, 4, st['year'])
                    sm = prompt_int(f"Semester [{st['semester']}]: ", 1, 8, st['semester'])
                    s, msg = update_student(sid, nm, em, ph, dp, cs, yr, sm)
                    print("✅" if s else "❌", msg)
            elif c == "5":
                sid = prompt_int("Student ID to Delete: ")
                s, msg = delete_student(sid)
                print("✅" if s else "❌", msg)
            pause()

        elif ch == "2":
            subs = get_all_subjects()
            rows = [[s['subject_id'], s['subject_code'], s['subject_name'], s['credits'], s['semester'], s['department_name']] for s in subs]
            print_table(rows, headers=["ID", "Code", "Subject Name", "Credits", "Sem", "Department"], title="ALL SUBJECTS")
            print("\nAdd new subject? (y/N)")
            if input().strip().lower() == 'y':
                cd = prompt_string("Subject Code: ")
                nm = prompt_string("Subject Name: ")
                cr = prompt_int("Credits: ", 1, 10)
                sm = prompt_int("Semester: ", 1, 8)
                dp = prompt_int("Dept ID: ")
                s, msg = add_subject(cd, nm, cr, sm, dp)
                print("✅" if s else "❌", msg)
            pause()

        elif ch == "3":
            dps = get_all_departments()
            rows = [[d['department_id'], d['department_code'], d['department_name']] for d in dps]
            print_table(rows, headers=["ID", "Code", "Department Name"], title="ALL DEPARTMENTS")
            print("\nAdd new department? (y/N)")
            if input().strip().lower() == 'y':
                cd = prompt_string("Dept Code: ")
                nm = prompt_string("Dept Name: ")
                s, msg = add_department(cd, nm)
                print("✅" if s else "❌", msg)
            pause()

        elif ch == "4":
            sid = prompt_int("Student ID: ")
            sub_id = prompt_int("Subject ID: ")
            internal = prompt_float("Internal Marks (max 20): ", 0, 20)
            assgn = prompt_float("Assignment Marks (max 10): ", 0, 10)
            prac = prompt_float("Practical Marks (max 20): ", 0, 20)
            final = prompt_float("Final Marks (max 50): ", 0, 50)
            upd = input("Is this an update? (y/N): ").strip().lower() == 'y'
            s, msg = add_or_update_marks(sid, sub_id, internal, assgn, prac, final, update=upd)
            print("✅" if s else "❌", msg)
            pause()

        elif ch == "5":
            sid = prompt_int("Student ID: ")
            sub_id = prompt_int("Subject ID: ")
            held = prompt_int("Classes Held: ", 1)
            att = prompt_int("Classes Attended: ", 0, held)
            upd = input("Is this an update? (y/N): ").strip().lower() == 'y'
            s, msg = record_attendance(sid, sub_id, held, att, update=upd)
            print("✅" if s else "❌", msg)
            pause()

        elif ch == "6":
            sid = prompt_int("Enter Student ID: ")
            generate_performance_report_card(sid)
            pause()

        elif ch == "7":
            ranks = get_rankings('overall')
            rows = [[r['rank_no'], r['enrollment_no'], r['name'], r['department_code'], f"{r['cgpa']:.2f}"] for r in ranks]
            print_table(rows, headers=["Rank", "Enrollment", "Name", "Department", "CGPA"], title="OVERALL STUDENT RANKINGS")
            pause()

        elif ch == "8":
            print_subject_analytics()
            pause()

        elif ch == "9":
            un = prompt_string("Username: ")
            em = prompt_string("Email: ")
            pw = prompt_string("Password: ")
            rl = prompt_string("Role (Admin/Faculty/Student): ")
            s, msg = create_user_account(un, em, pw, rl)
            print("✅ Account created." if s else "❌ Error: " + str(msg))
            pause()

        elif ch == "0":
            break

def faculty_dashboard(user):
    while True:
        opts = [
            ("1", "View Students"),
            ("2", "Record / Update Student Marks"),
            ("3", "Record / Update Student Attendance"),
            ("4", "View Student Report Card"),
            ("5", "Subject Performance Analytics"),
            ("0", "Logout")
        ]
        display_menu("FACULTY DASHBOARD", opts)
        ch = input("Select option: ").strip()

        if ch == "1":
            stds = get_all_students()
            rows = [[s['student_id'], s['enrollment_no'], s['name'], s['department_name'], s['course'], s['semester']] for s in stds]
            print_table(rows, headers=["ID", "Enrollment", "Name", "Department", "Course", "Sem"], title="STUDENTS LIST")
            pause()
        elif ch == "2":
            sid = prompt_int("Student ID: ")
            sub_id = prompt_int("Subject ID: ")
            internal = prompt_float("Internal (0-20): ", 0, 20)
            assgn = prompt_float("Assignment (0-10): ", 0, 10)
            prac = prompt_float("Practical (0-20): ", 0, 20)
            final = prompt_float("Final Exam (0-50): ", 0, 50)
            upd = input("Is update? (y/N): ").strip().lower() == 'y'
            s, msg = add_or_update_marks(sid, sub_id, internal, assgn, prac, final, update=upd)
            print("✅" if s else "❌", msg)
            pause()
        elif ch == "3":
            sid = prompt_int("Student ID: ")
            sub_id = prompt_int("Subject ID: ")
            held = prompt_int("Classes Held: ", 1)
            att = prompt_int("Classes Attended: ", 0, held)
            upd = input("Is update? (y/N): ").strip().lower() == 'y'
            s, msg = record_attendance(sid, sub_id, held, att, update=upd)
            print("✅" if s else "❌", msg)
            pause()
        elif ch == "4":
            sid = prompt_int("Student ID: ")
            generate_performance_report_card(sid)
            pause()
        elif ch == "5":
            print_subject_analytics()
            pause()
        elif ch == "0":
            break

def student_dashboard(user):
    st = None
    with get_db_cursor() as (cursor, conn):
        cursor.execute("SELECT student_id FROM students WHERE user_id = %s", (user['user_id'],))
        res = cursor.fetchone()
        if res: st = res['student_id']

    if not st:
        print("❌ Your account is not linked to a student record.")
        pause()
        return

    while True:
        opts = [
            ("1", "View My Academic Performance Report"),
            ("2", "View My Marks Breakdown"),
            ("3", "View My Attendance"),
            ("4", "Change Password"),
            ("0", "Logout")
        ]
        display_menu("STUDENT DASHBOARD", opts)
        ch = input("Select option: ").strip()

        if ch == "1":
            generate_performance_report_card(st)
            pause()
        elif ch == "2":
            marks = get_marks_by_student(st)
            rows = [[m['subject_code'], m['subject_name'], m['credits'], m['total_marks'], m['grade'], m['grade_point']] for m in marks]
            print_table(rows, headers=["Code", "Subject Name", "Credits", "Marks", "Grade", "GP"], title="MY MARKS")
            pause()
        elif ch == "3":
            att = get_attendance_by_student(st)
            rows = [[a['subject_code'], a['subject_name'], a['classes_held'], a['classes_attended'], f"{a['attendance_percentage']}%"] for a in att]
            print_table(rows, headers=["Code", "Subject Name", "Held", "Attended", "Percentage"], title="MY ATTENDANCE")
            pause()
        elif ch == "4":
            op = prompt_string("Old Password: ")
            np = prompt_string("New Password: ")
            s, msg = change_user_password(user['user_id'], op, np)
            print("✅" if s else "❌", msg)
            pause()
        elif ch == "0":
            break

# ==============================================================================
# MAIN ENTRY POINT
# ==============================================================================

def main():
    print("\n" + "=" * 60)
    print("    STUDENT ACADEMIC PERFORMANCE TRACKER (Python + MySQL CLI)")
    print("=" * 60)
    print("Verifying MySQL connection & initializing database...")
    
    success, msg = init_database(run_seed=True)
    if not success:
        print(f"❌ Failed to connect or initialize MySQL Database: {msg}")
        print("Please check your .env configuration and verify MariaDB/MySQL is running.")
        sys.exit(1)
        
    print("✅ Database connected & initialized.")

    while True:
        opts = [
            ("1", "Login"),
            ("2", "Re-Initialize Database (Run Schema & Seed Data)"),
            ("0", "Exit Application")
        ]
        display_menu("MAIN MENU", opts)
        ch = input("Select option: ").strip()

        if ch == "1":
            print("\n--- USER LOGIN ---")
            un = input("Username / Email : ").strip()
            import getpass
            try:
                pw = getpass.getpass("Password         : ").strip()
            except Exception:
                pw = input("Password         : ").strip()

            if not un or not pw:
                print("❌ Username and password are required.")
                continue

            s, res = authenticate_user(un, pw)
            if not s:
                print(f"❌ Login Failed: {res}")
            else:
                user = res
                print(f"✅ Login successful! Role: {user['role']}")
                if user['role'] == 'Admin':
                    admin_dashboard(user)
                elif user['role'] == 'Faculty':
                    faculty_dashboard(user)
                elif user['role'] == 'Student':
                    student_dashboard(user)
        elif ch == "2":
            if input("Re-seed database? (y/N): ").strip().lower() == 'y':
                s, msg = init_database(run_seed=True)
                print("✅" if s else "❌", msg)
        elif ch == "0":
            print("\nGoodbye!")
            sys.exit(0)

if __name__ == "__main__":
    main()
