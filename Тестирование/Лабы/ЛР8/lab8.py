import tkinter as tk
from tkinter import ttk, messagebox, scrolledtext
import random
import os
from PIL import Image, ImageTk
from pathlib import Path

from module1 import count_zeros
from module2 import min_max_odd_in_columns
from module3 import sum_above_anti_diagonal
from module4 import sort_above_anti_diagonal_insertion


BASE_DIR = Path(os.path.dirname(os.path.abspath(__file__)))

class MatrixApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Лабораторная работа №8")
        self.root.geometry("900x700")

        self.notebook = ttk.Notebook(root)
        self.notebook.pack(fill='both', expand=True)

        self.tab_main = tk.Frame(self.notebook)
        self.notebook.add(self.tab_main, text="Расчёт")

        self.tab_help = tk.Frame(self.notebook)
        self.notebook.add(self.tab_help, text="Справка")

        self.setup_main_tab()
        self.setup_help_tab()

    def setup_main_tab(self):
        frame_input = tk.Frame(self.tab_main)
        frame_input.pack(pady=10)

        tk.Label(frame_input, text="N (строки):").grid(row=0, column=0, padx=5, sticky='e')
        self.entry_n = tk.Entry(frame_input, width=10)
        self.entry_n.insert(0, "4")
        self.entry_n.grid(row=0, column=1, padx=5)

        tk.Label(frame_input, text="M (столбцы):").grid(row=0, column=2, padx=5, sticky='e')
        self.entry_m = tk.Entry(frame_input, width=10)
        self.entry_m.insert(0, "4")
        self.entry_m.grid(row=0, column=3, padx=5)

        tk.Button(frame_input, text="Сгенерировать матрицу и рассчитать", command=self.calculate).grid(row=0, column=4, padx=10)

        tk.Label(self.tab_main, text="Исходная матрица:", font=("Arial", 10, "bold")).pack(anchor='w', padx=10)
        self.text_matrix = scrolledtext.ScrolledText(self.tab_main, height=10, width=80, font=("Courier", 10))
        self.text_matrix.pack(padx=10, pady=5)

        tk.Label(self.tab_main, text="Результаты:", font=("Arial", 10, "bold")).pack(anchor='w', padx=10)
        self.text_results = scrolledtext.ScrolledText(self.tab_main, height=20, width=80, font=("Courier", 10))
        self.text_results.pack(padx=10, pady=5)

    def setup_help_tab(self):
        help_notebook = ttk.Notebook(self.tab_help)
        help_notebook.pack(fill='both', expand=True, padx=10, pady=10)

        tab_flow = tk.Frame(help_notebook)
        help_notebook.add(tab_flow, text="Блок-схемы")

        canvas_flow = tk.Canvas(tab_flow)
        scrollbar_flow = ttk.Scrollbar(
            tab_flow, orient="vertical", command=canvas_flow.yview)
        scrollable_flow = tk.Frame(canvas_flow)

        scrollable_flow.bind("<Configure>", lambda e: canvas_flow.configure(
            scrollregion=canvas_flow.bbox("all")))
        canvas_flow.create_window((0, 0), window=scrollable_flow, anchor="nw")
        canvas_flow.configure(yscrollcommand=scrollbar_flow.set)

        canvas_flow.pack(side="left", fill="both", expand=True)
        scrollbar_flow.pack(side="right", fill="y")

        try:
            tk.Label(scrollable_flow, text='Блок схема главного модуля:', justify="left", font=("Courier", 10), padx=10, pady=10).pack(pady=10, fill='x')

            img_module_main = Image.open(BASE_DIR / "module_main_flowchart.png")
            img_module_main = img_module_main.resize((800, 400), Image.LANCZOS)
            self.img_module_main_tk = ImageTk.PhotoImage(img_module_main)
            tk.Label(scrollable_flow, image=self.img_module_main_tk).pack(pady=5)

            tk.Label(scrollable_flow, text='Блок схема модуля 1:', justify="left", font=("Courier", 10), padx=10, pady=10).pack(pady=10, fill='x')

            img_module_1 = Image.open(BASE_DIR / "module_1_flowchart.png")
            img_module_1 = img_module_1.resize((800, 400), Image.LANCZOS)
            self.img_module_1_tk = ImageTk.PhotoImage(img_module_1)
            tk.Label(scrollable_flow, image=self.img_module_1_tk).pack(pady=5)

            tk.Label(scrollable_flow, text='Блок схема модуля 2:', justify="left", font=("Courier", 10), padx=10, pady=10).pack(pady=10, fill='x')

            img_module_2 = Image.open(BASE_DIR / "module_2_flowchart.png")
            img_module_2 = img_module_2.resize((800, 400), Image.LANCZOS)
            self.img_module_2_tk = ImageTk.PhotoImage(img_module_2)
            tk.Label(scrollable_flow, image=self.img_module_2_tk).pack(pady=5)

            tk.Label(scrollable_flow, text='Блок схема модуля 3:', justify="left", font=("Courier", 10), padx=10, pady=10).pack(pady=10, fill='x')

            img_module_3 = Image.open(BASE_DIR / "module_3_flowchart.png")
            img_module_3 = img_module_3.resize((800, 400), Image.LANCZOS)
            self.img_module_3_tk = ImageTk.PhotoImage(img_module_3)
            tk.Label(scrollable_flow, image=self.img_module_3_tk).pack(pady=5)

            tk.Label(scrollable_flow, text='Блок схема модуля 4:', justify="left", font=("Courier", 10), padx=10, pady=10).pack(pady=10, fill='x')

            img_module_4 = Image.open(BASE_DIR / "module_4_flowchart.png")
            img_module_4 = img_module_4.resize((800, 400), Image.LANCZOS)
            self.img_module_4_tk = ImageTk.PhotoImage(img_module_4)
            tk.Label(scrollable_flow, image=self.img_module_4_tk).pack(pady=5)
        except Exception as e:
            tk.Label(
                scrollable_flow, text=f"⚠️ Не удалось загрузить блок-схемы:\n{e}", bg="yellow", padx=10, pady=10).pack()

    def calculate(self):
        try:
            n = int(self.entry_n.get())
            m = int(self.entry_m.get())
            if n <= 0 or m <= 0:
                raise ValueError
        except ValueError:
            messagebox.showerror("Ошибка", "n и m должны быть целыми > 0")
            return

        matrix = [[random.randint(-10, 10) for _ in range(m)] for _ in range(n)]

        self.text_matrix.delete(1.0, tk.END)
        for row in matrix:
            self.text_matrix.insert(tk.END, " ".join(f"{x:3}" for x in row) + "\n")

        results = []

        zeros = count_zeros(matrix)
        results.append(f"1) Количество нулевых элементов: {zeros}")

        min_elems, max_elems = min_max_odd_in_columns(matrix, n, m)
        results.append("2) Минимальные и максимальные нечентные элементы столбцов:")
        if not min_elems:
            results.append("2) Нечётных элементов нет в матрице")
        else:
            for i in range(m):
                results.append(f"\tСтолбец: {i + 1} Мин. нечётный: {min_elems[i]}, Макс. нечётный: {max_elems[i]}")

        if n == m:
            try:
                total = sum_above_anti_diagonal(matrix, n)
                results.append(f"3) Сумма выше побочной диагонали: {total}")

                sorted_matrix = sort_above_anti_diagonal_insertion(matrix, n)
                results.append("4) Матрица после сортировки выше побочной диагонали:")
                for row in sorted_matrix:
                    results.append(" ".join(f"{x:3}" for x in row))
            except Exception as e:
                results.append(f"3/4) Ошибка: {e}")
        else:
            results.append("3 и 4 пропущены: матрица не квадратная (n != m)")

        self.text_results.delete(1.0, tk.END)
        self.text_results.insert(tk.END, "\n".join(results))

if __name__ == "__main__":
    root = tk.Tk()
    app = MatrixApp(root)
    root.mainloop()
