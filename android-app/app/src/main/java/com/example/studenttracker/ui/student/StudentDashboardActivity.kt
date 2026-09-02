package com.example.studenttracker.ui.student

import android.content.Intent
import android.os.Bundle
import android.widget.Toast
import androidx.appcompat.app.AppCompatActivity
import androidx.lifecycle.lifecycleScope
import androidx.recyclerview.widget.LinearLayoutManager
import com.example.studenttracker.R
import com.example.studenttracker.data.api.RetrofitClient
import com.example.studenttracker.data.repository.Repository
import com.example.studenttracker.databinding.ActivityStudentDashboardBinding
import com.example.studenttracker.ui.auth.LoginActivity
import com.example.studenttracker.utils.SessionManager
import kotlinx.coroutines.launch

class StudentDashboardActivity : AppCompatActivity() {

    private lateinit var binding: ActivityStudentDashboardBinding
    private lateinit var sessionManager: SessionManager
    private lateinit var repository: Repository
    private lateinit var adapter: SubjectPerformanceAdapter

    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        binding = ActivityStudentDashboardBinding.inflate(layoutInflater)
        setContentView(binding.root)

        sessionManager = SessionManager(this)
        repository = Repository(RetrofitClient.getApiService(this))

        adapter = SubjectPerformanceAdapter()
        binding.rvSubjectPerformance.layoutManager = LinearLayoutManager(this)
        binding.rvSubjectPerformance.adapter = adapter

        binding.btnLogout.setOnClickListener {
            sessionManager.clearSession()
            startActivity(Intent(this, LoginActivity::class.java))
            finish()
        }

        binding.swipeRefresh.setOnRefreshListener {
            loadDashboardData()
        }

        setupBottomNavigation()
        loadDashboardData()
    }

    private fun loadDashboardData() {
        binding.swipeRefresh.isRefreshing = true
        val studentId = sessionManager.getRoleId()

        lifecycleScope.launch {
            val result = repository.getStudentPerformance(if (studentId > 0) studentId else 1)
            binding.swipeRefresh.isRefreshing = false

            result.onSuccess { data ->
                binding.tvWelcomeName.text = "Welcome, ${data.name}"
                binding.tvEnrollmentInfo.text = "${data.enrollmentNumber} | ${data.departmentCode} - Sem ${data.semester}"
                binding.tvGpa.text = data.gpa.toString()
                binding.tvCgpa.text = data.cgpa.toString()
                binding.tvAttendance.text = "${data.attendancePercentage}%"
                binding.tvPercentage.text = "${data.overallPercentage}%"

                adapter.submitList(data.subjectPerformance)
            }.onFailure { error ->
                Toast.makeText(this@StudentDashboardActivity, "Error: ${error.message}", Toast.LENGTH_SHORT).show()
            }
        }
    }

    private fun setupBottomNavigation() {
        binding.bottomNavigation.selectedItemId = R.id.nav_home
        binding.bottomNavigation.setOnItemSelectedListener { item ->
            when (item.itemId) {
                R.id.nav_home -> true
                R.id.nav_marks -> {
                    startActivity(Intent(this, MarksActivity::class.java))
                    overridePendingTransition(0, 0)
                    true
                }
                R.id.nav_attendance -> {
                    startActivity(Intent(this, AttendanceActivity::class.java))
                    overridePendingTransition(0, 0)
                    true
                }
                R.id.nav_performance -> {
                    startActivity(Intent(this, PerformanceActivity::class.java))
                    overridePendingTransition(0, 0)
                    true
                }
                R.id.nav_profile -> {
                    startActivity(Intent(this, ProfileActivity::class.java))
                    overridePendingTransition(0, 0)
                    true
                }
                else -> false
            }
        }
    }
}
