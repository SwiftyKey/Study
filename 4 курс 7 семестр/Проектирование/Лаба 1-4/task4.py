import tkinter as tk
from tkinter import ttk, messagebox, scrolledtext
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import random

# ========================= #
# Основная логика программы #
# ========================= #


class RandomSequenceGenerator:
    """
    Класс для генерации нормально распределённых последовательностей,
    их объединения и статистического анализа.
    """

    def __init__(self):
        self.sequences = []
        self.combined_data = np.array([])
        self.mean = 0.0
        self.variance = 0.0
        self.hist_data = None
        self.bin_edges = None

    def generate_sequences(self):
        """Генерация трёх последовательностей по заданным параметрам."""
        # Сброс предыдущих данных
        self.sequences = []

        # Параметры: (mean, variance)
        params = [(2, 4), (3, 3), (4, 4)]

        for mean, variance in params:
            std = np.sqrt(variance)  # стандартное отклонение
            seq = np.random.normal(loc=mean, scale=std, size=30)
            self.sequences.append(seq)

    def combine_and_sort(self):
        """Объединение всех последовательностей и сортировка по возрастанию."""
        if not self.sequences:
            raise ValueError("Сначала нужно сгенерировать последовательности.")
        self.combined_data = np.sort(np.concatenate(self.sequences))

    def compute_statistics(self):
        """Вычисление среднего и дисперсии объединённого массива."""
        if len(self.combined_data) == 0:
            raise ValueError("Нет данных для анализа.")
        self.mean = np.mean(self.combined_data)
        self.variance = np.var(self.combined_data, ddof=0)

    def create_histogram(self):
        """Построение гистограммы с 10 интервалами."""
        if len(self.combined_data) == 0:
            raise ValueError("Нет данных для гистограммы.")
        self.hist_data, self.bin_edges = np.histogram(
            self.combined_data, bins=10)


# =========================== #
# Графический интерфейс (GUI) #
# =========================== #

