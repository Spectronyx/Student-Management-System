package com.example.studenttracker.data.model

import com.google.gson.annotations.SerializedName

data class Student(
    @SerializedName("student_id") val studentId: Int,
    @SerializedName("user_id") val userId: Int,
    @SerializedName("enrollment_number") val enrollmentNumber: String,
    @SerializedName("first_name") val firstName: String,
    @SerializedName("last_name") val lastName: String,
    val email: String,
    val phone: String? = null,
    @SerializedName("department_id") val departmentId: Int,
    @SerializedName("department_name") val departmentName: String? = null,
    @SerializedName("department_code") val departmentCode: String? = null,
    val course: String,
    val year: Int,
    val semester: Int,
    @SerializedName("admission_date") val admissionDate: String? = null
)

data class StudentCreateRequest(
    @SerializedName("first_name") val firstName: String,
    @SerializedName("last_name") val lastName: String,
    @SerializedName("enrollment_number") val enrollmentNumber: String,
    val email: String,
    val phone: String? = null,
    @SerializedName("department_id") val departmentId: Int,
    val course: String,
    val year: Int = 1,
    val semester: Int = 1,
    val password: String = "student123"
)
