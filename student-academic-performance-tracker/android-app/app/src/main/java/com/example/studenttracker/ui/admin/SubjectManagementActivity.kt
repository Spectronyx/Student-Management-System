package com.example.studenttracker.ui.admin

import android.os.Bundle
import android.widget.EditText
import android.widget.LinearLayout
import android.widget.Toast
import androidx.appcompat.app.AlertDialog
import androidx.appcompat.app.AppCompatActivity
import androidx.lifecycle.lifecycleScope
import androidx.recyclerview.widget.LinearLayoutManager
import com.example.studenttracker.data.api.RetrofitClient
import com.example.studenttracker.data.model.SubjectCreateRequest
import com.example.studenttracker.data.repository.Repository
import com.example.studenttracker.databinding.ActivitySubjectManagementBinding
import kotlinx.coroutines.launch

class SubjectManagementActivity : AppCompatActivity() {

    private lateinit var binding: ActivitySubjectManagementBinding
    private lateinit var repository: Repository
    private lateinit var adapter: SubjectsAdapter

    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        binding = ActivitySubjectManagementBinding.inflate(layoutInflater)
        setContentView(binding.root)

        repository = Repository(RetrofitClient.getApiService(this))

        adapter = SubjectsAdapter()
        binding.rvSubjects.layoutManager = LinearLayoutManager(this)
        binding.rvSubjects.adapter = adapter

        binding.btnAddSubject.setOnClickListener {
            showAddSubjectDialog()
        }

        loadSubjects()
    }

    private fun loadSubjects() {
        lifecycleScope.launch {
            val result = repository.getSubjects()
            result.onSuccess { data ->
                adapter.submitList(data)
            }.onFailure { error ->
                Toast.makeText(this@SubjectManagementActivity, "Error loading subjects: ${error.message}", Toast.LENGTH_SHORT).show()
            }
        }
    }

    private fun showAddSubjectDialog() {
        val context = this
        val layout = LinearLayout(context).apply {
            orientation = LinearLayout.VERTICAL
            setPadding(50, 40, 50, 10)
        }

        val etCode = EditText(context).apply { hint = "Subject Code (e.g. CS506)" }
        val etName = EditText(context).apply { hint = "Subject Name" }
        val etCredits = EditText(context).apply { hint = "Credits (e.g. 4)" }

        layout.addView(etCode)
        layout.addView(etName)
        layout.addView(etCredits)

        AlertDialog.Builder(context)
            .setTitle("Add New Subject")
            .setView(layout)
            .setPositiveButton("Create") { _, _ ->
                val code = etCode.text.toString().trim()
                val name = etName.text.toString().trim()
                val credits = etCredits.text.toString().toIntOrNull() ?: 3

                if (code.isEmpty() || name.isEmpty()) {
                    Toast.makeText(context, "Subject Code and Name are required", Toast.LENGTH_SHORT).show()
                    return@setPositiveButton
                }

                lifecycleScope.launch {
                    val req = SubjectCreateRequest(
                        subjectCode = code,
                        subjectName = name,
                        departmentId = 1,
                        semester = 5,
                        credits = credits
                    )
                    val res = repository.createSubject(req)
                    res.onSuccess {
                        Toast.makeText(context, "Subject Created Successfully!", Toast.LENGTH_SHORT).show()
                        loadSubjects()
                    }.onFailure { err ->
                        Toast.makeText(context, "Failed: ${err.message}", Toast.LENGTH_LONG).show()
                    }
                }
            }
            .setNegativeButton("Cancel", null)
            .show()
    }
}
