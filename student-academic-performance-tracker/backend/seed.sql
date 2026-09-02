-- MySQL Seed Data for Student Academic Performance Tracker

-- 1. DEPARTMENTS
INSERT INTO departments (department_id, department_code, department_name) VALUES
(1, 'CS', 'Computer Science and Engineering'),
(2, 'EC', 'Electronics and Communication Engineering'),
(3, 'IT', 'Information Technology')
ON DUPLICATE KEY UPDATE department_name=VALUES(department_name);

-- 2. USERS
-- Passwords:
-- admin / admin123 -> $2b$12$mHJ9jpWyU0B1TbD5Qk3hVOZnNviG4QfNz36DZM4AwHo70Zgv9VoPG
-- faculty / faculty123 -> $2b$12$auupoQdA2vwRvgiLLmRKRuVMmtJHqKahCCUlzdk.Ns7VSFl.D.fzm
-- student / student123 -> $2b$12$XBSFSX0O8jpc5RrGTrbTSuXr9yuzQ/tTCgjulKbQTYuKHGlEqrHUu

INSERT INTO users (user_id, username, email, password_hash, role, name) VALUES
-- Admin
(1, 'admin', 'admin@tracker.edu', '$2b$12$mHJ9jpWyU0B1TbD5Qk3hVOZnNviG4QfNz36DZM4AwHo70Zgv9VoPG', 'Admin', 'System Administrator'),

-- Faculty
(2, 'prof_sharma', 'sharma@tracker.edu', '$2b$12$auupoQdA2vwRvgiLLmRKRuVMmtJHqKahCCUlzdk.Ns7VSFl.D.fzm', 'Faculty', 'Prof. Rajesh Sharma'),
(3, 'prof_gupta', 'gupta@tracker.edu', '$2b$12$auupoQdA2vwRvgiLLmRKRuVMmtJHqKahCCUlzdk.Ns7VSFl.D.fzm', 'Faculty', 'Dr. Amit Gupta'),
(4, 'prof_verma', 'verma@tracker.edu', '$2b$12$auupoQdA2vwRvgiLLmRKRuVMmtJHqKahCCUlzdk.Ns7VSFl.D.fzm', 'Faculty', 'Prof. Sunita Verma'),
(5, 'prof_rao', 'rao@tracker.edu', '$2b$12$auupoQdA2vwRvgiLLmRKRuVMmtJHqKahCCUlzdk.Ns7VSFl.D.fzm', 'Faculty', 'Dr. K. S. Rao'),
(6, 'prof_patel', 'patel@tracker.edu', '$2b$12$auupoQdA2vwRvgiLLmRKRuVMmtJHqKahCCUlzdk.Ns7VSFl.D.fzm', 'Faculty', 'Prof. Neha Patel'),

