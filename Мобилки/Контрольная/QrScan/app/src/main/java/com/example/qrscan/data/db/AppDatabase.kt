package com.example.qrscan.data.db
import androidx.room.Database
import androidx.room.RoomDatabase
import com.example.qrscan.data.model.QrScan

@Database(entities = [QrScan::class], version = 1)
abstract class AppDatabase : RoomDatabase() {
    abstract fun qrScanDao(): QrScanDao
}