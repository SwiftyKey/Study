package com.example.lab2

import android.animation.AnimatorSet
import android.animation.ArgbEvaluator
import android.animation.ObjectAnimator
import android.animation.ValueAnimator
import android.content.res.ColorStateList
import android.graphics.Path
import android.os.Bundle
import android.view.View
import android.view.animation.AccelerateDecelerateInterpolator
import android.view.animation.LinearInterpolator
import androidx.appcompat.app.AppCompatActivity
import androidx.core.content.ContextCompat
import com.example.lab2.databinding.ActivityMainBinding

class MainActivity : AppCompatActivity() {
    private val blueSkyColor: Int by lazy {
        ContextCompat.getColor(this, R.color.blue_sky)
    }
    private val sunsetSkyColor: Int by lazy {
        ContextCompat.getColor(this, R.color.sunset_sky)
    }
    private val nightSkyColor: Int by lazy {
        ContextCompat.getColor(this, R.color.night_sky)
    }
    private val seaColor: Int by lazy {
        ContextCompat.getColor(this, R.color.sea)
    }

    private val brightSunColor: Int by lazy {
        ContextCompat.getColor(this, R.color.bright_sun)
    }

    private var ifDay = true
    private var sourceSunCoordX: Float = 0.0F
    private var sourceSunCoordY: Float = 0.0F

    private lateinit var binding: ActivityMainBinding

    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        binding = ActivityMainBinding.inflate(layoutInflater)
        val view = binding.root

        setContentView(view)

        binding.scene.setOnClickListener {
            if (ifDay) startNighAnimation(binding)
            else startDayAnimation(binding)
            ifDay = !ifDay
        }
    }

    private fun startNighAnimation(binding: ActivityMainBinding) {

        sourceSunCoordX = binding.sun.x
        sourceSunCoordY = binding.sun.y

        val startX = binding.sun.x
        val startY = binding.sun.y

        val endX = binding.scene.width.toFloat()
        val endY = binding.sky.height.toFloat()
       
        val path = Path().apply {
            moveTo(startX, startY)
           
            val controlX = binding.scene.width / 2f
            val controlY = 0f
            quadTo(controlX, controlY, endX, endY)
        }

        val sunPathAnimator = ObjectAnimator.ofFloat(binding.sun, View.X, View.Y, path).apply {
            duration = 5000
            interpolator = AccelerateDecelerateInterpolator()
        }

       
        val sunsetSkyAnimator = ValueAnimator.ofInt(blueSkyColor, sunsetSkyColor).apply {
            duration = 3000
            addUpdateListener { animator ->
                binding.sky.setBackgroundColor(animator.animatedValue as Int)
            }
        }
        sunsetSkyAnimator.setEvaluator(ArgbEvaluator())

        val nightSkyAnimator = ValueAnimator.ofInt(sunsetSkyColor, nightSkyColor).apply {
            duration = 2000
            addUpdateListener { animator ->
                binding.sky.setBackgroundColor(animator.animatedValue as Int)
            }
        }
        nightSkyAnimator.setEvaluator(ArgbEvaluator())

        val seaAnimator = ValueAnimator.ofInt(seaColor, nightSkyColor).apply {
            duration = 5000
            addUpdateListener { animator ->
                binding.sea.setBackgroundColor(animator.animatedValue as Int)
            }
        }
        seaAnimator.setEvaluator(ArgbEvaluator())

        val rotationAnimator = ObjectAnimator.ofFloat(binding.sun, "rotation", 0f, 30f).apply {
            duration = 5000
            interpolator = LinearInterpolator()
        }

        val sunColorAnimator = ValueAnimator.ofArgb(brightSunColor, sunsetSkyColor).apply {
            duration = 5000
            addUpdateListener { animator ->
                binding.sun.imageTintList = ColorStateList.valueOf(animator.animatedValue as Int)
            }
        }

        val animatorSet = AnimatorSet()
        animatorSet.play(sunPathAnimator)
            .with(sunsetSkyAnimator)
            .with(rotationAnimator)
            .with(sunColorAnimator)
            .before(nightSkyAnimator)
            .with(seaAnimator)

        animatorSet.start()
    }

    private fun startDayAnimation(binding: ActivityMainBinding) {
        val startX = -binding.sun.width.toFloat()
        val startY = binding.sky.height.toFloat()
        
        val endX = sourceSunCoordX
        val endY = sourceSunCoordY

        val path = Path().apply {
            moveTo(startX, startY)
            val controlX = -binding.scene.width / 2f
            val controlY = binding.sky.height.toFloat()
            quadTo(controlX, controlY, endX, endY)
        }

        val sunPathAnimator = ObjectAnimator.ofFloat(binding.sun, View.X, View.Y, path).apply {
            duration = 5000
            interpolator = AccelerateDecelerateInterpolator()
        }
       
        val sunsetSkyAnimator = ValueAnimator.ofInt(nightSkyColor, sunsetSkyColor).apply {
            duration = 3000
            addUpdateListener { animator ->
                binding.sky.setBackgroundColor(animator.animatedValue as Int)
            }
        }
        sunsetSkyAnimator.setEvaluator(ArgbEvaluator())

        val daySkyAnimator = ValueAnimator.ofInt(sunsetSkyColor, blueSkyColor).apply {
            duration = 2000
            addUpdateListener { animator ->
                binding.sky.setBackgroundColor(animator.animatedValue as Int)
            }
        }
        daySkyAnimator.setEvaluator(ArgbEvaluator())
       
        val seaAnimator = ValueAnimator.ofInt(nightSkyColor, seaColor).apply {
            duration = 5000
            addUpdateListener { animator ->
                binding.sea.setBackgroundColor(animator.animatedValue as Int)
            }
        }
        seaAnimator.setEvaluator(ArgbEvaluator())
       
        val rotationAnimator = ObjectAnimator.ofFloat(binding.sun, "rotation", 30f, 0f).apply {
            duration = 5000
            interpolator = LinearInterpolator()
        }

        val sunColorAnimator = ValueAnimator.ofArgb(sunsetSkyColor, brightSunColor).apply {
            duration = 5000
            addUpdateListener { animator ->
                binding.sun.imageTintList = ColorStateList.valueOf(animator.animatedValue as Int)
            }
        }

        val animatorSet = AnimatorSet()
        animatorSet.play(sunPathAnimator)
            .with(sunsetSkyAnimator)
            .with(rotationAnimator)
            .with(sunColorAnimator)
            .before(daySkyAnimator)
            .with(seaAnimator)

        animatorSet.start()
    }
}
