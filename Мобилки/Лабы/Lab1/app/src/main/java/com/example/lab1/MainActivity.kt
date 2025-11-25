package com.example.lab1

import androidx.appcompat.app.AppCompatActivity
import android.os.Bundle
import androidx.appcompat.app.AlertDialog
import com.example.lab1.databinding.ActivityMainBinding

class MainActivity : AppCompatActivity() {
    private lateinit var binding: ActivityMainBinding

    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        binding = ActivityMainBinding.inflate(layoutInflater)
        val view = binding.root
        setContentView(view)

        binding.glinka.setOnClickListener {
            AlertDialog.Builder(this)
                .setTitle(binding.glinkaText.text)
                .setMessage("Михаил Иванович Глинка — не только основоположник русской классики. " +
                        "Он был первым, кто добился широкого признания за рубежом. " +
                        "Его произведения легли на основу русской народной музыки, " +
                        "в свое время Глинка стал в этом вопросе новатором. " +
                        "Михаил Иванович лично знал величайших литераторов своего времени: " +
                        "А.С.Пушкина, В.А.Жуковского, А.С.Грибоедова, А.А.Дельвига. " +
                        "Благодаря своей поездке по Европе, длившейся несколько лет, " +
                        "великий русский композитор впитал и мировой опыт.")
                .setPositiveButton("Вернуться"){_,_->}
                .show()
        }
        binding.borodin.setOnClickListener {
            AlertDialog.Builder(this)
                .setTitle(binding.borodinText.text)
                .setMessage("Великий русский композитор Александр Бородин обладал многими талантами. " +
                        "Ученый-химик, врач, педагог и литератор писал музыку, " +
                        "ставшую шедевром русской классики. " +
                        "Интересно, что у Александра Бородина не было профессиональных учителей, " +
                        "искусство писать музыку он освоил сам. Толчком к творчеству стали женитьба " +
                        "на известной пианистке Е.С.Протопоповой и восхищение произведениями М. Глинки.")
                .setPositiveButton("Вернуться"){_,_->}
                .show()
        }
        binding.mussorgsky.setOnClickListener {
            AlertDialog.Builder(this)
                .setTitle(binding.mussorgskyText.text)
                .setMessage("Модест Петрович Мусоргский — не просто великий русский композитор" +
                        " и член «Могучей кучки», но и великий новатор. Его творчество потрясало и " +
                        "опережало время. В своих грандиозных произведениях — операх «Борис Годунов» " +
                        "и «Хованщина» он показал страницы русской истории так, " +
                        "как никто до этого не смог этого сделать в русской музыке.")
                .setPositiveButton("Вернуться"){_,_->}
                .show()
        }
    }

}
