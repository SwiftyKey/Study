package com.example.lab5

import android.content.Context
import android.net.Uri
import androidx.core.content.FileProvider
import java.io.*

class Video(private val assetPath: String) {

    val name: String = assetPath.split("/").last().removeSuffix(".mp4")

    @Throws(IOException::class)
    fun getUriForPlayback(context: Context): Uri {
        val videoCacheDir = File(context.cacheDir, "videos")
        videoCacheDir.mkdirs()

        val outputFile = File(videoCacheDir, name)
        if (!outputFile.exists()) {
            context.assets.open(assetPath).use { input ->
                outputFile.outputStream().use { output ->
                    input.copyTo(output)
                }
            }
        }

        return FileProvider.getUriForFile(
            context,
            "${context.packageName}.fileprovider",
            outputFile
        )
    }
}