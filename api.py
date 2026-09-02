"""
Student Academic Performance Tracker - Production REST API & Sync Engine
Supports offline data synchronization and cloud deployment (Render, Railway, Docker, AWS).
"""

import os
import sys
import logging
from flask import Flask, request, jsonify, send_from_directory
from flask_cors import CORS

import main

app = Flask(__name__, static_folder='android_app', static_url_path='')
CORS(app)

# Ensure Database is initialized on app startup
try:
    main.init_database(run_seed=True)
except Exception as e:
    logging.warning(f"Database init warning on API startup: {e}")

# ==============================================================================
# REST API & OFFLINE SYNC ENDPOINTS
# ==============================================================================

@app.route('/api/health', methods=['GET'])
def health_check():
    return jsonify({
        "status": "online",
        "app": "Student Academic Performance Tracker",
        "version": "1.1.0",
        "database": main.Config.DB_NAME,
        "offline_sync_supported": True
    })

# Batch Sync Endpoint for Offline Mutations
@app.route('/api/sync', methods=['POST'])
def batch_sync():
    """
    Receives an array of offline mutations queued while the app was offline.
    Executes each mutation against the database and returns a sync report.
    """
    data = request.get_json() or {}
    mutations = data.get('mutations', [])
    
    synced_items = []
    failed_items = []

    for item in mutations:
        m_id = item.get('id')
        m_type = item.get('type')
        payload = item.get('payload', {})

        try:
            success = False
            msg = "Unknown mutation type"

            if m_type == 'ADD_STUDENT':
                success, msg = main.add_student(
                    payload.get('enrollment_no'),
                    payload.get('name'),
                    payload.get('email'),
                    payload.get('phone', ''),
                    int(payload.get('department_id', 1)),
                    payload.get('course'),
                    int(payload.get('year', 1)),
                    int(payload.get('semester', 1)),
                    payload.get('username'),
                    payload.get('password')
                )
            elif m_type == 'UPDATE_STUDENT':
                success, msg = main.update_student(
                    int(payload.get('student_id')),
                    payload.get('name'),
                    payload.get('email'),
                    payload.get('phone', ''),
                    int(payload.get('department_id', 1)),
                    payload.get('course'),
                    int(payload.get('year', 1)),
                    int(payload.get('semester', 1))
                )
            elif m_type == 'DELETE_STUDENT':
                success, msg = main.delete_student(int(payload.get('student_id')))
            elif m_type == 'RECORD_MARKS':
                success, msg = main.add_or_update_marks(
                    int(payload.get('student_id')),
                    int(payload.get('subject_id')),
                    float(payload.get('internal_marks', 0)),
                    float(payload.get('assignment_marks', 0)),
                    float(payload.get('practical_marks', 0)),
                    float(payload.get('final_marks', 0)),
                    update=bool(payload.get('is_update', False))
                )
            elif m_type == 'RECORD_ATTENDANCE':
                success, msg = main.record_attendance(
                    int(payload.get('student_id')),
                    int(payload.get('subject_id')),
                    int(payload.get('classes_held', 0)),
                    int(payload.get('classes_attended', 0)),
                    update=bool(payload.get('is_update', False))
                )
            elif m_type == 'ADD_DEPARTMENT':
                success, msg = main.add_department(
                    payload.get('department_code'),
                    payload.get('department_name')
                )
            elif m_type == 'ADD_SUBJECT':
                success, msg = main.add_subject(
                    payload.get('subject_code'),
                    payload.get('subject_name'),
                    int(payload.get('credits', 3)),
                    int(payload.get('semester', 1)),
                    int(payload.get('department_id', 1))
                )

            if success:
                synced_items.append({"id": m_id, "type": m_type, "message": msg})
            else:
                failed_items.append({"id": m_id, "type": m_type, "error": msg})

        except Exception as err:
            failed_items.append({"id": m_id, "type": m_type, "error": str(err)})

    return jsonify({
        "success": True,
        "synced_count": len(synced_items),
        "failed_count": len(failed_items),
        "synced": synced_items,
        "failed": failed_items
    })

@app.route('/api/login', methods=['POST'])
def api_login():
    data = request.get_json() or {}
    username = data.get('username', '').strip()
    password = data.get('password', '').strip()

    if not username or not password:
        return jsonify({"success": False, "message": "Username and password required."}), 400

    success, result = main.authenticate_user(username, password)
    if success:
        return jsonify({"success": True, "user": result})
    else:
        return jsonify({"success": False, "message": result}), 401

@app.route('/api/dashboard', methods=['GET'])
def get_dashboard_summary():
    try:
        students = main.get_all_students()
        departments = main.get_all_departments()
        subjects = main.get_all_subjects()
        rankings = main.get_rankings(mode='overall')

        low_att_count = 0
        with main.get_db_cursor() as (cursor, conn):
            cursor.execute("SELECT COUNT(*) AS cnt FROM attendance WHERE attendance_percentage < 75.0")
            res = cursor.fetchone()
            if res:
                low_att_count = res.get('cnt', 0)

        avg_cgpa = 0.0
        if rankings:
            tot = sum(r.get('cgpa', 0) for r in rankings)
            avg_cgpa = round(tot / len(rankings), 2)

        return jsonify({
            "success": True,
            "summary": {
                "total_students": len(students),
                "total_departments": len(departments),
                "total_subjects": len(subjects),
                "average_cgpa": avg_cgpa,
                "low_attendance_warnings": low_att_count
            }
        })
    except Exception as e:
        return jsonify({"success": False, "message": str(e)}), 500

