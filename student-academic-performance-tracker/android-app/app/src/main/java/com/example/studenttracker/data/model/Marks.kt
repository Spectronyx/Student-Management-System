package com.example.studenttracker.data.model

import com.google.gson.annotations.SerializedName

data class Marks(
    @SerializedName("mark_id") val markId: Int,
    @SerializedName("student_id") val studentId: Int,
    @SerializedName("subject_id") val subjectId: Int,
    @SerializedName("subject_code") val subjectCode: String? = null,
    @SerializedName("subject_name") val subjectName: String? = null,
    val semester: Int,
    @SerializedName("internal_marks") val internalMarks: Double,
    @SerializedName("assignment_marks") val assignmentMarks: Double,
    @SerializedName("practical_marks") val practicalMarks: Double,
    @SerializedName("final_exam_marks") val finalExamMarks: Double,
    @SerializedName("total_marks") val totalMarks: Double,
    val grade: String,
    @SerializedName("grade_point") val gradePoint: Int,
    val credits: Int? = 3
)

data class MarkEntryRequest(
    @SerializedName("student_id") val studentId: Int,
    @SerializedName("subject_id") val subjectId: Int,
    val semester: Int = 1,
    @SerializedName("internal_marks") val internalMarks: Double = 0.0,
    @SerializedName("assignment_marks") val assignmentMarks: Double = 0.0,
    @SerializedName("practical_marks") val practicalMarks: Double = 0.0,
    @SerializedName("final_exam_marks") val finalExamMarks: Double = 0.0
)
