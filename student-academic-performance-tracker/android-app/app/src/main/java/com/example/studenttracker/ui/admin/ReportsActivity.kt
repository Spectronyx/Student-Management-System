package com.example.studenttracker.ui.admin

import android.os.Bundle
import android.widget.Toast
import androidx.appcompat.app.AppCompatActivity
import androidx.lifecycle.lifecycleScope
import com.example.studenttracker.data.api.RetrofitClient
import com.example.studenttracker.data.repository.Repository
import com.example.studenttracker.databinding.ActivityReportsBinding
import kotlinx.coroutines.launch

class ReportsActivity : AppCompatActivity() {

    private lateinit var binding: ActivityReportsBinding
    private lateinit var repository: Repository

    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        binding = ActivityReportsBinding.inflate(layoutInflater)
        setContentView(binding.root)

        repository = Repository(RetrofitClient.getApiService(this))

        loadAttendanceWarnings()
    }

    private fun loadAttendanceWarnings() {
        lifecycleScope.launch {
            val result = repository.getAttendanceWarnings()
            result.onSuccess { list ->
                if (list.isEmpty()) {
                    binding.tvWarningsList.text = "No students are currently below 75% attendance threshold."
                } else {
                    val sb = StringBuilder()
                    list.forEachIndexed { idx, item ->
                        val name = item["student_name"] ?: "Student"
                        val roll = item["enrollment_number"] ?: ""
                        val sub = item["subject_code"] ?: ""
                        val pct = item["attendance_percentage"] ?: 0.0
                        sb.append("${idx + 1}. $name ($roll)\n   Subject: $sub | Attendance: $pct%\n\n")
                    }
                    binding.tvWarningsList.text = sb.toString()
                }
            }.onFailure { err ->
                Toast.makeText(this@ReportsActivity, "Error: ${err.message}", Toast.LENGTH_SHORT).show()
            }
        }
    }
}
