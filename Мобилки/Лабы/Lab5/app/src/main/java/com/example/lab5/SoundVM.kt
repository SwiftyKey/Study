package com.example.lab5

import androidx.databinding.BaseObservable
import androidx.databinding.Bindable

class SoundVM: BaseObservable() {
    var sound:Sound?=null
        set(sound) {
            field=sound
            notifyChange()
        }

    @get:Bindable
    val title: String?
        get( )=sound?.nаmе + ".mp3"

    fun onClickButton(){
        sound?.run { play() }
    }
}
