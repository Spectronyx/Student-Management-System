package com.example.studenttracker.ui.admin

import android.view.LayoutInflater
import android.view.ViewGroup
import androidx.recyclerview.widget.RecyclerView
import com.example.studenttracker.data.model.Student
import com.example.studenttracker.databinding.ItemStudentBinding

class StudentsAdapter(
    private var studentsList: List<Student> = emptyList()
) : RecyclerView.Adapter<StudentsAdapter.ViewHolder>() {

    fun submitList(newList: List<Student>) {
        studentsList = newList
        notifyDataSetChanged()
    }

    class ViewHolder(val binding: ItemStudentBinding) : RecyclerView.ViewHolder(binding.root)

    override fun onCreateViewHolder(parent: ViewGroup, viewType: Int): ViewHolder {
        val binding = ItemStudentBinding.inflate(LayoutInflater.from(parent.context), parent, false)
        return ViewHolder(binding)
    }

    override fun onBindViewHolder(holder: ViewHolder, position: Int) {
        val item = studentsList[position]
        with(holder.binding) {
            tvStudentName.text = "${item.firstName} ${item.lastName}"
            tvEnrollment.text = "Enrollment: ${item.enrollmentNumber}"
            tvDepartmentPill.text = "${item.departmentCode ?: "CSE"} | Sem ${item.semester}"
            tvStudentEmail.text = item.email
        }
    }

    override fun getItemCount(): Int = studentsList.size
}
