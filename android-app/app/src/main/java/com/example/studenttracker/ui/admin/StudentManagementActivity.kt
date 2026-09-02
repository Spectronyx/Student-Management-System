package com.example.studenttracker.ui.admin

import android.os.Bundle
import android.text.Editable
import android.text.TextWatcher
import android.widget.EditText
import android.widget.LinearLayout
import android.widget.Toast
import androidx.appcompat.app.AlertDialog
import androidx.appcompat.app.AppCompatActivity
import androidx.lifecycle.lifecycleScope
import androidx.recyclerview.widget.LinearLayoutManager
import com.example.studenttracker.data.api.RetrofitClient
import com.example.studenttracker.data.model.StudentCreateRequest
import com.example.studenttracker.data.repository.Repository
import com.example.studenttracker.databinding.ActivityStudentManagementBinding
import kotlinx.coroutines.launch

class StudentManagementActivity : AppCompatActivity() {

    private lateinit var binding: ActivityStudentManagementBinding
    private lateinit var repository: Repository
    private lateinit var adapter: StudentsAdapter

    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        binding = ActivityStudentManagementBinding.inflate(layoutInflater)
        setContentView(binding.root)

        repository = Repository(RetrofitClient.getApiService(this))

        adapter = StudentsAdapter()
        binding.rvStudents.layoutManager = LinearLayoutManager(this)
        binding.rvStudents.adapter = adapter

        binding.etSearch.addTextChangedListener(object : TextWatcher {
            override fun beforeTextChanged(s: CharSequence?, start: Int, count: Int, after: Int) {}
            override fun onTextChanged(s: CharSequence?, start: Int, before: Int, count: Int) {
                loadStudents(s?.toString())
            }
            override fun afterTextChanged(s: Editable?) {}
        })

        binding.btnAddStudent.setOnClickListener {
            showAddStudentDialog()
        }

        loadStudents()
    }

    private fun loadStudents(query: String? = null) {
        lifecycleScope.launch {
            val result = repository.getStudents(search = query)
            result.onSuccess { data ->
                adapter.submitList(data)
            }.onFailure { error ->
                Toast.makeText(this@StudentManagementActivity, "Error loading students: ${error.message}", Toast.LENGTH_SHORT).show()
            }
        }
    }

    private fun showAddStudentDialog() {
        val context = this
        val layout = LinearLayout(context).apply {
            orientation = LinearLayout.VERTICAL
            setPadding(50, 40, 50, 10)
        }

        val etFirstName = EditText(context).apply { hint = "First Name" }
        val etLastName = EditText(context).apply { hint = "Last Name" }
        val etEnrollment = EditText(context).apply { hint = "Enrollment Number (e.g. CS2026099)" }
        val etEmail = EditText(context).apply { hint = "Email Address" }

        layout.addView(etFirstName)
        layout.addView(etLastName)
        layout.addView(etEnrollment)
        layout.addView(etEmail)

        AlertDialog.Builder(context)
            .setTitle("Register New Student")
            .setView(layout)
            .setPositiveButton("Register") { dialog, _ ->
                val firstName = etFirstName.text.toString().trim()
                val lastName = etLastName.text.toString().trim()
                val enrollment = etEnrollment.text.toString().trim()
                val email = etEmail.text.toString().trim()

                if (firstName.isEmpty() || lastName.isEmpty() || enrollment.isEmpty() || email.isEmpty()) {
                    Toast.makeText(context, "All fields are required", Toast.LENGTH_SHORT).show()
                    return@setPositiveButton
                }

                lifecycleScope.launch {
                    val req = StudentCreateRequest(
                        firstName = firstName,
                        lastName = lastName,
                        enrollmentNumber = enrollment,
                        email = email,
                        departmentId = 1,
                        course = "B.Tech",
                        semester = 5
                    )
                    val res = repository.createStudent(req)
                    res.onSuccess {
                        Toast.makeText(context, "Student Registered Successfully!", Toast.LENGTH_SHORT).show()
                        loadStudents()
                    }.onFailure { err ->
                        Toast.makeText(context, "Failed: ${err.message}", Toast.LENGTH_LONG).show()
                    }
                }
            }
            .setNegativeButton("Cancel", null)
            .show()
    }
}
