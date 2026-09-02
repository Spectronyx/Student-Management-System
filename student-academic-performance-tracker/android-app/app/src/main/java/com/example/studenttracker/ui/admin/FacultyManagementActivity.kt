package com.example.studenttracker.ui.admin

import android.os.Bundle
import androidx.appcompat.app.AppCompatActivity
import com.example.studenttracker.databinding.ActivityFacultyManagementBinding

class FacultyManagementActivity : AppCompatActivity() {

    private lateinit var binding: ActivityFacultyManagementBinding

    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        binding = ActivityFacultyManagementBinding.inflate(layoutInflater)
        setContentView(binding.root)
    }
}
