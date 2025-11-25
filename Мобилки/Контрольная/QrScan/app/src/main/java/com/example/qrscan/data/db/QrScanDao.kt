package com.example.qrscan.data.db

import androidx.room.*
import com.example.qrscan.data.model.QrScan
import kotlinx.coroutines.flow.Flow

@Dao
interface QrScanDao {
    @Insert
    suspend fun insert(scan: QrScan)

    @Query("SELECT * FROM qr_scans WHERE userId = :userId ORDER BY timestamp DESC")
    fun getScansByUser(userId: String): Flow<List<QrScan>>
}