package com.example.qrscan.ui.main

import android.text.util.Linkify
import android.view.LayoutInflater
import android.view.ViewGroup
import android.widget.TextView
import androidx.core.text.util.LinkifyCompat
import androidx.recyclerview.widget.DiffUtil
import androidx.recyclerview.widget.ListAdapter
import androidx.recyclerview.widget.RecyclerView
import com.example.qrscan.data.model.QrScan
import com.example.qrscan.R

class HistoryAdapter(
    private val onItemClicked: (String) -> Unit
) : ListAdapter<QrScan, HistoryAdapter.ViewHolder>(DiffCallback()) {

    class ViewHolder(val textView: TextView) : RecyclerView.ViewHolder(textView)

    override fun onCreateViewHolder(parent: ViewGroup, viewType: Int): ViewHolder {
        val textView = LayoutInflater.from(parent.context)
            .inflate(R.layout.item_history, parent, false) as TextView
        return ViewHolder(textView)
    }

    override fun onBindViewHolder(holder: ViewHolder, position: Int) {
        val scan = getItem(position)
        holder.textView.text = scan.content

        LinkifyCompat.addLinks(holder.textView, Linkify.WEB_URLS)

        holder.textView.setOnClickListener {
            onItemClicked(scan.content)
        }
    }

    class DiffCallback : DiffUtil.ItemCallback<QrScan>() {
        override fun areItemsTheSame(oldItem: QrScan, newItem: QrScan) = oldItem.id == newItem.id
        override fun areContentsTheSame(oldItem: QrScan, newItem: QrScan) = oldItem == newItem
    }
}