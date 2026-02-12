package com.example.lab4

import android.annotation.SuppressLint
import android.content.Intent
import android.content.pm.ResolveInfo
import androidx.appcompat.app.AppCompatActivity
import android.os.Bundle
import android.view.LayoutInflater
import android.view.View
import android.view.ViewGroup
import android.widget.TextView
import androidx.recyclerview.widget.LinearLayoutManager
import androidx.recyclerview.widget.RecyclerView


class MainActivity : AppCompatActivity() {
    private lateinit var recyclerView: RecyclerView
    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        setContentView(R.layout.activity_main)
        recyclerView=findViewById(R.id.main)
        recyclerView.layoutManager= LinearLayoutManager(this)
        setupAdapter()
    }
    @SuppressLint("QueryPermissionsNeeded")
    private fun setupAdapter( ) {
        val startupIntent = Intent(Intent.ACTION_MAIN).apply {
            addCategory(Intent.CATEGORY_LAUNCHER)
        }
        val activities = packageManager.queryIntentActivities(startupIntent, 0)
        activities.sortWith { a, b ->
            String.CASE_INSENSITIVE_ORDER.compare(
                a.loadLabel(packageManager).toString(),
                b.loadLabel(packageManager).toString()
            )
        }
        recyclerView.adapter = ActivityAdapter(activities)
    }

    private class ActivityHolder(itemView: View) :
        RecyclerView.ViewHolder(itemView) {
        private val nameTextView = itemView as TextView
        private lateinit var resolveInfo: ResolveInfo

        init {
            nameTextView.setOnClickListener{
                val activityInfo=resolveInfo.activityInfo
                val intent=Intent(Intent.ACTION_MAIN).apply {
                    setClassName(activityInfo.applicationInfo.packageName,
                        activityInfo.name)
                    addFlags(Intent.FLAG_ACTIVITY_NEW_TASK)
                }
                val context = itemView.context
                context.startActivity(intent)
            }
        }
        fun bindActivity(resolveInfo: ResolveInfo) {
            this.resolveInfo = resolveInfo
            val packageManager = itemView.context.packageManager
            val appName = resolveInfo.loadLabel(packageManager).toString()
            nameTextView.text = appName
        }
    }

    private class ActivityAdapter(val activities: List<ResolveInfo>) :
        RecyclerView.Adapter<ActivityHolder>() {
        override fun onCreateViewHolder(container: ViewGroup, viewType: Int): ActivityHolder {
            val layoutInflater = LayoutInflater.from(container.context)
            val view = layoutInflater
                .inflate(android.R.layout.simple_list_item_1, container, false)
            return ActivityHolder(view)
        }
        override fun onBindViewHolder(holder: ActivityHolder, position: Int) {
            val resolveInfo = activities[position]
            holder.bindActivity(resolveInfo)
        }
        override fun getItemCount(): Int {
            return activities.size
        }
    }
}
