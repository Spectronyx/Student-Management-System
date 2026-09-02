package com.example.studenttracker.data.repository

import com.example.studenttracker.data.api.ApiService
import com.example.studenttracker.data.model.*
import retrofit2.Response

class Repository(private val apiService: ApiService) {

    suspend fun login(req: LoginRequest): Result<LoginResponseData> {
        return safeApiCall { apiService.login(req) }
    }

    suspend fun getStudentPerformance(studentId: Int): Result<PerformanceSummary> {
        return safeApiCall { apiService.getStudentPerformance(studentId) }
    }

    suspend fun getMarksForStudent(studentId: Int): Result<List<Marks>> {
        return safeApiCall { apiService.getMarksForStudent(studentId) }
    }

    suspend fun getAttendanceForStudent(studentId: Int): Result<List<Attendance>> {
        return safeApiCall { apiService.getAttendanceForStudent(studentId) }
    }

    suspend fun getStudentById(studentId: Int): Result<Student> {
        return safeApiCall { apiService.getStudentById(studentId) }
    }

    suspend fun getStudents(departmentId: Int? = null, semester: Int? = null, search: String? = null): Result<List<Student>> {
        return safeApiCall { apiService.getStudents(departmentId, semester, search) }
    }

    suspend fun createStudent(req: StudentCreateRequest): Result<Student> {
        return safeApiCall { apiService.createStudent(req) }
    }

    suspend fun getSubjects(departmentId: Int? = null, semester: Int? = null): Result<List<Subject>> {
        return safeApiCall { apiService.getSubjects(departmentId, semester) }
    }

    suspend fun createSubject(req: SubjectCreateRequest): Result<Subject> {
        return safeApiCall { apiService.createSubject(req) }
    }

    suspend fun addOrUpdateMarks(req: MarkEntryRequest): Result<Marks> {
        return safeApiCall { apiService.addOrUpdateMarks(req) }
    }

    suspend fun recordAttendance(req: AttendanceEntryRequest): Result<Attendance> {
        return safeApiCall { apiService.recordAttendance(req) }
    }

    suspend fun getAttendanceWarnings(): Result<List<Map<String, Any>>> {
        return safeApiCall { apiService.getAttendanceWarnings() }
    }

    private suspend fun <T> safeApiCall(call: suspend () -> Response<StandardResponse<T>>): Result<T> {
        return try {
            val response = call()
            if (response.isSuccessful && response.body() != null) {
                val body = response.body()!!
                if (body.success && body.data != null) {
                    Result.success(body.data)
                } else {
                    Result.failure(Exception(body.message ?: "Unknown API Error"))
                }
            } else {
                Result.failure(Exception("HTTP Error ${response.code()}: ${response.message()}"))
            }
        } catch (e: Exception) {
            Result.failure(e)
        }
    }
}
