package com.example.studenttracker.ui.admin

import android.content.Intent
import android.os.Bundle
import androidx.appcompat.app.AppCompatActivity
import com.example.studenttracker.databinding.ActivityAdminDashboardBinding
import com.example.studenttracker.ui.auth.LoginActivity
import com.example.studenttracker.utils.SessionManager

class AdminDashboardActivity : AppCompatActivity() {

    private lateinit var binding: ActivityAdminDashboardBinding
    private lateinit var sessionManager: SessionManager

    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        binding = ActivityAdminDashboardBinding.inflate(layoutInflater)
        setContentView(binding.root)

        sessionManager = SessionManager(this)

        binding.tvAdminWelcome.text = "Welcome, ${sessionManager.getUserName() ?: "Admin"}"

        binding.cardStudentManagement.setOnClickListener {
            startActivity(Intent(this, StudentManagementActivity::class.java))
        }

        binding.cardFacultyManagement.setOnClickListener {
            startActivity(Intent(this, FacultyManagementActivity::class.java))
        }

        binding.cardSubjectManagement.setOnClickListener {
            startActivity(Intent(this, SubjectManagementActivity::class.java))
        }

        binding.cardReports.setOnClickListener {
            startActivity(Intent(this, ReportsActivity::class.java))
        }

        binding.btnLogout.setOnClickListener {
            sessionManager.clearSession()
            startActivity(Intent(this, LoginActivity::class.java))
            finish()
        }
    }
}
