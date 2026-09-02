# System Architecture & Technical Specifications

## 1. Overview

The **Student Management System** is a modular, multi-tiered enterprise Python application backed by a fully normalized **MySQL** database. It adheres to strict software design patterns, decoupling user interaction (`UI`), business rules (`Services`), database querying (`Repositories`), and schema management (`Database Connection`).

---

## 2. Multi-Layer Architecture

```
+-------------------------------------------------------------------+
|                        USER INTERFACE LAYER                       |
|          (LoginUI, AdminMenu, TeacherMenu, StudentMenu)           |
+-------------------------------------------------------------------+
                                  |
                                  v
+-------------------------------------------------------------------+
|                       BUSINESS LOGIC SERVICES                     |
| (AuthenticationService, StudentService, CourseService,            |
|  AttendanceService, ExaminationService, FeeService)              |
+-------------------------------------------------------------------+
                                  |
                                  v
+-------------------------------------------------------------------+
|                        REPOSITORY SQL LAYER                       |
| (UserRepository, StudentRepository, CourseRepository,             |
|  AttendanceRepository, MarksRepository, FeeRepository)            |
+-------------------------------------------------------------------+
                                  |
                                  v
+-------------------------------------------------------------------+
|                       MYSQL DATABASE ENGINE                       |
|   (users, students, teachers, courses, attendance, marks, fees)   |
+-------------------------------------------------------------------+
```

### Layer Responsibilities

1. **UI Layer (`ui/`)**:
   - Manages CLI interaction, menu rendering, user prompts, input masks, and output tables.
   - Enforces role-based menu visibility (`Admin`, `Teacher`, `Student`).
   - Translates exceptions into clear terminal notifications without crashing the process.

2. **Services Layer (`services/`)**:
   - Encapsulates domain logic, validation pipelines, transaction orchestration, and grading/percentage logic.
   - Coordinates cross-repository operations (e.g. creating a `User` account + `Student` record + `Enrollment` inside a single database transaction).

3. **Repositories Layer (`repositories/`)**:
   - Handles all direct SQL interaction using parameterized statements (`%s`).
   - Prevents SQL injection vulnerabilities completely.
   - Implements SQL aggregate queries, JOINs, GROUP BYs, subqueries, and window/case expressions.

4. **Database Connection Layer (`database/`)**:
   - Provides connection pooling, automatic failover between `mysql-connector` and `pymysql`, and SSL support.
   - Supplies an explicit `db_manager.transaction()` context manager for atomic commit/rollback workflows.

---

## 3. Database Entity Relationship (ER) & Schema Design

The MySQL schema (`database/schema.sql`) consists of **12 normalized tables**:

- **`users`**: Central authentication store (user_id PK, username UNIQUE, password_hash, role, email).
- **`departments`**: Academic departments (department_id PK, department_code UNIQUE, department_name).
- **`courses`**: Academic degree programs (course_id PK, course_code UNIQUE, department_id FK, credits).
- **`teachers`**: Faculty members (teacher_id PK, user_id FK UNIQUE, department_id FK).
- **`students`**: Enrolled students (student_id PK, user_id FK UNIQUE, roll_number UNIQUE, department_id FK, course_id FK, semester).
- **`subjects`**: Course curriculum subjects (subject_id PK, course_id FK, semester, credits).
- **`enrollments`**: Junction table for student course enrollments (enrollment_id PK, student_id FK, course_id FK, semester).
- **`attendance`**: Daily attendance tracking (attendance_id PK, student_id FK, course_id FK, date, status).
- **`examinations`**: Registered exams (exam_id PK, course_id FK, semester, total_marks).
- **`marks`**: Subject examination results (mark_id PK, exam_id FK, subject_id FK, student_id FK, marks_obtained, grade).
- **`fees`**: Tuition fee invoices (fee_id PK, student_id FK, semester, total_amount, due_date, status).
- **`payments`**: Payment ledger transactions (payment_id PK, fee_id FK, amount_paid, payment_date, transaction_ref).

---

## 4. Security Architecture

1. **Password Hashing**:
   - Passwords are encrypted using **PBKDF2 HMAC SHA-256** with 100,000 iterations and a unique salt.
   - Plaintext passwords are never logged, displayed, or saved to storage.

2. **SQL Injection Defense**:
   - 100% of database queries execute via parameterized placeholders (`%s`).
   - String concatenation of raw user input inside SQL query strings is strictly prohibited.

3. **Transaction Safety**:
   - Financial payments and student enrollment workflows wrap multi-query sequences in atomic transaction blocks (`COMMIT` on success, `ROLLBACK` on exception).
