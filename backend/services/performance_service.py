from database import fetch_all, fetch_one
from services.gpa_service import calculate_gpa

def get_student_performance_summary(student_id: int) -> dict:
    """Generates complete academic performance summary for a student."""
    student = fetch_one("""
        SELECT s.*, d.department_name, d.department_code, u.name AS full_name
        FROM students s
        JOIN departments d ON s.department_id = d.department_id
        JOIN users u ON s.user_id = u.user_id
        WHERE s.student_id = %s
    """, (student_id,))

    if not student:
        return None

    # Fetch marks
    marks = fetch_all("""
        SELECT m.*, sub.subject_code, sub.subject_name, sub.credits
        FROM marks m
        JOIN subjects sub ON m.subject_id = sub.subject_id
        WHERE m.student_id = %s
    """, (student_id,))

    # Fetch attendance
    attendance = fetch_all("""
        SELECT a.*, sub.subject_code, sub.subject_name
        FROM attendance a
        JOIN subjects sub ON a.subject_id = sub.subject_id
        WHERE a.student_id = %s
    """, (student_id,))

    subjects_dict = {m['subject_id']: {'credits': m['credits']} for m in marks}
    
    # Current semester GPA
    sem_marks = [m for m in marks if m['semester'] == student['semester']]
    gpa = calculate_gpa(sem_marks, subjects_dict)

    # Overall CGPA
    cgpa = calculate_gpa(marks, subjects_dict)

    # Overall percentage
    if marks:
        total_obt = sum(float(m['total_marks']) for m in marks)
        total_max = len(marks) * 100.0
        overall_pct = round((total_obt / total_max) * 100.0, 2) if total_max > 0 else 0.0
    else:
        overall_pct = 0.0

    # Overall attendance percentage
    if attendance:
        tot_held = sum(int(a['classes_held']) for a in attendance)
        tot_attended = sum(int(a['classes_attended']) for a in attendance)
        attendance_pct = round((float(tot_attended) / float(tot_held)) * 100.0, 2) if tot_held > 0 else 0.0
    else:
        attendance_pct = 0.0

    # Subject performance list
    att_map = {a['subject_id']: a for a in attendance}
    subject_performance = []
    for m in marks:
        sub_id = m['subject_id']
        att_info = att_map.get(sub_id, {})
        att_p = float(att_info.get('attendance_percentage', 0.0))
        subject_performance.append({
            "subject_id": sub_id,
            "subject_code": m['subject_code'],
            "subject_name": m['subject_name'],
            "credits": m['credits'],
            "total_marks": float(m['total_marks']),
            "grade": m['grade'],
            "grade_point": m['grade_point'],
            "attendance_percentage": att_p,
            "attendance_warning": att_p < 75.0
        })

    # Class Ranking
    rank_res = fetch_all("""
        SELECT student_id, AVG(total_marks) AS avg_score
        FROM marks
        WHERE semester = %s
        GROUP BY student_id
        ORDER BY avg_score DESC
    """, (student['semester'],))

    rank = 1
    for idx, r in enumerate(rank_res, 1):
        if r['student_id'] == student_id:
            rank = idx
            break

    academic_status = "Good Standing"
    if attendance_pct < 75.0 or cgpa < 5.0:
        academic_status = "Academic Warning"

    return {
        "student_id": student['student_id'],
        "enrollment_number": student['enrollment_number'],
        "name": f"{student['first_name']} {student['last_name']}",
        "email": student['email'],
        "phone": student['phone'],
        "department_id": student['department_id'],
        "department_name": student['department_name'],
        "department_code": student['department_code'],
        "course": student['course'],
        "year": student['year'],
        "semester": student['semester'],
        "gpa": gpa,
        "cgpa": cgpa,
        "overall_percentage": overall_pct,
        "attendance_percentage": attendance_pct,
        "number_of_subjects": len(marks),
        "rank": rank,
        "academic_status": academic_status,
        "subject_performance": subject_performance,
        "attendance_records": attendance
    }
