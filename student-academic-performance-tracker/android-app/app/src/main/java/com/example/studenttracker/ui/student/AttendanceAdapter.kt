package com.example.studenttracker.ui.student

import android.view.LayoutInflater
import android.view.View
import android.view.ViewGroup
import androidx.core.content.ContextCompat
import androidx.recyclerview.widget.RecyclerView
import com.example.studenttracker.R
import com.example.studenttracker.data.model.Attendance
import com.example.studenttracker.databinding.ItemAttendanceBinding

class AttendanceAdapter(
    private var attendanceList: List<Attendance> = emptyList()
) : RecyclerView.Adapter<AttendanceAdapter.ViewHolder>() {

    fun submitList(newList: List<Attendance>) {
        attendanceList = newList
        notifyDataSetChanged()
    }

    class ViewHolder(val binding: ItemAttendanceBinding) : RecyclerView.ViewHolder(binding.root)

    override fun onCreateViewHolder(parent: ViewGroup, viewType: Int): ViewHolder {
        val binding = ItemAttendanceBinding.inflate(LayoutInflater.from(parent.context), parent, false)
        return ViewHolder(binding)
    }

    override fun onBindViewHolder(holder: ViewHolder, position: Int) {
        val item = attendanceList[position]
        val pct = item.attendancePercentage
        val isWarning = pct < 75.0

        with(holder.binding) {
            tvSubjectCode.text = item.subjectCode ?: "SUB"
            tvSubjectName.text = item.subjectName ?: "Subject"
            tvClassCounts.text = "Classes: ${item.classesAttended} attended out of ${item.classesHeld} held"
            tvAttendancePctPill.text = "$pct%"

            if (isWarning) {
                tvWarning.visibility = View.VISIBLE
                tvAttendancePctPill.setBackgroundColor(ContextCompat.getColor(root.context, R.color.accent_rose))
            } else {
                tvWarning.visibility = View.GONE
                tvAttendancePctPill.setBackgroundColor(ContextCompat.getColor(root.context, R.color.accent_emerald))
            }
        }
    }

    override fun getItemCount(): Int = attendanceList.size
}
