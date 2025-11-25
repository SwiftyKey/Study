package com.example.lab5

sealed class MediaItem {
    data class Sound(val sound: com.example.lab5.Sound) : MediaItem()
    data class Video(val video: com.example.lab5.Video) : MediaItem()
}