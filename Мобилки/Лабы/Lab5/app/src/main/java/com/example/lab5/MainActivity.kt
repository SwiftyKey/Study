package com.example.lab5

import android.os.Bundle
import android.view.ViewGroup
import androidx.appcompat.app.AppCompatActivity
import androidx.databinding.DataBindingUtil
import androidx.recyclerview.widget.GridLayoutManager
import androidx.recyclerview.widget.RecyclerView
import com.example.lab5.databinding.ActivityMainBinding
import com.example.lab5.databinding.ListItemSoundBinding
import com.example.lab5.databinding.ListItemVideoBinding

class MainActivity : AppCompatActivity() {
    private lateinit var mediaRepo: MediaRepository
    private lateinit var binder: ActivityMainBinding
    private lateinit var mediaItems: List<MediaItem>

    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        binder = DataBindingUtil.setContentView(this, R.layout.activity_main)
        mediaRepo = MediaRepository(assets)

        mediaItems = mediaRepo.sounds.map { MediaItem.Sound(it) } +
                mediaRepo.videos.map { MediaItem.Video(it) }

        binder.recyclerView.apply {
            layoutManager = GridLayoutManager(context, 2)
            adapter = MediaAdapter(mediaItems)
        }
    }

    override fun onDestroy() {
        super.onDestroy()
        mediaRepo.release()
    }

    inner class SoundHolder(private val binding: ListItemSoundBinding) :
        RecyclerView.ViewHolder(binding.root) {
        init {
            binding.viewModel = SoundVM()
        }
        fun bind(sound: Sound) {
            binding.viewModel?.sound = sound as Sound?
            binding.executePendingBindings()
        }
    }

    inner class VideoHolder(private val binding: ListItemVideoBinding) :
        RecyclerView.ViewHolder(binding.root) {
        init {
            binding.viewModel = VideoVM()
        }
        fun bind(video: Video) {
            binding.viewModel?.video = video as Video?
            binding.executePendingBindings()
        }
    }

    // --- Adapter ---
    inner class MediaAdapter(private val items: List<MediaItem>) :
        RecyclerView.Adapter<RecyclerView.ViewHolder>() {

        val TYPE_SOUND = 0
        val TYPE_VIDEO = 1

        override fun getItemViewType(position: Int): Int {
            return when (items[position]) {
                is MediaItem.Sound -> TYPE_SOUND
                is MediaItem.Video -> TYPE_VIDEO
            }
        }

        override fun onCreateViewHolder(parent: ViewGroup, viewType: Int): RecyclerView.ViewHolder {
            return when (viewType) {
                TYPE_SOUND -> {
                    val binding = DataBindingUtil.inflate<ListItemSoundBinding>(
                        layoutInflater, R.layout.list_item_sound, parent, false
                    )
                    SoundHolder(binding)
                }
                TYPE_VIDEO -> {
                    val binding = DataBindingUtil.inflate<ListItemVideoBinding>(
                        layoutInflater, R.layout.list_item_video, parent, false
                    )
                    VideoHolder(binding)
                }
                else -> throw IllegalArgumentException("Unknown view type")
            }
        }

        override fun onBindViewHolder(holder: RecyclerView.ViewHolder, position: Int) {
            when (val item = items[position]) {
                is MediaItem.Sound -> (holder as SoundHolder).bind(item.sound)
                is MediaItem.Video -> (holder as VideoHolder).bind(item.video)
            }
        }

        override fun getItemCount() = items.size
    }
}