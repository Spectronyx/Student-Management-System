package com.example.studenttracker.data.model

import com.google.gson.annotations.SerializedName

data class Attendance(
    @SerializedName("attendance_id") val attendanceId: Int,
    @SerializedName("student_id") val studentId: Int,
    @SerializedName("subject_id") val subjectId: Int,
    @SerializedName("subject_code") val subjectCode: String? = null,
    @SerializedName("subject_name") val subjectName: String? = null,
    val semester: Int,
    @SerializedName("classes_held") val classesHeld: Int,
    @SerializedName("classes_attended") val classesAttended: Int,
    @SerializedName("attendance_percentage") val attendancePercentage: Double
)

data class AttendanceEntryRequest(
    @SerializedName("student_id") val studentId: Int,
    @SerializedName("subject_id") val subjectId: Int,
    val semester: Int = 1,
    @SerializedName("classes_held") val classesHeld: Int,
    @SerializedName("classes_attended") val classesAttended: Int
)
