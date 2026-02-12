package com.example.qrscan.ui.auth

import android.os.Bundle
import android.view.LayoutInflater
import android.view.View
import android.view.ViewGroup
import android.widget.Toast
import androidx.fragment.app.Fragment
import androidx.fragment.app.viewModels
import androidx.lifecycle.lifecycleScope
import androidx.navigation.fragment.findNavController
import com.example.qrscan.R
import com.example.qrscan.databinding.FragmentLoginBinding
import com.example.qrscan.viewmodel.SharedViewModel
import kotlinx.coroutines.launch

class LoginFragment : Fragment() {
    private var isProcessing = false
    private var _binding: FragmentLoginBinding? = null
    private val binding get() = _binding!!
    private val viewModel: SharedViewModel by viewModels({ requireActivity() })

    override fun onCreateView(
        inflater: LayoutInflater,
        container: ViewGroup?,
        savedInstanceState: Bundle?
    ): View {
        _binding = FragmentLoginBinding.inflate(inflater, container, false)
        return binding.root
    }

    override fun onViewCreated(view: View, savedInstanceState: Bundle?) {
        super.onViewCreated(view, savedInstanceState)

        binding.btnLogin.setOnClickListener {
            if (isProcessing) return@setOnClickListener
            isProcessing = true
            val email = binding.etEmail.text.toString().trim()
            val password = binding.etPassword.text.toString().trim()
            if (email.isNotEmpty() && password.isNotEmpty()) {
                login(email, password)
            } else {
                Toast.makeText(context, "Заполните все поля", Toast.LENGTH_SHORT).show()
            }
        }

        binding.btnRegister.setOnClickListener {
            val email = binding.etEmail.text.toString().trim()
            val password = binding.etPassword.text.toString().trim()
            if (email.isNotEmpty() && password.isNotEmpty()) {
                register(email, password)
            } else {
                Toast.makeText(context, "Заполните все поля", Toast.LENGTH_SHORT).show()
            }
        }
    }

    private fun login(email: String, password: String) {
        viewLifecycleOwner.lifecycleScope.launch {
            try {
                val result = viewModel.signIn(email, password)
                if (result.isSuccess) {
                    if (isAdded && !requireActivity().isFinishing) {
                        navigateToMain()
                    }
                } else {
                    Toast.makeText(context, "Ошибка: ${result.exceptionOrNull()?.message}", Toast.LENGTH_LONG).show()
                }
            } catch (e: Exception) {
                if (isAdded) {
                    Toast.makeText(context, "Ошибка: ${e.message}", Toast.LENGTH_LONG).show()
                }
            }
        }
    }

    private fun register(email: String, password: String) {
        viewLifecycleOwner.lifecycleScope.launch {
            val result = viewModel.signUp(email, password)
            if (result.isSuccess) {
                navigateToMain()
            } else {
                Toast.makeText(context, "Ошибка регистрации: ${result.exceptionOrNull()?.message}", Toast.LENGTH_LONG).show()
            }
        }
    }

    private fun navigateToMain() {
        findNavController().navigate(R.id.action_login_to_main)
    }

    override fun onDestroyView() {
        super.onDestroyView()
        _binding = null
    }
}