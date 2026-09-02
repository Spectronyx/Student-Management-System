import sys
import os
import json

# Ensure sys.path includes backend root
backend_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, backend_dir)

from fastapi.testclient import TestClient
from main import app
from database import init_db

client = TestClient(app)

def run_route_tests():
    print("=" * 70)
    print(" 🚀 RUNNING COMPREHENSIVE BACKEND ROUTE VERIFICATION")
    print("=" * 70)

    # 1. Init Database
    init_db()

    results = []

    def check(route_name, method, url, status_code, headers=None, json_data=None):
        try:
            if method == "GET":
                res = client.get(url, headers=headers)
            elif method == "POST":
                res = client.post(url, headers=headers, json=json_data)
            elif method == "PUT":
                res = client.put(url, headers=headers, json=json_data)
            elif method == "DELETE":
                res = client.delete(url, headers=headers)
            
            passed = res.status_code == status_code
            status_symbol = "✅ PASS" if passed else f"❌ FAIL (Got {res.status_code}, Expected {status_code})"
            
            results.append({
                "route": route_name,
                "endpoint": f"{method} {url}",
                "expected": status_code,
                "actual": res.status_code,
                "passed": passed
            })
            print(f"[{status_symbol}] {method} {url}")
            if not passed:
                print(f"   Response Body: {res.text}")
            return res
        except Exception as e:
            print(f"[❌ EXCEPTION] {method} {url} -> {e}")
            results.append({
                "route": route_name,
                "endpoint": f"{method} {url}",
                "expected": status_code,
                "actual": "EXCEPTION",
                "passed": False
            })
            return None

    # AUTH ROUTES
    print("\n--- 🔑 Auth Routes ---")
    admin_login = check("Admin Login", "POST", "/auth/login", 200, json_data={"username_or_email": "admin", "password": "admin123"})
    admin_token = admin_login.json()["data"]["access_token"] if admin_login and admin_login.status_code == 200 else ""
    admin_headers = {"Authorization": f"Bearer {admin_token}"}

    student_login = check("Student Login", "POST", "/auth/login", 200, json_data={"username_or_email": "student1", "password": "student123"})
    student_token = student_login.json()["data"]["access_token"] if student_login and student_login.status_code == 200 else ""
    student_headers = {"Authorization": f"Bearer {student_token}"}

    check("Invalid Credentials", "POST", "/auth/login", 401, json_data={"username_or_email": "admin", "password": "wrongpassword"})

    # STUDENTS ROUTES
    print("\n--- 👨‍🎓 Students Routes ---")
    check("Get All Students", "GET", "/students", 200, headers=admin_headers)
    check("Get Student by ID", "GET", "/students/1", 200, headers=admin_headers)
    check("Search Students", "GET", "/students?search=student1", 200, headers=admin_headers)
    check("Filter Students by Dept", "GET", "/students?department_id=1", 200, headers=admin_headers)
    
    # Create temp student
    test_enrollment = "TEMP" + str(int(os.times().user * 1000))
    create_res = check("Create Student", "POST", "/students", 200, headers=admin_headers, json_data={
        "enrollment_number": test_enrollment,
        "first_name": "Test",
        "last_name": "Student",
        "email": f"test.{test_enrollment}@college.edu",
        "phone": "9876543210",
        "department_id": 1,
        "course": "B.Tech",
        "year": 1,
        "semester": 1,
        "password": "password123"
    })
    
    temp_id = None
    if create_res and create_res.status_code == 200:
        temp_id = create_res.json()["data"]["student_id"]
        check("Update Student", "PUT", f"/students/{temp_id}", 200, headers=admin_headers, json_data={"first_name": "UpdatedName"})
        check("Delete Student", "DELETE", f"/students/{temp_id}", 200, headers=admin_headers)

    check("Get Non-existent Student", "GET", "/students/999999", 404, headers=admin_headers)

    # SUBJECTS ROUTES
    print("\n--- 📚 Subjects Routes ---")
    check("Get All Subjects", "GET", "/subjects", 200, headers=admin_headers)
    check("Get Subject by ID", "GET", "/subjects/1", 200, headers=admin_headers)
    
    test_sub_code = "SUB" + str(int(os.times().user * 100))
    check("Create Subject", "POST", "/subjects", 200, headers=admin_headers, json_data={
        "subject_code": test_sub_code,
        "subject_name": "Testing Principles",
        "department_id": 1,
        "semester": 1,
        "credits": 4
    })

    # MARKS ROUTES
    print("\n--- 📝 Marks Routes ---")
    check("Get Marks for Student 1", "GET", "/marks/student/1", 200, headers=admin_headers)
    check("Post/Update Marks with Auto Grade Recalculation", "POST", "/marks", 200, headers=admin_headers, json_data={
        "student_id": 1,
        "subject_id": 1,
        "semester": 5,
        "internal_marks": 28.0,
        "assignment_marks": 18.0,
        "practical_marks": 18.0,
        "final_exam_marks": 30.0
    })

    # ATTENDANCE ROUTES
    print("\n--- 📅 Attendance Routes ---")
    check("Get Attendance for Student 1", "GET", "/attendance/student/1", 200, headers=admin_headers)
    check("Record Valid Attendance", "POST", "/attendance", 200, headers=admin_headers, json_data={
        "student_id": 1,
        "subject_id": 1,
        "semester": 5,
        "classes_held": 40,
        "classes_attended": 35
    })
    check("Reject Invalid Attendance (> classes_held)", "POST", "/attendance", 400, headers=admin_headers, json_data={
        "student_id": 1,
        "subject_id": 1,
        "semester": 5,
        "classes_held": 40,
        "classes_attended": 50
    })

    # PERFORMANCE ROUTES
    print("\n--- 📊 Performance Routes ---")
    check("Get Student Performance Summary", "GET", "/performance/student/1", 200, headers=admin_headers)

    # ANALYTICS ROUTES
    print("\n--- 📈 Analytics Routes ---")
    check("Subject Performance Stats", "GET", "/analytics/subject-performance", 200, headers=admin_headers)
    check("Department Performance Stats", "GET", "/analytics/department-performance", 200, headers=admin_headers)
    check("Top Students Rankers", "GET", "/analytics/top-students", 200, headers=admin_headers)
    check("Attendance Warning List (<75%)", "GET", "/analytics/attendance-warning", 200, headers=admin_headers)

    # SUMMARY
    passed_count = sum(1 for r in results if r["passed"])
    total_count = len(results)

    print("\n" + "=" * 70)
    print(f" 📊 VERIFICATION SUMMARY: {passed_count}/{total_count} ROUTE TESTS PASSED")
    print("=" * 70)

    if passed_count == total_count:
        print("🎉 ALL BACKEND ROUTE VERIFICATIONS PASSED SUCCESSFULLY!")
    else:
        print("⚠️ SOME BACKEND ROUTES FAILED. PLEASE REVIEW LOGS ABOVE.")

if __name__ == "__main__":
    run_route_tests()
