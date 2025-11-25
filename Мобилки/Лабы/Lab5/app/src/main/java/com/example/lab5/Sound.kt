package com.example.lab5

import android.media.SoundPool

class Sound(val soundPool : SoundPool,val assetPath: String, var soundId: Int? = null) {
    val nаmе = assetPath.split("/").last().removeSuffix(".mp3")
    var pool: SoundPool = soundPool

    fun play(){
        soundId?.let { pool.play(it,1.0f, 1.0f, 1, 0, 1.0f) }
    }
}
