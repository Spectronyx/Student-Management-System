package com.example.studenttracker.ui.student

import android.view.LayoutInflater
import android.view.ViewGroup
import androidx.recyclerview.widget.RecyclerView
import com.example.studenttracker.data.model.Marks
import com.example.studenttracker.databinding.ItemMarkBinding

class MarksAdapter(
    private var marksList: List<Marks> = emptyList()
) : RecyclerView.Adapter<MarksAdapter.ViewHolder>() {

    fun submitList(newList: List<Marks>) {
        marksList = newList
        notifyDataSetChanged()
    }

    class ViewHolder(val binding: ItemMarkBinding) : RecyclerView.ViewHolder(binding.root)

    override fun onCreateViewHolder(parent: ViewGroup, viewType: Int): ViewHolder {
        val binding = ItemMarkBinding.inflate(LayoutInflater.from(parent.context), parent, false)
        return ViewHolder(binding)
    }

    override fun onBindViewHolder(holder: ViewHolder, position: Int) {
        val item = marksList[position]
        with(holder.binding) {
            tvSubjectCode.text = item.subjectCode ?: "SUB"
            tvSubjectName.text = item.subjectName ?: "Subject"
            tvGradeBadge.text = "${item.grade} (${item.gradePoint} GP)"
            tvInternal.text = "${item.internalMarks} / 30"
            tvAssignment.text = "${item.assignmentMarks} / 20"
            tvPractical.text = "${item.practicalMarks} / 20"
            tvFinalExam.text = "${item.finalExamMarks} / 50"
            tvTotalScore.text = "Total Score: ${item.totalMarks} / 100 | Credits: ${item.credits ?: 3}"
        }
    }

    override fun getItemCount(): Int = marksList.size
}