-- Students (1-20)
(7, 'student1', 'rahul.sharma@student.edu', '$2b$12$XBSFSX0O8jpc5RrGTrbTSuXr9yuzQ/tTCgjulKbQTYuKHGlEqrHUu', 'Student', 'Rahul Sharma'),
(8, 'student2', 'priya.singh@student.edu', '$2b$12$XBSFSX0O8jpc5RrGTrbTSuXr9yuzQ/tTCgjulKbQTYuKHGlEqrHUu', 'Student', 'Priya Singh'),
(9, 'student3', 'amit.kumar@student.edu', '$2b$12$XBSFSX0O8jpc5RrGTrbTSuXr9yuzQ/tTCgjulKbQTYuKHGlEqrHUu', 'Student', 'Amit Kumar'),
(10, 'student4', 'sneha.patel@student.edu', '$2b$12$XBSFSX0O8jpc5RrGTrbTSuXr9yuzQ/tTCgjulKbQTYuKHGlEqrHUu', 'Student', 'Sneha Patel'),
(11, 'student5', 'vikram.aditya@student.edu', '$2b$12$XBSFSX0O8jpc5RrGTrbTSuXr9yuzQ/tTCgjulKbQTYuKHGlEqrHUu', 'Student', 'Vikram Aditya'),
(12, 'student6', 'ananya.roy@student.edu', '$2b$12$XBSFSX0O8jpc5RrGTrbTSuXr9yuzQ/tTCgjulKbQTYuKHGlEqrHUu', 'Student', 'Ananya Roy'),
(13, 'student7', 'rohan.mehta@student.edu', '$2b$12$XBSFSX0O8jpc5RrGTrbTSuXr9yuzQ/tTCgjulKbQTYuKHGlEqrHUu', 'Student', 'Rohan Mehta'),
(14, 'student8', 'kavya.nair@student.edu', '$2b$12$XBSFSX0O8jpc5RrGTrbTSuXr9yuzQ/tTCgjulKbQTYuKHGlEqrHUu', 'Student', 'Kavya Nair'),
(15, 'student9', 'aditya.verma@student.edu', '$2b$12$XBSFSX0O8jpc5RrGTrbTSuXr9yuzQ/tTCgjulKbQTYuKHGlEqrHUu', 'Student', 'Aditya Verma'),
(16, 'student10', 'pooja.joshi@student.edu', '$2b$12$XBSFSX0O8jpc5RrGTrbTSuXr9yuzQ/tTCgjulKbQTYuKHGlEqrHUu', 'Student', 'Pooja Joshi'),
(17, 'student11', 'siddharth.rao@student.edu', '$2b$12$XBSFSX0O8jpc5RrGTrbTSuXr9yuzQ/tTCgjulKbQTYuKHGlEqrHUu', 'Student', 'Siddharth Rao'),
(18, 'student12', 'divya.reddy@student.edu', '$2b$12$XBSFSX0O8jpc5RrGTrbTSuXr9yuzQ/tTCgjulKbQTYuKHGlEqrHUu', 'Student', 'Divya Reddy'),
(19, 'student13', 'manish.choudhary@student.edu', '$2b$12$XBSFSX0O8jpc5RrGTrbTSuXr9yuzQ/tTCgjulKbQTYuKHGlEqrHUu', 'Student', 'Manish Choudhary'),
(20, 'student14', 'shweta.deshmukh@student.edu', '$2b$12$XBSFSX0O8jpc5RrGTrbTSuXr9yuzQ/tTCgjulKbQTYuKHGlEqrHUu', 'Student', 'Shweta Deshmukh'),
(21, 'student15', 'tarun.bhatia@student.edu', '$2b$12$XBSFSX0O8jpc5RrGTrbTSuXr9yuzQ/tTCgjulKbQTYuKHGlEqrHUu', 'Student', 'Tarun Bhatia'),
(22, 'student16', 'ishita.saxena@student.edu', '$2b$12$XBSFSX0O8jpc5RrGTrbTSuXr9yuzQ/tTCgjulKbQTYuKHGlEqrHUu', 'Student', 'Ishita Saxena'),
(23, 'student17', 'deepak.mishra@student.edu', '$2b$12$XBSFSX0O8jpc5RrGTrbTSuXr9yuzQ/tTCgjulKbQTYuKHGlEqrHUu', 'Student', 'Deepak Mishra'),
(24, 'student18', 'ritika.khanna@student.edu', '$2b$12$XBSFSX0O8jpc5RrGTrbTSuXr9yuzQ/tTCgjulKbQTYuKHGlEqrHUu', 'Student', 'Ritika Khanna'),
(25, 'student19', 'varun.nambiar@student.edu', '$2b$12$XBSFSX0O8jpc5RrGTrbTSuXr9yuzQ/tTCgjulKbQTYuKHGlEqrHUu', 'Student', 'Varun Nambiar'),
(26, 'student20', 'megha.kapoor@student.edu', '$2b$12$XBSFSX0O8jpc5RrGTrbTSuXr9yuzQ/tTCgjulKbQTYuKHGlEqrHUu', 'Student', 'Megha Kapoor')
ON DUPLICATE KEY UPDATE name=VALUES(name);

-- 3. FACULTY
INSERT INTO faculty (faculty_id, user_id, employee_id, name, email, phone, department_id, hire_date) VALUES
(1, 2, 'FAC101', 'Prof. Rajesh Sharma', 'sharma@tracker.edu', '+919876500001', 1, '2018-06-15'),
(2, 3, 'FAC102', 'Dr. Amit Gupta', 'gupta@tracker.edu', '+919876500002', 1, '2019-08-01'),
(3, 4, 'FAC103', 'Prof. Sunita Verma', 'verma@tracker.edu', '+919876500003', 2, '2020-01-10'),
(4, 5, 'FAC104', 'Dr. K. S. Rao', 'rao@tracker.edu', '+919876500004', 2, '2017-04-20'),
(5, 6, 'FAC105', 'Prof. Neha Patel', 'patel@tracker.edu', '+919876500005', 3, '2021-09-15')
ON DUPLICATE KEY UPDATE name=VALUES(name);

