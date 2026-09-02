package com.example.studenttracker.data.api

import com.example.studenttracker.data.model.*
import retrofit2.Response
import retrofit2.http.*

interface ApiService {

    // Auth
    @POST("auth/login")
    suspend fun login(@Body request: LoginRequest): Response<StandardResponse<LoginResponseData>>

    @POST("auth/logout")
    suspend fun logout(): Response<StandardResponse<Unit>>

    @GET("auth/me")
    suspend fun getMe(): Response<StandardResponse<User>>

    // Students
    @GET("students")
    suspend fun getStudents(
        @Query("department_id") departmentId: Int? = null,
        @Query("semester") semester: Int? = null,
        @Query("search") search: String? = null
    ): Response<StandardResponse<List<Student>>>

    @GET("students/{id}")
    suspend fun getStudentById(@Path("id") id: Int): Response<StandardResponse<Student>>

    @POST("students")
    suspend fun createStudent(@Body request: StudentCreateRequest): Response<StandardResponse<Student>>

    @PUT("students/{id}")
    suspend fun updateStudent(@Path("id") id: Int, @Body request: Map<String, Any>): Response<StandardResponse<Student>>

    @DELETE("students/{id}")
    suspend fun deleteStudent(@Path("id") id: Int): Response<StandardResponse<Unit>>

    // Subjects
    @GET("subjects")
    suspend fun getSubjects(
        @Query("department_id") departmentId: Int? = null,
        @Query("semester") semester: Int? = null
    ): Response<StandardResponse<List<Subject>>>

    @GET("subjects/{id}")
    suspend fun getSubjectById(@Path("id") id: Int): Response<StandardResponse<Subject>>

    @POST("subjects")
    suspend fun createSubject(@Body request: SubjectCreateRequest): Response<StandardResponse<Subject>>

    @DELETE("subjects/{id}")
    suspend fun deleteSubject(@Path("id") id: Int): Response<StandardResponse<Unit>>

    // Marks
    @GET("marks/student/{student_id}")
    suspend fun getMarksForStudent(@Path("student_id") studentId: Int): Response<StandardResponse<List<Marks>>>

    @GET("marks/subject/{subject_id}")
    suspend fun getMarksForSubject(@Path("subject_id") subjectId: Int): Response<StandardResponse<List<Marks>>>

    @POST("marks")
    suspend fun addOrUpdateMarks(@Body request: MarkEntryRequest): Response<StandardResponse<Marks>>

    @DELETE("marks/{id}")
    suspend fun deleteMarks(@Path("id") id: Int): Response<StandardResponse<Unit>>

    // Attendance
    @GET("attendance/student/{student_id}")
    suspend fun getAttendanceForStudent(@Path("student_id") studentId: Int): Response<StandardResponse<List<Attendance>>>

    @GET("attendance/subject/{subject_id}")
    suspend fun getAttendanceForSubject(@Path("subject_id") subjectId: Int): Response<StandardResponse<List<Attendance>>>

    @POST("attendance")
    suspend fun recordAttendance(@Body request: AttendanceEntryRequest): Response<StandardResponse<Attendance>>

    // Performance & Analytics
    @GET("performance/student/{student_id}")
    suspend fun getStudentPerformance(@Path("student_id") studentId: Int): Response<StandardResponse<PerformanceSummary>>

    @GET("analytics/attendance-warning")
    suspend fun getAttendanceWarnings(): Response<StandardResponse<List<Map<String, Any>>>>

    @GET("analytics/top-students")
    suspend fun getTopStudents(): Response<StandardResponse<List<Map<String, Any>>>>
}
