package com.example.studenttracker.ui.student

import android.content.Intent
import android.os.Bundle
import android.widget.Toast
import androidx.appcompat.app.AppCompatActivity
import androidx.lifecycle.lifecycleScope
import com.example.studenttracker.R
import com.example.studenttracker.data.api.RetrofitClient
import com.example.studenttracker.data.repository.Repository
import com.example.studenttracker.databinding.ActivityPerformanceBinding
import com.example.studenttracker.utils.SessionManager
import kotlinx.coroutines.launch

class PerformanceActivity : AppCompatActivity() {

    private lateinit var binding: ActivityPerformanceBinding
    private lateinit var sessionManager: SessionManager
    private lateinit var repository: Repository

    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        binding = ActivityPerformanceBinding.inflate(layoutInflater)
        setContentView(binding.root)

        sessionManager = SessionManager(this)
        repository = Repository(RetrofitClient.getApiService(this))

        setupBottomNavigation()
        loadPerformance()
    }

    private fun loadPerformance() {
        val studentId = sessionManager.getRoleId()
        lifecycleScope.launch {
            val result = repository.getStudentPerformance(if (studentId > 0) studentId else 1)
            result.onSuccess { data ->
                binding.tvPerfName.text = data.name
                binding.tvRankPill.text = "Class Rank: #${data.rank} in Department"
                binding.tvPerfGpa.text = data.gpa.toString()
                binding.tvPerfCgpa.text = data.cgpa.toString()
                binding.tvAcademicStatus.text = data.academicStatus

                binding.tvScorePctTitle.text = "Academic Percentage Score: ${data.overallPercentage}%"
                binding.pbScore.progress = data.overallPercentage.toInt()

                binding.tvAttendancePctTitle.text = "Total Attendance Percentage: ${data.attendancePercentage}%"
                binding.pbAttendance.progress = data.attendancePercentage.toInt()
            }.onFailure { error ->
                Toast.makeText(this@PerformanceActivity, "Error loading performance: ${error.message}", Toast.LENGTH_SHORT).show()
            }
        }
    }

    private fun setupBottomNavigation() {
        binding.bottomNavigation.selectedItemId = R.id.nav_performance
        binding.bottomNavigation.setOnItemSelectedListener { item ->
            when (item.itemId) {
                R.id.nav_home -> {
                    startActivity(Intent(this, StudentDashboardActivity::class.java))
                    overridePendingTransition(0, 0)
                    finish()
                    true
                }
                R.id.nav_marks -> {
                    startActivity(Intent(this, MarksActivity::class.java))
                    overridePendingTransition(0, 0)
                    finish()
                    true
                }
                R.id.nav_attendance -> {
                    startActivity(Intent(this, AttendanceActivity::class.java))
                    overridePendingTransition(0, 0)
                    finish()
                    true
                }
                R.id.nav_performance -> true
                R.id.nav_profile -> {
                    startActivity(Intent(this, ProfileActivity::class.java))
                    overridePendingTransition(0, 0)
                    finish()
                    true
                }
                else -> false
            }
        }
    }
}