@app.route('/api/students', methods=['GET'])
def list_students():
    kw = request.args.get('q', '').strip()
    try:
        if kw:
            students = main.search_students(kw)
        else:
            students = main.get_all_students()
        return jsonify({"success": True, "students": students})
    except Exception as e:
        return jsonify({"success": False, "message": str(e)}), 500

@app.route('/api/students/<int:student_id>', methods=['GET'])
def get_student(student_id):
    try:
        student = main.get_student_by_id(student_id)
        if student:
            return jsonify({"success": True, "student": student})
        return jsonify({"success": False, "message": "Student not found."}), 404
    except Exception as e:
        return jsonify({"success": False, "message": str(e)}), 500

@app.route('/api/students', methods=['POST'])
def create_student():
    data = request.get_json() or {}
    try:
        enrollment_no = data.get('enrollment_no', '').strip()
        name = data.get('name', '').strip()
        email = data.get('email', '').strip()
        phone = data.get('phone', '').strip()
        department_id = int(data.get('department_id', 1))
        course = data.get('course', '').strip()
        year = int(data.get('year', 1))
        semester = int(data.get('semester', 1))
        username = data.get('username', '').strip() or None
        password = data.get('password', '').strip() or None

        success, msg = main.add_student(
            enrollment_no, name, email, phone, department_id, course, year, semester, username, password
        )
        return jsonify({"success": success, "message": msg}), (200 if success else 400)
    except Exception as e:
        return jsonify({"success": False, "message": str(e)}), 500

@app.route('/api/students/<int:student_id>', methods=['PUT'])
def update_student(student_id):
    data = request.get_json() or {}
    try:
        name = data.get('name', '').strip()
        email = data.get('email', '').strip()
        phone = data.get('phone', '').strip()
        department_id = int(data.get('department_id', 1))
        course = data.get('course', '').strip()
        year = int(data.get('year', 1))
        semester = int(data.get('semester', 1))

        success, msg = main.update_student(student_id, name, email, phone, department_id, course, year, semester)
        return jsonify({"success": success, "message": msg}), (200 if success else 400)
    except Exception as e:
        return jsonify({"success": False, "message": str(e)}), 500

@app.route('/api/students/<int:student_id>', methods=['DELETE'])
def delete_student(student_id):
    try:
        success, msg = main.delete_student(student_id)
        return jsonify({"success": success, "message": msg}), (200 if success else 400)
    except Exception as e:
        return jsonify({"success": False, "message": str(e)}), 500

@app.route('/api/departments', methods=['GET', 'POST'])
def handle_departments():
    if request.method == 'GET':
        try:
            depts = main.get_all_departments()
            return jsonify({"success": True, "departments": depts})
        except Exception as e:
            return jsonify({"success": False, "message": str(e)}), 500
    else:
        data = request.get_json() or {}
        code = data.get('department_code', '').strip()
        name = data.get('department_name', '').strip()
        success, msg = main.add_department(code, name)
        return jsonify({"success": success, "message": msg}), (200 if success else 400)

@app.route('/api/subjects', methods=['GET', 'POST'])
def handle_subjects():
    if request.method == 'GET':
        try:
            subs = main.get_all_subjects()
            return jsonify({"success": True, "subjects": subs})
        except Exception as e:
            return jsonify({"success": False, "message": str(e)}), 500
    else:
        data = request.get_json() or {}
        try:
            code = data.get('subject_code', '').strip()
            name = data.get('subject_name', '').strip()
            credits = int(data.get('credits', 3))
            semester = int(data.get('semester', 1))
            dept_id = int(data.get('department_id', 1))
            success, msg = main.add_subject(code, name, credits, semester, dept_id)
            return jsonify({"success": success, "message": msg}), (200 if success else 400)
        except Exception as e:
            return jsonify({"success": False, "message": str(e)}), 500

@app.route('/api/marks/<int:student_id>', methods=['GET'])
def get_marks(student_id):
    try:
        marks = main.get_marks_by_student(student_id)
        return jsonify({"success": True, "marks": marks})
    except Exception as e:
        return jsonify({"success": False, "message": str(e)}), 500

@app.route('/api/marks', methods=['POST'])
def record_marks():
    data = request.get_json() or {}
    try:
        student_id = int(data.get('student_id'))
        subject_id = int(data.get('subject_id'))
        internal = float(data.get('internal_marks', 0))
        assignment = float(data.get('assignment_marks', 0))
        practical = float(data.get('practical_marks', 0))
        final = float(data.get('final_marks', 0))
        is_update = bool(data.get('is_update', False))

        success, msg = main.add_or_update_marks(student_id, subject_id, internal, assignment, practical, final, update=is_update)
        return jsonify({"success": success, "message": msg}), (200 if success else 400)
    except Exception as e:
        return jsonify({"success": False, "message": str(e)}), 500

