package com.example.lab5

import android.content.res.AssetManager
import android.media.SoundPool
import android.util.Log

private const val TAG = "MediaRepository"
private const val SOUNDS_FOLDER = "sample_sounds"
private const val VIDEOS_FOLDER = "sample_videos"
private const val MAX_SOUNDS = 5

class MediaRepository(private val assets: AssetManager) {
    private val soundPool = SoundPool.Builder().setMaxStreams(MAX_SOUNDS).build()
    val sounds: List<Sound> = loadSounds()
    val videos: List<Video> = loadVideos()

    fun release() {
        soundPool.release()
    }

    private fun loadSounds(): List<Sound> {
        return try {
            val files = assets.list(SOUNDS_FOLDER) ?: emptyArray()
            files.filter { it.endsWith(".mp3") }
                .map { path -> Sound(soundPool, "$SOUNDS_FOLDER/$path").also { loadSound(it) } }
        } catch (e: Exception) {
            Log.e(TAG, "Failed to load sounds", e)
            emptyList()
        }
    }

    private fun loadVideos(): List<Video> {
        return try {
            val files = assets.list(VIDEOS_FOLDER) ?: emptyArray()
            files.filter { it.endsWith(".mp4") || it.endsWith(".3gp") }
                .map { path -> Video("$VIDEOS_FOLDER/$path") }
        } catch (e: Exception) {
            Log.e(TAG, "Failed to load videos", e)
            emptyList()
        }
    }

    private fun loadSound(sound: Sound) {
        val afd = assets.openFd(sound.assetPath)
        sound.soundId = soundPool.load(afd, 1)
    }
}