package com.example.studenttracker.ui.faculty

import android.os.Bundle
import android.widget.Toast
import androidx.appcompat.app.AppCompatActivity
import androidx.lifecycle.lifecycleScope
import com.example.studenttracker.data.api.RetrofitClient
import com.example.studenttracker.data.model.AttendanceEntryRequest
import com.example.studenttracker.data.repository.Repository
import com.example.studenttracker.databinding.ActivityFacultyAttendanceBinding
import kotlinx.coroutines.launch

class FacultyAttendanceActivity : AppCompatActivity() {

    private lateinit var binding: ActivityFacultyAttendanceBinding
    private lateinit var repository: Repository

    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        binding = ActivityFacultyAttendanceBinding.inflate(layoutInflater)
        setContentView(binding.root)

        repository = Repository(RetrofitClient.getApiService(this))

        binding.btnSubmitAttendance.setOnClickListener {
            val studentId = binding.etStudentId.text.toString().toIntOrNull()
            val subjectId = binding.etSubjectId.text.toString().toIntOrNull()
            val held = binding.etClassesHeld.text.toString().toIntOrNull()
            val attended = binding.etClassesAttended.text.toString().toIntOrNull()

            if (studentId == null || subjectId == null || held == null || attended == null) {
                Toast.makeText(this, "Please fill in all numerical fields", Toast.LENGTH_SHORT).show()
                return@setOnClickListener
            }

            if (attended > held) {
                Toast.makeText(this, "Classes attended cannot exceed total classes held!", Toast.LENGTH_LONG).show()
                return@setOnClickListener
            }

            lifecycleScope.launch {
                val req = AttendanceEntryRequest(
                    studentId = studentId,
                    subjectId = subjectId,
                    classesHeld = held,
                    classesAttended = attended
                )
                val result = repository.recordAttendance(req)
                result.onSuccess { data ->
                    Toast.makeText(
                        this@FacultyAttendanceActivity,
                        "Attendance Logged! Percentage: ${data.attendancePercentage}%",
                        Toast.LENGTH_LONG
                    ).show()
                    finish()
                }.onFailure { error ->
                    Toast.makeText(this@FacultyAttendanceActivity, "Failed: ${error.message}", Toast.LENGTH_LONG).show()
                }
            }
        }
    }
}