@app.route('/api/attendance/<int:student_id>', methods=['GET'])
def get_attendance(student_id):
    try:
        att = main.get_attendance_by_student(student_id)
        return jsonify({"success": True, "attendance": att})
    except Exception as e:
        return jsonify({"success": False, "message": str(e)}), 500

@app.route('/api/attendance', methods=['POST'])
def record_attendance():
    data = request.get_json() or {}
    try:
        student_id = int(data.get('student_id'))
        subject_id = int(data.get('subject_id'))
        classes_held = int(data.get('classes_held', 0))
        classes_attended = int(data.get('classes_attended', 0))
        is_update = bool(data.get('is_update', False))

        success, msg = main.record_attendance(student_id, subject_id, classes_held, classes_attended, update=is_update)
        return jsonify({"success": success, "message": msg}), (200 if success else 400)
    except Exception as e:
        return jsonify({"success": False, "message": str(e)}), 500

@app.route('/api/report-card/<int:student_id>', methods=['GET'])
def get_report_card(student_id):
    try:
        student = main.get_student_by_id(student_id)
        if not student:
            return jsonify({"success": False, "message": "Student not found."}), 404

        marks = main.get_marks_by_student(student_id)
        attendance = main.get_attendance_by_student(student_id)
        att_map = {a['subject_id']: a['attendance_percentage'] for a in attendance}

        subject_details = []
        warnings = []
        for m in marks:
            att_pct = att_map.get(m['subject_id'], 0.0)
            subject_details.append({
                "subject_code": m['subject_code'],
                "subject_name": m['subject_name'],
                "credits": m['credits'],
                "internal_marks": float(m['internal_marks']),
                "assignment_marks": float(m['assignment_marks']),
                "practical_marks": float(m['practical_marks']),
                "final_marks": float(m['final_marks']),
                "total_marks": float(m['total_marks']),
                "grade": m['grade'],
                "grade_point": float(m['grade_point']),
                "attendance_percentage": float(att_pct),
                "is_low_attendance": att_pct < 75.0
            })
            if att_pct < 75.0:
                warnings.append(f"{m['subject_code']} - {m['subject_name']} attendance is {att_pct:.1f}% (< 75%)")

        cgpa = main.calculate_gpa(marks)
        total_held = sum(a['classes_held'] for a in attendance)
        total_attended = sum(a['classes_attended'] for a in attendance)
        overall_att = round((total_attended / total_held * 100.0), 2) if total_held > 0 else 0.0
        has_failed = any(m['grade'] == 'F' for m in marks)
        status = main.determine_performance_status(cgpa, overall_att, has_failed)

        return jsonify({
            "success": True,
            "student": student,
            "subjects": subject_details,
            "overall_cgpa": cgpa,
            "overall_attendance": overall_att,
            "status": status,
            "warnings": warnings
        })
    except Exception as e:
        return jsonify({"success": False, "message": str(e)}), 500

@app.route('/api/rankings', methods=['GET'])
def get_rankings():
    mode = request.args.get('mode', 'overall')
    dept_id = request.args.get('department_id')
    try:
        rankings = main.get_rankings(mode=mode, target_id=int(dept_id) if dept_id else None)
        return jsonify({"success": True, "rankings": rankings})
    except Exception as e:
        return jsonify({"success": False, "message": str(e)}), 500

@app.route('/api/analytics', methods=['GET'])
def get_analytics():
    try:
        q = """SELECT sub.subject_code, sub.subject_name, COUNT(m.mark_id) AS total_students,
                      ROUND(AVG(m.total_marks), 1) AS avg_marks, ROUND(MAX(m.total_marks), 1) AS max_marks,
                      ROUND(MIN(m.total_marks), 1) AS min_marks,
                      SUM(CASE WHEN m.grade != 'F' THEN 1 ELSE 0 END) AS passed_students,
                      ROUND((SUM(CASE WHEN m.grade != 'F' THEN 1 ELSE 0 END) / COUNT(m.mark_id)) * 100, 1) AS pass_percentage
               FROM subjects sub LEFT JOIN marks m ON sub.subject_id = m.subject_id
               GROUP BY sub.subject_id HAVING total_students > 0 ORDER BY sub.subject_code"""
        with main.get_db_cursor() as (cursor, conn):
            cursor.execute(q)
            res = cursor.fetchall()
            return jsonify({"success": True, "analytics": res})
    except Exception as e:
        return jsonify({"success": False, "message": str(e)}), 500

# Serve Static Web App
@app.route('/')
def serve_android_app():
    return send_from_directory('android_app', 'index.html')

@app.route('/<path:path>')
def serve_static(path):
    return send_from_directory('android_app', path)

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    print(f"🚀 Starting Student Tracker Server on http://0.0.0.0:{port}")
    app.run(host='0.0.0.0', port=port, debug=True)
