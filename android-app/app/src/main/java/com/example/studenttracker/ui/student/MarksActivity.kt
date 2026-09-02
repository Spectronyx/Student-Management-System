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
import com.example.studenttracker.databinding.ActivityMarksBinding
import com.example.studenttracker.utils.SessionManager
import kotlinx.coroutines.launch

class MarksActivity : AppCompatActivity() {

    private lateinit var binding: ActivityMarksBinding
    private lateinit var sessionManager: SessionManager
    private lateinit var repository: Repository
    private lateinit var adapter: MarksAdapter

    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        binding = ActivityMarksBinding.inflate(layoutInflater)
        setContentView(binding.root)

        sessionManager = SessionManager(this)
        repository = Repository(RetrofitClient.getApiService(this))

        adapter = MarksAdapter()
        binding.rvMarks.layoutManager = LinearLayoutManager(this)
        binding.rvMarks.adapter = adapter

        setupBottomNavigation()
        loadMarks()
    }

    private fun loadMarks() {
        val studentId = sessionManager.getRoleId()
        lifecycleScope.launch {
            val result = repository.getMarksForStudent(if (studentId > 0) studentId else 1)
            result.onSuccess { data ->
                adapter.submitList(data)
            }.onFailure { error ->
                Toast.makeText(this@MarksActivity, "Error loading marks: ${error.message}", Toast.LENGTH_SHORT).show()
            }
        }
    }

    private fun setupBottomNavigation() {
        binding.bottomNavigation.selectedItemId = R.id.nav_marks
        binding.bottomNavigation.setOnItemSelectedListener { item ->
            when (item.itemId) {
                R.id.nav_home -> {
                    startActivity(Intent(this, StudentDashboardActivity::class.java))
                    overridePendingTransition(0, 0)
                    finish()
                    true
                }
                R.id.nav_marks -> true
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
