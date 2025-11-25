package com.example.qrscan.viewmodel

import android.app.Application
import androidx.lifecycle.AndroidViewModel
import androidx.lifecycle.viewModelScope
import com.example.qrscan.QrReaderApp
import com.example.qrscan.auth.AuthManager
import com.example.qrscan.data.repo.QrRepository
import kotlinx.coroutines.flow.SharingStarted
import kotlinx.coroutines.flow.StateFlow
import kotlinx.coroutines.flow.stateIn
import kotlinx.coroutines.launch

class SharedViewModel(application: Application) : AndroidViewModel(application) {

    private val authManager = AuthManager()
    private val database = (application as QrReaderApp).database

    private val repository = QrRepository(database.qrScanDao(), authManager)

    val history = repository.getHistory()

    fun saveScan(content: String) {
        viewModelScope.launch {
            repository.saveScan(content)
        }
    }

    fun signOut() {
        authManager.signOut()
    }

    suspend fun signIn(email: String, password: String) = authManager.signIn(email, password)
    suspend fun signUp(email: String, password: String) = authManager.signUp(email, password)
}