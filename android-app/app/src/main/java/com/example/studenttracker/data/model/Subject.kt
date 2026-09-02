package com.example.studenttracker.data.model

import com.google.gson.annotations.SerializedName

data class Subject(
    @SerializedName("subject_id") val subjectId: Int,
    @SerializedName("subject_code") val subjectCode: String,
    @SerializedName("subject_name") val subjectName: String,
    @SerializedName("department_id") val departmentId: Int,
    @SerializedName("department_name") val departmentName: String? = null,
    @SerializedName("department_code") val departmentCode: String? = null,
    val semester: Int,
    val credits: Int
)

data class SubjectCreateRequest(
    @SerializedName("subject_code") val subjectCode: String,
    @SerializedName("subject_name") val subjectName: String,
    @SerializedName("department_id") val departmentId: Int,
    val semester: Int = 1,
    val credits: Int = 3
)
