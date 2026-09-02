package com.example.studenttracker.data.model

import com.google.gson.annotations.SerializedName

data class SubjectPerformance(
    @SerializedName("subject_id") val subjectId: Int,
    @SerializedName("subject_code") val subjectCode: String,
    @SerializedName("subject_name") val subjectName: String,
    val credits: Int,
    @SerializedName("total_marks") val totalMarks: Double,
    val grade: String,
    @SerializedName("grade_point") val gradePoint: Int,
    @SerializedName("attendance_percentage") val attendancePercentage: Double,
    @SerializedName("attendance_warning") val attendanceWarning: Boolean
)

data class PerformanceSummary(
    @SerializedName("student_id") val studentId: Int,
    @SerializedName("enrollment_number") val enrollmentNumber: String,
    val name: String,
    val email: String,
    val phone: String? = null,
    @SerializedName("department_id") val departmentId: Int,
    @SerializedName("department_name") val departmentName: String,
    @SerializedName("department_code") val departmentCode: String,
    val course: String,
    val year: Int,
    val semester: Int,
    val gpa: Double,
    val cgpa: Double,
    @SerializedName("overall_percentage") val overallPercentage: Double,
    @SerializedName("attendance_percentage") val attendancePercentage: Double,
    @SerializedName("number_of_subjects") val numberOfSubjects: Int,
    val rank: Int,
    @SerializedName("academic_status") val academicStatus: String,
    @SerializedName("subject_performance") val subjectPerformance: List<SubjectPerformance>,
    @SerializedName("attendance_records") val attendanceRecords: List<Attendance>
)
