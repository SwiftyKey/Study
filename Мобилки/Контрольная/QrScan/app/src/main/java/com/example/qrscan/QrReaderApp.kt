package com.example.qrscan

import android.app.Application
import androidx.room.Room
import com.example.qrscan.data.db.AppDatabase

class QrReaderApp : Application() {
    private val _database: AppDatabase by lazy {
        Room.databaseBuilder(
            applicationContext,
            AppDatabase::class.java,
            "qr_scans.db"
        ).build()
    }

    val database: AppDatabase
        get() = _database
}