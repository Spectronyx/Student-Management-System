from typing import Tuple

def calculate_grade_and_point(total_marks: float) -> Tuple[str, int]:
    """
    Calculates letter grade and grade point from total marks based on grading criteria:
    90–100 -> A+ -> 10
    80–89  -> A  -> 9
    70–79  -> B+ -> 8
    60–69  -> B  -> 7
    50–59  -> C  -> 6
    40–49  -> D  -> 5
    < 40   -> F  -> 0
    """
    marks = round(float(total_marks), 2)
    if marks >= 90.0:
        return "A+", 10
    elif marks >= 80.0:
        return "A", 9
    elif marks >= 70.0:
        return "B+", 8
    elif marks >= 60.0:
        return "B", 7
    elif marks >= 50.0:
        return "C", 6
    elif marks >= 40.0:
        return "D", 5
    else:
        return "F", 0

def calculate_gpa(marks_records: list, subjects_dict: dict) -> float:
    """
    Calculates GPA: SUM(grade_point * credits) / SUM(credits)
    """
    total_credit_points = 0.0
    total_credits = 0.0

    for m in marks_records:
        sub_id = m['subject_id']
        sub_info = subjects_dict.get(sub_id, {})
        credits = float(sub_info.get('credits', m.get('credits', 3)))
        gp = float(m.get('grade_point', 0))

        total_credit_points += (gp * credits)
        total_credits += credits

    if total_credits == 0.0:
        return 0.0

    return round(total_credit_points / total_credits, 2)

def calculate_attendance_pct(classes_attended: int, classes_held: int) -> float:
    if classes_held <= 0:
        return 0.0
    return round((float(classes_attended) / float(classes_held)) * 100.0, 2)
