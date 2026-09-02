package com.example.studenttracker.ui.admin

import android.view.LayoutInflater
import android.view.ViewGroup
import androidx.recyclerview.widget.RecyclerView
import com.example.studenttracker.data.model.Subject
import com.example.studenttracker.databinding.ItemSubjectBinding

class SubjectsAdapter(
    private var subjectsList: List<Subject> = emptyList()
) : RecyclerView.Adapter<SubjectsAdapter.ViewHolder>() {

    fun submitList(newList: List<Subject>) {
        subjectsList = newList
        notifyDataSetChanged()
    }

    class ViewHolder(val binding: ItemSubjectBinding) : RecyclerView.ViewHolder(binding.root)

    override fun onCreateViewHolder(parent: ViewGroup, viewType: Int): ViewHolder {
        val binding = ItemSubjectBinding.inflate(LayoutInflater.from(parent.context), parent, false)
        return ViewHolder(binding)
    }

    override fun onBindViewHolder(holder: ViewHolder, position: Int) {
        val item = subjectsList[position]
        with(holder.binding) {
            tvSubjectCode.text = item.subjectCode
            tvSubjectName.text = item.subjectName
            tvAttendancePct.text = "Semester ${item.semester} | Credits: ${item.credits}"
            tvGradeBadge.text = "${item.credits} CR"
            tvTotalMarks.text = item.departmentCode ?: "Dept"
        }
    }

    override fun getItemCount(): Int = subjectsList.size
}
