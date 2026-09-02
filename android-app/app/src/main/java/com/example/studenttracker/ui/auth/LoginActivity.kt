package com.example.studenttracker.ui.auth

import android.content.Intent
import android.os.Bundle
import android.view.View
import android.widget.Toast
import androidx.appcompat.app.AppCompatActivity
import androidx.lifecycle.lifecycleScope
import com.example.studenttracker.data.api.RetrofitClient
import com.example.studenttracker.data.model.LoginRequest
import com.example.studenttracker.data.repository.Repository
import com.example.studenttracker.databinding.ActivityLoginBinding
import com.example.studenttracker.ui.admin.AdminDashboardActivity
import com.example.studenttracker.ui.faculty.FacultyDashboardActivity
import com.example.studenttracker.ui.student.StudentDashboardActivity
import com.example.studenttracker.utils.Constants
import com.example.studenttracker.utils.SessionManager
import kotlinx.coroutines.launch

class LoginActivity : AppCompatActivity() {

    private lateinit var binding: ActivityLoginBinding
    private lateinit var sessionManager: SessionManager
    private lateinit var repository: Repository

    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        binding = ActivityLoginBinding.inflate(layoutInflater)
        setContentView(binding.root)

        sessionManager = SessionManager(this)
        repository = Repository(RetrofitClient.getApiService(this))

        // Check auto login
        if (sessionManager.isLoggedIn()) {
            navigateToRoleDashboard(sessionManager.getUserRole())
            finish()
            return
        }

        binding.btnLogin.setOnClickListener {
            val username = binding.etUsername.text.toString().trim()
            val password = binding.etPassword.text.toString().trim()

            if (username.isEmpty() || password.isEmpty()) {
                Toast.makeText(this, "Please enter both username and password", Toast.LENGTH_SHORT).show()
                return@setOnClickListener
            }

            performLogin(username, password)
        }
    }

    private fun performLogin(user: String, pass: String) {
        binding.progressBar.visibility = View.VISIBLE
        binding.btnLogin.isEnabled = false

        lifecycleScope.launch {
            val result = repository.login(LoginRequest(user, pass))
            binding.progressBar.visibility = View.GONE
            binding.btnLogin.isEnabled = true

            result.onSuccess { data ->
                sessionManager.saveAuthSession(
                    token = data.accessToken,
                    userId = data.userId,
                    roleId = data.roleId,
                    role = data.role,
                    name = data.name,
                    email = data.email
                )
                Toast.makeText(this@LoginActivity, "Welcome ${data.name}!", Toast.LENGTH_SHORT).show()
                navigateToRoleDashboard(data.role)
                finish()
            }.onFailure { error ->
                Toast.makeText(this@LoginActivity, "Login Failed: ${error.message}", Toast.LENGTH_LONG).show()
            }
        }
    }

    private fun navigateToRoleDashboard(role: String?) {
        val intent = when (role) {
            Constants.ROLE_ADMIN -> Intent(this, AdminDashboardActivity::class.java)
            Constants.ROLE_FACULTY -> Intent(this, FacultyDashboardActivity::class.java)
            Constants.ROLE_STUDENT -> Intent(this, StudentDashboardActivity::class.java)
            else -> Intent(this, StudentDashboardActivity::class.java)
        }
        startActivity(intent)
    }
}
