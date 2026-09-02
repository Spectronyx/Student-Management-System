package com.example.studenttracker.ui.faculty

import android.content.Intent
import android.os.Bundle
import androidx.appcompat.app.AppCompatActivity
import com.example.studenttracker.databinding.ActivityFacultyDashboardBinding
import com.example.studenttracker.ui.auth.LoginActivity
import com.example.studenttracker.utils.SessionManager

class FacultyDashboardActivity : AppCompatActivity() {

    private lateinit var binding: ActivityFacultyDashboardBinding
    private lateinit var sessionManager: SessionManager

    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        binding = ActivityFacultyDashboardBinding.inflate(layoutInflater)
        setContentView(binding.root)

        sessionManager = SessionManager(this)

        binding.tvFacultyWelcome.text = "Welcome, ${sessionManager.getUserName() ?: "Faculty"}"
        binding.tvFacultyEmail.text = sessionManager.getUserEmail() ?: ""

        binding.cardMarksManagement.setOnClickListener {
            startActivity(Intent(this, MarksManagementActivity::class.java))
        }

        binding.cardAttendanceManagement.setOnClickListener {
            startActivity(Intent(this, FacultyAttendanceActivity::class.java))
        }

        binding.btnLogout.setOnClickListener {
            sessionManager.clearSession()
            startActivity(Intent(this, LoginActivity::class.java))
            finish()
        }
    }
}
