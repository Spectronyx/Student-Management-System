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
import com.example.studenttracker.databinding.ActivityAttendanceBinding
import com.example.studenttracker.utils.SessionManager
import kotlinx.coroutines.launch

class AttendanceActivity : AppCompatActivity() {

    private lateinit var binding: ActivityAttendanceBinding
    private lateinit var sessionManager: SessionManager
    private lateinit var repository: Repository
    private lateinit var adapter: AttendanceAdapter

    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        binding = ActivityAttendanceBinding.inflate(layoutInflater)
        setContentView(binding.root)

        sessionManager = SessionManager(this)
        repository = Repository(RetrofitClient.getApiService(this))

        adapter = AttendanceAdapter()
        binding.rvAttendance.layoutManager = LinearLayoutManager(this)
        binding.rvAttendance.adapter = adapter

        setupBottomNavigation()
        loadAttendance()
    }

    private fun loadAttendance() {
        val studentId = sessionManager.getRoleId()
        lifecycleScope.launch {
            val result = repository.getAttendanceForStudent(if (studentId > 0) studentId else 1)
            result.onSuccess { data ->
                adapter.submitList(data)
            }.onFailure { error ->
                Toast.makeText(this@AttendanceActivity, "Error loading attendance: ${error.message}", Toast.LENGTH_SHORT).show()
            }
        }
    }

    private fun setupBottomNavigation() {
        binding.bottomNavigation.selectedItemId = R.id.nav_attendance
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
                R.id.nav_attendance -> true
                R.id.nav_performance -> {
                    startActivity(Intent(this, PerformanceActivity::class.java))
                    overridePendingTransition(0, 0)
                    finish()
                    true
                }
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
