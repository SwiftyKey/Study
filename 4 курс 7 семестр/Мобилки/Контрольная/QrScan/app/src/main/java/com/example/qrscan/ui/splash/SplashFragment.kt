package com.example.qrscan.ui.splash

import android.os.Bundle
import android.os.Handler
import android.os.Looper
import android.view.LayoutInflater
import android.view.View
import android.view.ViewGroup
import androidx.fragment.app.Fragment
import androidx.navigation.fragment.findNavController
import com.example.qrscan.R
import com.google.firebase.auth.FirebaseAuth

class SplashFragment : Fragment() {
    override fun onCreateView(inflater: LayoutInflater, container: ViewGroup?, savedInstanceState: Bundle?): View? {
        return inflater.inflate(R.layout.fragment_splash, container, false)
    }

    override fun onViewCreated(view: View, savedInstanceState: Bundle?) {
        super.onViewCreated(view, savedInstanceState)
        Handler(Looper.getMainLooper()).postDelayed({
            val currentUser = FirebaseAuth.getInstance().currentUser
            if (currentUser != null) {
                findNavController().navigate(R.id.action_splash_to_main)
            } else {
                findNavController().navigate(R.id.action_splash_to_scanner)
            }
        }, 800)
    }
}