-- 4. STUDENTS
INSERT INTO students (student_id, user_id, enrollment_number, first_name, last_name, email, phone, department_id, course, year, semester, admission_date) VALUES
(1, 7, 'CS2026001', 'Rahul', 'Sharma', 'rahul.sharma@student.edu', '+919811100001', 1, 'B.Tech CS', 3, 5, '2023-08-01'),
(2, 8, 'CS2026002', 'Priya', 'Singh', 'priya.singh@student.edu', '+919811100002', 1, 'B.Tech CS', 3, 5, '2023-08-01'),
(3, 9, 'CS2026003', 'Amit', 'Kumar', 'amit.kumar@student.edu', '+919811100003', 1, 'B.Tech CS', 3, 5, '2023-08-01'),
(4, 10, 'CS2026004', 'Sneha', 'Patel', 'sneha.patel@student.edu', '+919811100004', 1, 'B.Tech CS', 3, 5, '2023-08-01'),
(5, 11, 'CS2026005', 'Vikram', 'Aditya', 'vikram.aditya@student.edu', '+919811100005', 1, 'B.Tech CS', 3, 5, '2023-08-01'),
(6, 12, 'CS2026006', 'Ananya', 'Roy', 'ananya.roy@student.edu', '+919811100006', 1, 'B.Tech CS', 3, 5, '2023-08-01'),
(7, 13, 'CS2026007', 'Rohan', 'Mehta', 'rohan.mehta@student.edu', '+919811100007', 1, 'B.Tech CS', 3, 5, '2023-08-01'),
(8, 14, 'EC2026001', 'Kavya', 'Nair', 'kavya.nair@student.edu', '+919822200001', 2, 'B.Tech EC', 3, 5, '2023-08-01'),
(9, 15, 'EC2026002', 'Aditya', 'Verma', 'aditya.verma@student.edu', '+919822200002', 2, 'B.Tech EC', 3, 5, '2023-08-01'),
(10, 16, 'EC2026003', 'Pooja', 'Joshi', 'pooja.joshi@student.edu', '+919822200003', 2, 'B.Tech EC', 3, 5, '2023-08-01'),
(11, 17, 'EC2026004', 'Siddharth', 'Rao', 'siddharth.rao@student.edu', '+919822200004', 2, 'B.Tech EC', 3, 5, '2023-08-01'),
(12, 18, 'EC2026005', 'Divya', 'Reddy', 'divya.reddy@student.edu', '+919822200005', 2, 'B.Tech EC', 3, 5, '2023-08-01'),
(13, 19, 'IT2026001', 'Manish', 'Choudhary', 'manish.choudhary@student.edu', '+919833300001', 3, 'B.Tech IT', 3, 5, '2023-08-01'),
(14, 20, 'IT2026002', 'Shweta', 'Deshmukh', 'shweta.deshmukh@student.edu', '+919833300002', 3, 'B.Tech IT', 3, 5, '2023-08-01'),
(15, 21, 'IT2026003', 'Tarun', 'Bhatia', 'tarun.bhatia@student.edu', '+919833300003', 3, 'B.Tech IT', 3, 5, '2023-08-01'),
(16, 22, 'IT2026004', 'Ishita', 'Saxena', 'ishita.saxena@student.edu', '+919833300004', 3, 'B.Tech IT', 3, 5, '2023-08-01'),
(17, 23, 'IT2026005', 'Deepak', 'Mishra', 'deepak.mishra@student.edu', '+919833300005', 3, 'B.Tech IT', 3, 5, '2023-08-01'),
(18, 24, 'CS2026008', 'Ritika', 'Khanna', 'ritika.khanna@student.edu', '+919811100008', 1, 'B.Tech CS', 2, 3, '2024-08-01'),
(19, 25, 'EC2026006', 'Varun', 'Nambiar', 'varun.nambiar@student.edu', '+919822200006', 2, 'B.Tech EC', 2, 3, '2024-08-01'),
(20, 26, 'IT2026006', 'Megha', 'Kapoor', 'megha.kapoor@student.edu', '+919833300006', 3, 'B.Tech IT', 2, 3, '2024-08-01')
ON DUPLICATE KEY UPDATE first_name=VALUES(first_name);

-- 5. SUBJECTS
INSERT INTO subjects (subject_id, subject_code, subject_name, department_id, semester, credits) VALUES
(1, 'CS501', 'Data Structures & Algorithms', 1, 5, 4),
(2, 'CS502', 'Database Management Systems', 1, 5, 4),
(3, 'CS503', 'Operating Systems', 1, 5, 3),
(4, 'CS504', 'Computer Networks', 1, 5, 3),
(5, 'EC501', 'Digital Signal Processing', 2, 5, 4),
(6, 'EC502', 'Microprocessors & Microcontrollers', 2, 5, 4),
(7, 'IT501', 'Web Technologies & Frameworks', 3, 5, 4),
(8, 'IT502', 'Software Engineering & Agile', 3, 5, 3)
ON DUPLICATE KEY UPDATE subject_name=VALUES(subject_name);

