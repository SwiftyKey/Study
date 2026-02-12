package com.example.qrscan.data.repo

import com.example.qrscan.auth.AuthManager
import com.example.qrscan.data.db.QrScanDao
import com.example.qrscan.data.model.QrScan
import kotlinx.coroutines.flow.Flow
import kotlinx.coroutines.flow.emptyFlow

class QrRepository(
    private val dao: QrScanDao,
    private val authManager: AuthManager
) {
    fun getHistory(): Flow<List<QrScan>> {
        val userId = authManager.currentUser?.uid ?: return emptyFlow()
        return dao.getScansByUser(userId)
    }

    suspend fun saveScan(content: String): Boolean {
        val userId = authManager.currentUser?.uid
        if (userId == null) return false
        dao.insert(QrScan(content = content, userId = userId))
        return true
    }
}