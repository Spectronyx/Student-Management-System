# Student Academic Performance Tracker

A lightweight, powerful **Student Academic Performance Tracker** CLI application built using **Pure Python 3** and **Pure MySQL / MariaDB** in a single file (`main.py`).

---

## 📌 Overview

This project provides a complete command-line interface (CLI) for managing students, faculty, departments, subjects, marks, attendance, rankings, and academic analytics for educational institutions.

---

## ✨ Features

1. **Single-File Pure Python & SQL Design**: All business logic, database initialization, schema DDL, seed data, and CLI menus are cleanly implemented in `main.py` without any web frameworks.
2. **Student Management**: Add, View, Search, Update, and Delete student records with validation.
3. **Marks Management & Centralized Grading**:
   - Component-wise entry: Internal (max 20), Assignment (max 10), Practical (max 20), Final Exam (max 50).
   - Grade mapping: 90-100 (`A+`), 80-89 (`A`), 70-79 (`B+`), 60-69 (`B`), 50-59 (`C`), 40-49 (`D`), <40 (`F`).
4. **Attendance Management**: Calculates percentage `(attended / held) * 100` and flags **"Attendance Warning"** for values < 75%.
5. **GPA / CGPA Calculation**: $\text{GPA} = \frac{\sum (\text{Grade Point} \times \text{Credits})}{\sum \text{Credits}}$ and status evaluation (`Excellent`, `Good`, `Average`, `Needs Improvement`, `At Risk`).
6. **SQL Rankings**: Overall and Department-wise student rankings using MySQL window function `RANK() OVER (...)`.
7. **Academic Analytics**: Subject pass/fail statistics, pass percentages, department averages, low attendance warning lists.
8. **Role-Based Authentication**: Admin, Faculty, and Student accounts secured with `bcrypt` / SHA-256 password hashing.

---

## 📁 File Structure

```text
Student-Management-System/
├── main.py                     # Single self-contained Python CLI application
├── requirements.txt            # Python dependencies (mysql-connector-python, bcrypt, python-dotenv)
├── .env                        # Local database credentials
├── .env.example                # Environment variables template
└── README.md                   # Documentation
```

---

## 🔑 Demo Credentials

| Role | Username | Email | Password |
| :--- | :--- | :--- | :--- |
| **Admin** | `admin` | `admin@tracker.edu` | `admin123` |
| **Faculty** | `prof_rajesh` | `rajesh.sharma@tracker.edu` | `faculty123` |
| **Student** | `std_rahul` | `rahul.kumar@tracker.edu` | `student123` |

---

## 🚀 Quick Start Guide

### 1. Install Dependencies
```bash
python3 -m venv venv
source venv/bin/activate
pip install mysql-connector-python bcrypt python-dotenv
```

### 2. Configure Database Credentials (`.env`)
```env
DB_HOST=127.0.0.1
DB_PORT=3306
DB_NAME=student_academic_tracker
DB_USER=tracker_user
DB_PASSWORD=tracker_pass
DB_SOCKET=/tmp/mariadb.sock
```

### 3. Run Application
```bash
python3 main.py
```
*(The application automatically creates the MySQL database `student_academic_tracker`, initializes tables and indexes, and seeds sample data on startup).*
