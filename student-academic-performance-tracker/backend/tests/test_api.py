import pytest
from fastapi.testclient import TestClient
from main import app
from database import init_db

client = TestClient(app)

@pytest.fixture(scope="module", autouse=True)
def setup_database():
    """Initializes schema and seed data before running tests."""
    init_db()

def test_01_root():
    response = client.get("/")
    assert response.status_code == 200
    data = response.json()
    assert data["success"] is True

def test_02_admin_login():
    response = client.post("/auth/login", json={
        "username_or_email": "admin",
        "password": "admin123"
    })
    assert response.status_code == 200
    res = response.json()
    assert res["success"] is True
    assert res["data"]["role"] == "Admin"
    assert "access_token" in res["data"]

def test_03_student_login():
    response = client.post("/auth/login", json={
        "username_or_email": "student1",
        "password": "student123"
    })
    assert response.status_code == 200
    res = response.json()
    assert res["success"] is True
    assert res["data"]["role"] == "Student"

def test_04_faculty_login():
    response = client.post("/auth/login", json={
        "username_or_email": "prof_sharma",
        "password": "faculty123"
    })
    assert response.status_code == 200
    res = response.json()
    assert res["success"] is True
    assert res["data"]["role"] == "Faculty"

def test_05_invalid_login():
    response = client.post("/auth/login", json={
        "username_or_email": "admin",
        "password": "wrong_password"
    })
    assert response.status_code == 401
    res = response.json()
    assert res["detail"]["success"] is False

def test_06_student_performance_summary():
    # Login as admin to get token
    login_res = client.post("/auth/login", json={"username_or_email": "admin", "password": "admin123"}).json()
    token = login_res["data"]["access_token"]

    response = client.get("/performance/student/1", headers={"Authorization": f"Bearer {token}"})
    assert response.status_code == 200
    res = response.json()
    assert res["success"] is True
    assert res["data"]["student_id"] == 1
    assert "gpa" in res["data"]
    assert "cgpa" in res["data"]

def test_07_backend_grade_recalculation():
    login_res = client.post("/auth/login", json={"username_or_email": "admin", "password": "admin123"}).json()
    token = login_res["data"]["access_token"]

    # Post marks: Total = 28 + 18 + 20 + 45 = 91 -> Grade should be A+, Grade Point should be 10
    response = client.post("/marks", headers={"Authorization": f"Bearer {token}"}, json={
        "student_id": 1,
        "subject_id": 1,
        "semester": 5,
        "internal_marks": 25.0,
        "assignment_marks": 15.0,
        "practical_marks": 15.0,
        "final_exam_marks": 36.0
    })
    assert response.status_code == 200
    res = response.json()
    assert res["success"] is True
    assert float(res["data"]["total_marks"]) == 91.0
    assert res["data"]["grade"] == "A+"
    assert res["data"]["grade_point"] == 10

def test_08_attendance_validation():
    login_res = client.post("/auth/login", json={"username_or_email": "admin", "password": "admin123"}).json()
    token = login_res["data"]["access_token"]

    # Invalid attendance: attended 50 out of 40 -> Should fail with 400 Bad Request
    response = client.post("/attendance", headers={"Authorization": f"Bearer {token}"}, json={
        "student_id": 1,
        "subject_id": 1,
        "semester": 5,
        "classes_held": 40,
        "classes_attended": 50
    })
    assert response.status_code == 400
    res = response.json()
    assert res["detail"]["success"] is False
