# 🎓 Complete Student Management System (Python 3 + MySQL)

A complete, production-grade **Student Management System** built with **Python 3** and **MySQL**, designed using clean **Object-Oriented Programming (OOP)** and a strict **Multi-Layered Architecture** (`UI → Services → Repositories → Database`).

---

## 🌟 Key Features

### 👤 Role-Based Authentication & Authorization
- **Admin**: Full administrative privileges over students, faculty, departments, courses, exams, fees, and system telemetry reports.
- **Teacher**: Manage attendance, record/update subject examination marks, search students, and generate result cards.
- **Student**: Self-service portal to view personal profile, attendance breakdown %, exam marks, and fee payment balances.

### 📚 Student Management
- Complete CRUD operations (Add, View All, Search, View Profile, Update, Delete).
- Automatic creation of linked `user` login credentials upon student registration inside an **atomic database transaction**.
- Captures Roll Number, Name, DOB, Gender, Email, Phone, Address, Department, Course, Semester, and Admission Date.

### 🏢 Department & Course Management
- Add & View Departments and Course Degree Programs.
- Add Subjects with specific semester assignments and credit values.
- Track course credits and department allocations.

### 📅 Attendance Management
- Mark & Update daily attendance (`Present`, `Absent`, `Late`, `Excused`).
- Dynamic attendance percentage calculation: $\text{Attendance } \% = \frac{\text{Classes Attended}}{\text{Total Classes}} \times 100$.
- Automated **Low Attendance Defaulter Alerts** identifying students below the **75% threshold**.

### 📝 Examination & Marks Management
- Register examinations (e.g., Mid-Term, Final Semesters).
- Enter & update subject marks (0 – 100).
- **Centralized Grading Logic**:
  - `90% - 100%`: **A+**
  - `80% - 89%`: **A**
  - `70% - 79%`: **B+**
  - `60% - 69%`: **B**
  - `50% - 59%`: **C**
  - `40% - 49%`: **D**
  - `< 40%`: **F (Failed)**
- Instant printable **Result Card** generation with subject breakdown, total, percentage, and overall pass/fail status.

### 💳 Fees & Payment Management
- Invoicing tuition fees per semester and academic year.
- Process partial or full fee payments with automatic status transitions (`Pending` ➔ `Partial` ➔ `Paid`).
- Atomic transaction processing ensuring ledger integrity.
- Real-time **Financial Summary Telemetry** (Total Receivable, Total Collected, Outstanding Pending Balance).

---

## 📁 Folder & Architecture Structure

```
Student-Management-System/
│
├── main.py                         # Application Bootstrap & Main Runner
├── config.py                       # Configuration & Environment Variables
├── requirements.txt                # Python Dependencies
├── README.md                       # Comprehensive System Documentation
│
├── database/
│   ├── connection.py               # DatabaseManager & Connection Pool
│   └── schema.sql                  # MySQL Normalized Schema & Seed Data
│
├── models/                         # Dataclass Domain Models
│   ├── user.py
│   ├── student.py
│   ├── teacher.py
│   ├── course.py
│   ├── attendance.py
│   ├── examination.py
│   └── fees.py
│
├── repositories/                   # Parameterized SQL Data Access Layer
│   ├── base_repository.py
│   ├── user_repository.py
│   ├── student_repository.py
│   ├── teacher_repository.py
│   ├── course_repository.py
│   ├── attendance_repository.py
│   ├── marks_repository.py
│   └── fee_repository.py
│
├── services/                       # Domain Logic & Transaction Services
│   ├── authentication_service.py
│   ├── student_service.py
│   ├── course_service.py
│   ├── attendance_service.py
│   ├── examination_service.py
│   └── fee_service.py
│
├── ui/                             # Terminal Menu User Interface
│   ├── login.py
│   ├── admin_menu.py
│   ├── teacher_menu.py
│   ├── student_menu.py
│   └── common.py
│
├── utils/                          # Security, Validators & Helpers
│   ├── validators.py
│   ├── security.py
│   └── helpers.py
│
├── tests/                          # Automated Unit Test Suite
│   └── test_system.py
│
└── docs/                           # Architectural Documentation
    └── architecture.md
```

---

## 🔑 Demo Credentials

| Role | Username | Password | Permissions |
| :--- | :--- | :--- | :--- |
| **Admin** | `admin` | `admin123` | Full System Access |
| **Teacher** | `prof_sharma` | `teacher123` | Attendance, Marks, Academic Reports |
| **Student** | `student1` | `student123` | Personal Profile, Attendance, Marks, Fees |

---

## 🚀 Setup & Execution Instructions

### 1. Prerequisites
- **Python 3.10+**
- **MySQL / MariaDB Server**

### 2. Environment Configuration
Create or edit `.env` in the root project directory:
```env
DB_HOST=localhost
DB_PORT=3306
DB_USER=root
DB_PASSWORD=your_password
DB_NAME=student_management
DB_SSL=false
SECRET_KEY=super_secret_student_management_key_2026
PASSWORD_SALT=sms_salt_2026
ATTENDANCE_THRESHOLD=75.0
```

### 3. Install Dependencies
```bash
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

### 4. Run Application
```bash
python main.py
```
*The application will automatically connect to MySQL, verify tables, and sync seed data on startup!*

### 5. Run Automated Unit Tests
```bash
python -m unittest tests/test_system.py
```

---

## 🔒 Security Highlights

1. **PBKDF2 Password Hashing**: Passwords are securely hashed with PBKDF2 HMAC SHA-256 (100,000 rounds) + Salt. Plaintext passwords are never stored.
2. **Parameterized SQL Queries**: 100% of SQL statements use `%s` placeholders, completely preventing SQL Injection.
3. **Database Transactions**: Financial payments and student creation execute inside `db_manager.transaction()` blocks with automatic `COMMIT` / `ROLLBACK`.