-- 6. FACULTY_SUBJECTS
INSERT INTO faculty_subjects (faculty_id, subject_id) VALUES
(1, 1), (1, 3), -- Prof. Sharma -> DSA, OS
(2, 2), (2, 4), -- Dr. Gupta -> DBMS, CN
(3, 5),         -- Prof. Verma -> DSP
(4, 6),         -- Dr. Rao -> Microprocessors
(5, 7), (5, 8)  -- Prof. Patel -> Web Tech, Software Eng
ON DUPLICATE KEY UPDATE faculty_id=VALUES(faculty_id);

-- 7. MARKS RECORDS
-- Student 1 (Rahul Sharma - CS)
INSERT INTO marks (student_id, subject_id, semester, internal_marks, assignment_marks, practical_marks, final_exam_marks, total_marks, grade, grade_point) VALUES
(1, 1, 5, 28.0, 18.0, 20.0, 45.0, 91.0, 'A+', 10),
(1, 2, 5, 25.0, 17.0, 18.0, 42.0, 84.0, 'A', 9),
(1, 3, 5, 22.0, 15.0, 16.0, 38.0, 76.0, 'B+', 8),
(1, 4, 5, 26.0, 16.0, 17.0, 40.0, 81.0, 'A', 9),

-- Student 2 (Priya Singh - CS)
(2, 1, 5, 29.0, 19.0, 20.0, 47.0, 95.0, 'A+', 10),
(2, 2, 5, 27.0, 18.0, 19.0, 44.0, 88.0, 'A', 9),
(2, 3, 5, 25.0, 17.0, 18.0, 42.0, 82.0, 'A', 9),
(2, 4, 5, 28.0, 18.0, 19.0, 45.0, 90.0, 'A+', 10),

-- Student 3 (Amit Kumar - CS)
(3, 1, 5, 20.0, 14.0, 15.0, 32.0, 63.0, 'B', 7),
(3, 2, 5, 18.0, 12.0, 14.0, 30.0, 56.0, 'C', 6),
(3, 3, 5, 15.0, 10.0, 12.0, 28.0, 47.0, 'D', 5),
(3, 4, 5, 21.0, 14.0, 15.0, 34.0, 64.0, 'B', 7),

-- Student 8 (Kavya Nair - EC)
(8, 5, 5, 27.0, 18.0, 19.0, 43.0, 87.0, 'A', 9),
(8, 6, 5, 26.0, 17.0, 18.0, 41.0, 82.0, 'A', 9),

-- Student 13 (Manish Choudhary - IT)
(13, 7, 5, 28.0, 18.0, 19.0, 44.0, 89.0, 'A', 9),
(13, 8, 5, 25.0, 16.0, 17.0, 40.0, 78.0, 'B+', 8)
ON DUPLICATE KEY UPDATE total_marks=VALUES(total_marks);

-- 8. ATTENDANCE RECORDS
INSERT INTO attendance (student_id, subject_id, semester, classes_held, classes_attended, attendance_percentage) VALUES
-- Student 1 (Rahul Sharma)
(1, 1, 5, 40, 37, 92.50),
(1, 2, 5, 42, 37, 88.10),
(1, 3, 5, 40, 29, 72.50), -- warning threshold < 75%
(1, 4, 5, 38, 33, 86.84),

-- Student 2 (Priya Singh)
(2, 1, 5, 40, 39, 97.50),
(2, 2, 5, 42, 40, 95.24),
(2, 3, 5, 40, 36, 90.00),
(2, 4, 5, 38, 35, 92.11),

-- Student 3 (Amit Kumar)
(3, 1, 5, 40, 28, 70.00), -- warning threshold < 75%
(3, 2, 5, 42, 29, 69.05), -- warning threshold < 75%
(3, 3, 5, 40, 25, 62.50), -- warning threshold < 75%
(3, 4, 5, 38, 30, 78.95),

-- Student 8 (Kavya Nair)
(8, 5, 5, 45, 42, 93.33),
(8, 6, 5, 40, 36, 90.00),

-- Student 13 (Manish Choudhary)
(13, 7, 5, 40, 38, 95.00),
(13, 8, 5, 35, 32, 91.43)
ON DUPLICATE KEY UPDATE attendance_percentage=VALUES(attendance_percentage);
