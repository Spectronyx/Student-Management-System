package com.example.studenttracker.ui.faculty

import android.os.Bundle
import android.widget.Toast
import androidx.appcompat.app.AppCompatActivity
import androidx.lifecycle.lifecycleScope
import com.example.studenttracker.data.api.RetrofitClient
import com.example.studenttracker.data.model.MarkEntryRequest
import com.example.studenttracker.data.repository.Repository
import com.example.studenttracker.databinding.ActivityMarksManagementBinding
import kotlinx.coroutines.launch

class MarksManagementActivity : AppCompatActivity() {

    private lateinit var binding: ActivityMarksManagementBinding
    private lateinit var repository: Repository

    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        binding = ActivityMarksManagementBinding.inflate(layoutInflater)
        setContentView(binding.root)

        repository = Repository(RetrofitClient.getApiService(this))

        binding.btnSubmitMarks.setOnClickListener {
            val studentIdStr = binding.etStudentId.text.toString().trim()
            val subjectIdStr = binding.etSubjectId.text.toString().trim()

            if (studentIdStr.isEmpty() || subjectIdStr.isEmpty()) {
                Toast.makeText(this, "Please enter Student ID and Subject ID", Toast.LENGTH_SHORT).show()
                return@setOnClickListener
            }

            val studentId = studentIdStr.toInt()
            val subjectId = subjectIdStr.toInt()
            val internal = binding.etInternalMarks.text.toString().toDoubleOrNull() ?: 0.0
            val assignment = binding.etAssignmentMarks.text.toString().toDoubleOrNull() ?: 0.0
            val practical = binding.etPracticalMarks.text.toString().toDoubleOrNull() ?: 0.0
            val finalExam = binding.etFinalExamMarks.text.toString().toDoubleOrNull() ?: 0.0

            lifecycleScope.launch {
                val req = MarkEntryRequest(
                    studentId = studentId,
                    subjectId = subjectId,
                    internalMarks = internal,
                    assignmentMarks = assignment,
                    practicalMarks = practical,
                    finalExamMarks = finalExam
                )
                val result = repository.addOrUpdateMarks(req)
                result.onSuccess { data ->
                    Toast.makeText(
                        this@MarksManagementActivity,
                        "Marks saved! Total: ${data.totalMarks}, Grade: ${data.grade}",
                        Toast.LENGTH_LONG
                    ).show()
                    finish()
                }.onFailure { error ->
                    Toast.makeText(this@MarksManagementActivity, "Failed: ${error.message}", Toast.LENGTH_LONG).show()
                }
            }
        }
    }
}
