package com.example.qrscan.ui.main

import android.content.Intent
import android.os.Bundle
import android.net.Uri
import android.view.LayoutInflater
import android.view.View
import android.view.ViewGroup
import android.widget.Toast
import androidx.fragment.app.Fragment
import androidx.fragment.app.viewModels
import androidx.lifecycle.lifecycleScope
import androidx.recyclerview.widget.LinearLayoutManager
import com.example.qrscan.viewmodel.SharedViewModel
import com.example.qrscan.databinding.FragmentMainBinding
import androidx.navigation.fragment.findNavController
import androidx.recyclerview.widget.DividerItemDecoration
import com.example.qrscan.R
import kotlinx.coroutines.launch

class MainFragment : Fragment() {

    private var _binding: FragmentMainBinding? = null
    private val binding get() = _binding!!
    private val viewModel: SharedViewModel by viewModels({ requireActivity() })

    override fun onCreateView(inflater: LayoutInflater, container: ViewGroup?, savedInstanceState: Bundle?): View {
        _binding = FragmentMainBinding.inflate(inflater, container, false)
        return binding.root
    }

    override fun onViewCreated(view: View, savedInstanceState: Bundle?) {
        super.onViewCreated(view, savedInstanceState)

        val adapter = HistoryAdapter { content ->
            if (content.startsWith("http://") || content.startsWith("https://")) {
                val intent = Intent(Intent.ACTION_VIEW, Uri.parse(content))
                startActivity(intent)
            } else {
                Toast.makeText(context, "Текст: $content", Toast.LENGTH_SHORT).show()
            }
        }
        binding.recyclerView.adapter = adapter
        binding.recyclerView.layoutManager = LinearLayoutManager(context)

        val divider = DividerItemDecoration(context, DividerItemDecoration.VERTICAL)
        binding.recyclerView.addItemDecoration(divider)

        viewLifecycleOwner.lifecycleScope.launch {
            viewModel.history.collect { scans ->
                adapter.submitList(scans)
            }
        }

        binding.btnScan.setOnClickListener {
            findNavController().navigate(R.id.action_main_to_scanner)
        }

        binding.btnSignOut.setOnClickListener {
            viewModel.signOut()
            findNavController().navigate(R.id.action_main_to_scanner)
        }
    }

    override fun onDestroyView() {
        super.onDestroyView()
        _binding = null
    }
}