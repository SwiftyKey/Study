package com.example.lab5

import android.content.Context
import android.content.Intent
import android.widget.Toast
import androidx.databinding.BaseObservable
import androidx.databinding.Bindable
import java.io.IOException

class VideoVM : BaseObservable() {
    var video: Video? = null
        set(value) {
            field = value
            notifyChange()
        }

    @get:Bindable
    val title: String?
        get() = video?.name + ".mp4"

    fun onClickButton(context: Context) {
        try {
            val uri = video?.getUriForPlayback(context) ?: return
            val intent = Intent(Intent.ACTION_VIEW).apply {
                setDataAndType(uri, "video/*")
                addFlags(Intent.FLAG_GRANT_READ_URI_PERMISSION)
                addFlags(Intent.FLAG_ACTIVITY_NEW_TASK)
            }
            context.startActivity(intent)
        } catch (e: IOException) {
            e.printStackTrace()
        }
    }
}