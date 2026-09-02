package com.example.studenttracker.ui.student

import android.view.LayoutInflater
import android.view.View
import android.view.ViewGroup
import androidx.recyclerview.widget.RecyclerView
import com.example.studenttracker.data.model.SubjectPerformance
import com.example.studenttracker.databinding.ItemSubjectBinding

class SubjectPerformanceAdapter(
    private var subjects: List<SubjectPerformance> = emptyList()
) : RecyclerView.Adapter<SubjectPerformanceAdapter.ViewHolder>() {

    fun submitList(newList: List<SubjectPerformance>) {
        subjects = newList
        notifyDataSetChanged()
    }

    class ViewHolder(val binding: ItemSubjectBinding) : RecyclerView.ViewHolder(binding.root)

    override fun onCreateViewHolder(parent: ViewGroup, viewType: Int): ViewHolder {
        val binding = ItemSubjectBinding.inflate(LayoutInflater.from(parent.context), parent, false)
        return ViewHolder(binding)
    }

    override fun onBindViewHolder(holder: ViewHolder, position: Int) {
        val item = subjects[position]
        with(holder.binding) {
            tvSubjectCode.text = item.subjectCode
            tvSubjectName.text = item.subjectName
            tvAttendancePct.text = "Attendance: ${item.attendancePercentage}%"
            tvGradeBadge.text = item.grade
            tvTotalMarks.text = "${item.totalMarks} / 100"

            if (item.attendanceWarning) {
                tvWarningPill.visibility = View.VISIBLE
            } else {
                tvWarningPill.visibility = View.GONE
            }
        }
    }

    override fun getItemCount(): Int = subjects.size
}
