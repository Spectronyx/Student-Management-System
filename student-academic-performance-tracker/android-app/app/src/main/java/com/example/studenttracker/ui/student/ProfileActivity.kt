package com.example.studenttracker.ui.student

import android.content.Intent
import android.os.Bundle
import android.widget.Toast
import androidx.appcompat.app.AppCompatActivity
import androidx.lifecycle.lifecycleScope
import com.example.studenttracker.R
import com.example.studenttracker.data.api.RetrofitClient
import com.example.studenttracker.data.repository.Repository
import com.example.studenttracker.databinding.ActivityProfileBinding
import com.example.studenttracker.ui.auth.LoginActivity
import com.example.studenttracker.utils.SessionManager
import kotlinx.coroutines.launch

class ProfileActivity : AppCompatActivity() {

    private lateinit var binding: ActivityProfileBinding
    private lateinit var sessionManager: SessionManager
    private lateinit var repository: Repository

    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        binding = ActivityProfileBinding.inflate(layoutInflater)
        setContentView(binding.root)

        sessionManager = SessionManager(this)
        repository = Repository(RetrofitClient.getApiService(this))

        binding.btnLogout.setOnClickListener {
            sessionManager.clearSession()
            startActivity(Intent(this, LoginActivity::class.java))
            finish()
        }

        setupBottomNavigation()
        loadProfile()
    }

    private fun loadProfile() {
        val studentId = sessionManager.getRoleId()
        lifecycleScope.launch {
            val result = repository.getStudentById(if (studentId > 0) studentId else 1)
            result.onSuccess { data ->
                binding.tvProfileName.text = "${data.firstName} ${data.lastName}"
                binding.tvEnrollmentNo.text = "Enrollment No: ${data.enrollmentNumber}"
                binding.tvEmail.text = "Email: ${data.email}"
                binding.tvPhone.text = "Phone: ${data.phone ?: "N/A"}"
                binding.tvDepartment.text = "Department: ${data.departmentName ?: "Computer Science"}"
                binding.tvCourseSem.text = "Course: ${data.course} | Year ${data.year} | Semester ${data.semester}"
            }.onFailure { error ->
                Toast.makeText(this@ProfileActivity, "Error loading profile: ${error.message}", Toast.LENGTH_SHORT).show()
            }
        }
    }

    private fun setupBottomNavigation() {
        binding.bottomNavigation.selectedItemId = R.id.nav_profile
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
                R.id.nav_performance -> {
                    startActivity(Intent(this, PerformanceActivity::class.java))
                    overridePendingTransition(0, 0)
                    finish()
                    true
                }
                R.id.nav_profile -> true
                else -> false
            }
        }
    }
}