class App:
    def __init__(self, root):
        self.root = root
        self.root.title("Анализ случайных последовательностей")
        self.root.geometry("1000x700")
        self.root.resizable(True, True)

        self.generator = RandomSequenceGenerator()

        self.setup_ui()
        self.show_help_intro()

    def setup_ui(self):
        """Настройка пользовательского интерфейса."""
        # Верхняя панель: кнопки
        top_frame = ttk.Frame(self.root, padding=10)
        top_frame.pack(fill='x')

        ttk.Button(top_frame, text="Сгенерировать данные",
                   command=self.generate_data).pack(side='left', padx=5)
        ttk.Button(top_frame, text="Показать данные",
                   command=self.show_data).pack(side='left', padx=5)
        ttk.Button(top_frame, text="Показать статистику",
                   command=self.show_stats).pack(side='left', padx=5)
        ttk.Button(top_frame, text="Справка",
                   command=self.show_help).pack(side='left', padx=5)

        # Основной контейнер: разделение на текст и график
        main_paned = ttk.PanedWindow(self.root, orient=tk.HORIZONTAL)
        main_paned.pack(fill='both', expand=True, padx=10, pady=5)

        # Левая часть — текст
        text_frame = ttk.LabelFrame(main_paned, text="Результаты", padding=10)
        main_paned.add(text_frame, weight=3)

        self.text_area = scrolledtext.ScrolledText(
            text_frame, wrap=tk.WORD, height=20, font=("Courier", 10))
        self.text_area.pack(fill='both', expand=True)

        # Правая часть — график
        plot_frame = ttk.LabelFrame(main_paned, text="Гистограмма", padding=10)
        main_paned.add(plot_frame, weight=5)

        self.fig, self.ax = plt.subplots(figsize=(6, 5), dpi=100)
        self.canvas = FigureCanvasTkAgg(self.fig, plot_frame)
        self.canvas.get_tk_widget().pack(fill='both', expand=True)

    def show_help_intro(self):
        """Показ краткого введения при запуске."""
        msg = (
            "Добро пожаловать в программу анализа случайных последовательностей!\n\n"
            "Эта программа:\n"
            "• Генерирует три последовательности по 30 чисел с нормальным распределением\n"
            "• Объединяет их, сортирует и анализирует\n"
            "• Строит гистограмму (10 интервалов)\n\n"
            "Используйте кнопки выше для управления.\n"
            "Нажмите 'Справка', чтобы узнать больше."
        )
        self.text_area.insert(tk.END, msg)
        self.text_area.config(state='disabled')

    def show_help(self):
        """Отображение справочной информации."""
        help_text = (
            "СПРАВКА:\n"
            "────────────────────────────────────────────\n"
            "1. Сгенерировать данные — создать три последовательности:\n"
            "   • (mx=2, Dx=4)\n"
            "   • (mx=3, Dx=3)\n"
            "   • (mx=4, Dx=4)\n\n"
            "2. Показать данные — вывести объединённый и отсортированный массив.\n\n"
            "3. Показать статистику — среднее и дисперсию.\n\n"
            "4. Все операции можно повторять.\n\n"
            "Если возникла ошибка — проверьте, сгенерированы ли данные.\n"
            "Программа позволяет исправлять ошибки и перезапускать анализ."
        )
        messagebox.showinfo("Справка", help_text)

    def generate_data(self):
        """Генерация данных и сброс графика."""
        try:
            self.generator.generate_sequences()
            self.generator.combine_and_sort()
            self.generator.compute_statistics()
            self.generator.create_histogram()
            self.clear_plot()
            self.plot_histogram()
            self.text_area.config(state='normal')
            self.text_area.delete(1.0, tk.END)
            self.text_area.insert(
                tk.END, "Данные успешно сгенерированы и обработаны.\n")
            self.text_area.insert(
                tk.END, "Теперь доступны: просмотр данных, статистика и гистограмма.\n")
            self.text_area.config(state='disabled')
        except Exception as e:
            messagebox.showerror(
                "Ошибка", f"Ошибка при генерации данных: {str(e)}")

    def show_data(self):
        """Отображение объединённого массива."""
        if len(self.generator.combined_data) == 0:
            messagebox.showwarning(
                "Предупреждение", "Сначала сгенерируйте данные.")
            return
        self.text_area.config(state='normal')
        self.text_area.delete(1.0, tk.END)
        self.text_area.insert(
            tk.END, "Объединённый и отсортированный массив (90 чисел):\n\n")
        # Форматируем вывод по 6 чисел в строке
        formatted = [f"{x:8.3f}" for x in self.generator.combined_data]
        for i in range(0, len(formatted), 6):
            line = "  ".join(formatted[i:i+6])
            self.text_area.insert(tk.END, line + "\n")
        self.text_area.config(state='disabled')

    def show_stats(self):
        """Отображение статистики."""
        if len(self.generator.combined_data) == 0:
            messagebox.showwarning(
                "Предупреждение", "Сначала сгенерируйте данные.")
            return
        self.text_area.config(state='normal')
        self.text_area.delete(1.0, tk.END)
        self.text_area.insert(tk.END, "РЕЗУЛЬТАТЫ АНАЛИЗА:\n")
        self.text_area.insert(tk.END, "────────────────────────────────────\n")
        self.text_area.insert(
            tk.END, f"Количество элементов: {len(self.generator.combined_data)}\n")
        self.text_area.insert(
            tk.END, f"Среднее значение:      {self.generator.mean:8.4f}\n")
        self.text_area.insert(
            tk.END, f"Дисперсия:             {self.generator.variance:8.4f}\n")
        self.text_area.insert(
            tk.END, "\nОжидаемые средние: 2, 3, 4 → общее около 3.\n")
        self.text_area.insert(
            tk.END, "Полученное среднее должно быть близко к 3.\n")
        self.text_area.config(state='disabled')

    def plot_histogram(self):
        """Построение гистограммы."""
        if self.generator.hist_data is None:
            messagebox.showwarning(
                "Предупреждение", "Сначала сгенерируйте данные.")
            return

        self.clear_plot()
        self.ax.clear()
        self.ax.bar(self.generator.bin_edges[:-1], self.generator.hist_data,
                    width=np.diff(self.generator.bin_edges), edgecolor="black", alpha=0.7)
        self.ax.set_title(
            "Гистограмма объединённого массива (10 интервалов)", fontsize=12)
        self.ax.set_xlabel("Значение")
        self.ax.set_ylabel("Частота")
        self.ax.grid(True, alpha=0.3)
        self.canvas.draw()

    def clear_plot(self):
        """Очистка графика."""
        self.ax.clear()
        self.canvas.draw()


# ================= #
# Запуск приложения #
# ================= #

if __name__ == "__main__":
    # Проверка наличия необходимых библиотек
    try:
        import numpy as np
        import matplotlib.pyplot as plt
    except ImportError as e:
        messagebox.showerror(
            "Ошибка", f"Не хватает библиотек: {e}. Установите: pip install numpy matplotlib")
    else:
        root = tk.Tk()
        app = App(root)
        root.mainloop()
