import tkinter as tk
from tkinter import ttk, messagebox, filedialog
import math
import random
import csv
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from PIL import Image, ImageTk
import os
from pathlib import Path

BASE_DIR = Path(os.path.dirname(os.path.abspath(__file__)))


def f(x):
    return 1.8 * x**4 - math.sin(10 * x)


def df(x):
    return 7.2 * x**3 - 10 * math.cos(10 * x)


def newton_method_correct(epsilon, a, b, x0=0.22, max_iter=1000):
    if not (a <= x0 <= b):
        raise ValueError(
            f"Начальное приближение {x0} не входит в заданный отрезок: [{a}, {b}]")
    x = x0

    for i in range(max_iter):
        fx = f(x)
        if abs(fx) < epsilon:
            return x, i + 1
        dfx = df(x)
        if abs(dfx) < 1e-14:
            raise ValueError(
                f"Производная близка к нулю при x = {x}. Метод не может продолжаться.")
        x = x - fx / dfx
    raise RuntimeError(f"Метод не сошёлся за {max_iter} итераций.")


def newton_method_incorrect(epsilon, a, b, x0=0.22, max_iter=1000):
    if not (a <= x0 <= b):
        raise ValueError(
            f"Начальное приближение {x0} не входит в заданный отрезок: [{a}, {b}]")
    x = x0

    for i in range(max_iter):
        fx = f(x)
        if fx < epsilon:
            return x, i + 1
        dfx = df(x)
        if abs(dfx) < 1e-14:
            raise ValueError(
                f"Производная близка к нулю при x = {x}. Метод не может продолжаться.")
        x = x - fx / dfx
    raise RuntimeError(f"Метод не сошёлся за {max_iter} итераций.")


def generate_test_epsilons(n):
    base_eps = [1e-1, 1e-2, 1e-3, 1e-4, 1e-5, 1e-6, 1e-8, 1e-10]
    if n <= len(base_eps):
        return base_eps[:n]
    else:
        epsilons = base_eps[:]
        for _ in range(n - len(base_eps)):
            exp = random.uniform(-12, -1)
            epsilons.append(random.choice((-1.0, 1.0)) * 10 ** exp)
        return epsilons[:n]


class NewtonTestApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Лабораторная работа №5")
        self.root.geometry("1000x700")

        self.notebook = ttk.Notebook(root)
        self.notebook.pack(fill='both', expand=True)

        self.tab_test = tk.Frame(self.notebook)
        self.notebook.add(self.tab_test, text="Тестирование")

        self.tab_help = tk.Frame(self.notebook)
        self.notebook.add(self.tab_help, text="Справка")

        self.setup_test_tab()
        self.setup_help_tab()

    def setup_test_tab(self):
        frame_input = tk.Frame(self.tab_test)
        frame_input.pack(pady=10)

        tk.Label(frame_input, text="Количество тестов:").pack(
            side=tk.LEFT, padx=5)
        self.entry_n = tk.Entry(frame_input, width=10)
        self.entry_n.insert(0, "5")
        self.entry_n.pack(side=tk.LEFT, padx=5)

        tk.Button(frame_input, text="Запустить тесты",
                  command=self.run_tests).pack(side=tk.LEFT, padx=10)
        tk.Button(frame_input, text="Сохранить отчёт",
                  command=self.save_report).pack(side=tk.LEFT, padx=10)

        frame_table = tk.Frame(self.tab_test)
        frame_table.pack(fill='both', expand=True, padx=10, pady=10)

        columns = ("№", "(ε, x₀, [a, b])", "Ожидаемое значение",
                   "Фактическое значение", "Результат")
        self.tree = ttk.Treeview(
            frame_table, columns=columns, show='headings', height=20)

        for col in columns:
            self.tree.heading(col, text=col)
            self.tree.column(col, width=150)

        vsb = ttk.Scrollbar(frame_table, orient="vertical",
                            command=self.tree.yview)
        hsb = ttk.Scrollbar(frame_table, orient="horizontal",
                            command=self.tree.xview)
        self.tree.configure(yscrollcommand=vsb.set, xscrollcommand=hsb.set)

        self.tree.grid(row=0, column=0, sticky='nsew')
        vsb.grid(row=0, column=1, sticky='ns')
        hsb.grid(row=1, column=0, sticky='ew')

        frame_table.grid_rowconfigure(0, weight=1)
        frame_table.grid_columnconfigure(0, weight=1)

        self.tree.tag_configure("fail", background="#ffcccc")
        self.tree.tag_configure("pass", background="#ccffcc")

    def setup_help_tab(self):
        help_notebook = ttk.Notebook(self.tab_help)
        help_notebook.pack(fill='both', expand=True, padx=10, pady=10)

        tab_graph = tk.Frame(help_notebook)
        help_notebook.add(tab_graph, text="График функции")

        fig, ax = plt.subplots(figsize=(8, 4))
        x_vals = [i/100 for i in range(0, 2201)]
        y_vals = [f(x) for x in x_vals]
        ax.plot(x_vals, y_vals, label=r'$f(x) = 1.8 \cdot x^4 - \sin(10x)$')
        ax.axhline(y=0, color='k', linestyle='--', linewidth=0.5)
        ax.set_xlabel('x')
        ax.set_ylabel('f(x)')
        ax.set_title('График функции на интервале [0, 22]')
        ax.legend()
        ax.grid(True)

        canvas = FigureCanvasTkAgg(fig, master=tab_graph)
        canvas.draw()
        canvas.get_tk_widget().pack(fill='both', expand=True)

        tab_cause = tk.Frame(help_notebook)
        help_notebook.add(tab_cause, text="Причины и таблицы")

        canvas_cause = tk.Canvas(tab_cause)
        scrollbar_cause = ttk.Scrollbar(
            tab_cause, orient="vertical", command=canvas_cause.yview)
        scrollable_frame_cause = tk.Frame(canvas_cause)

        scrollable_frame_cause.bind(
            "<Configure>",
            lambda e: canvas_cause.configure(
                scrollregion=canvas_cause.bbox("all"))
        )

        canvas_cause.create_window(
            (0, 0), window=scrollable_frame_cause, anchor="nw")
        canvas_cause.configure(yscrollcommand=scrollbar_cause.set)

        canvas_cause.pack(side="left", fill="both", expand=True)
        scrollbar_cause.pack(side="right", fill="y")

        try:
            img1_path = BASE_DIR / "cause_effect_diagram.png"
            img1 = Image.open(img1_path)
            img1 = img1.resize((800, 400), Image.LANCZOS)
            self.img1_tk = ImageTk.PhotoImage(img1)
            label1 = tk.Label(scrollable_frame_cause, image=self.img1_tk)
            label1.pack(pady=5)

            img2_path = BASE_DIR / "decision_table.png"
            img2 = Image.open(img2_path)
            img2 = img2.resize((800, 300), Image.LANCZOS)
            self.img2_tk = ImageTk.PhotoImage(img2)
            label2 = tk.Label(scrollable_frame_cause, image=self.img2_tk)
            label2.pack(pady=5)

        except Exception as e:
            error_label = tk.Label(
                scrollable_frame_cause, text=f"⚠️ Не удалось загрузить изображения:\n{str(e)}\nУбедитесь, что файлы exist.", bg="yellow", justify="left", padx=10, pady=10)
            error_label.pack(pady=10)

        causes_text = """
        ОПИСАНИЕ ПРИЧИН

        1. f(x) = 1.8 * x ^ 4 - sin(10 * x) = 0
           → Уравнение, корень которого ищется.

        2. x₀ ∈ [a, b]
           → Начальное приближение должно лежать в заданном отрезке.

        3. ε > 0
           → Точность должна быть положительной.

        4. f'(x) = 0
           → Критическая ошибка: деление на ноль в методе Ньютона.

        5. |f(x)| < ε
           → Условие завершения: значение функции достаточно близко к нулю.

        """

        tk.Label(scrollable_frame_cause, text=causes_text, justify="left", font=(
            "Courier", 10), padx=10, pady=10).pack(pady=10, fill='x')

        tab_flowchart = tk.Frame(help_notebook)
        help_notebook.add(tab_flowchart, text="Блок-схема")

        canvas_flow = tk.Canvas(tab_flowchart)
        scrollbar_flow = ttk.Scrollbar(
            tab_flowchart, orient="vertical", command=canvas_flow.yview)
        scrollable_frame_flow = tk.Frame(canvas_flow)

        scrollable_frame_flow.bind(
            "<Configure>",
            lambda e: canvas_flow.configure(
                scrollregion=canvas_flow.bbox("all"))
        )

        canvas_flow.create_window(
            (0, 0), window=scrollable_frame_flow, anchor="nw")
        canvas_flow.configure(yscrollcommand=scrollbar_flow.set)

        canvas_flow.pack(side="left", fill="both", expand=True)
        scrollbar_flow.pack(side="right", fill="y")

        try:
            img3_path = BASE_DIR / "flowchart.png"
            img3 = Image.open(img3_path)
            img3 = img3.resize((800, 1000), Image.LANCZOS)
            self.img3_tk = ImageTk.PhotoImage(img3)
            label3 = tk.Label(scrollable_frame_flow, image=self.img3_tk)
            label3.pack(pady=10)
        except Exception as e:
            tk.Label(scrollable_frame_flow,
                     text=f"⚠️ Не удалось загрузить блок-схему:\n{str(e)}", bg="yellow", justify="left", padx=10, pady=10).pack(pady=10)

    def run_tests(self):
        try:
            n = int(self.entry_n.get())
            if n <= 0:
                raise ValueError
        except ValueError:
            messagebox.showerror(
                "Ошибка", "Введите корректное количество тестов (целое > 0)")
            return

        for item in self.tree.get_children():
            self.tree.delete(item)

        epsilons = generate_test_epsilons(n)
        self.test_results = []

        for i, eps in enumerate(epsilons, 1):
            status, tag = "", ""
            x0 = random.random()
            a = random.choice((-1, 1)) * random.random() * 2
            b = a + random.random() * 3

            try:
                expected_val, _ = newton_method_correct(eps, a, b, x0)
            except Exception as e:
                expected_val = f"{e}"

            try:
                actual_val, _ = newton_method_incorrect(eps, a, b, x0)
            except Exception as e:
                actual_val = f"{e}"

            if isinstance(actual_val, str) and isinstance(expected_val, str):
                status = "УСПЕШНО" if expected_val != actual_val else "НЕУСПЕШНО"
                tag = "pass" if status == "УСПЕШНО" else "fail"
            elif isinstance(actual_val, float) and isinstance(expected_val, float):
                status = "УСПЕШНО" if abs(
                    expected_val - actual_val) >= 1e-8 else "НЕУСПЕШНО"
                tag = "pass" if status == "УСПЕШНО" else "fail"
            else:
                status = "УСПЕШНО"
                tag = "pass"

            input_str = f"({eps:.1e}, {x0}, [{a}, {b}])"
            expected_str = f"{expected_val:.10f}" if isinstance(
                expected_val, float) else str(expected_val)
            actual_str = f"{actual_val:.10f}" if isinstance(
                actual_val, float) else str(actual_val)

            self.tree.insert("", "end", values=(
                i, input_str, expected_str, actual_str, status), tags=(tag,))

            self.test_results.append({
                '№': i,
                '(ε, x₀, [a, b])': input_str,
                'Ожидаемое значение': expected_str,
                'Фактическое значение': actual_str,
                'Результат': status
            })

    def save_report(self):
        if not hasattr(self, 'test_results') or len(self.test_results) == 0:
            messagebox.showwarning("Нет данных", "Сначала запустите тесты!")
            return

        filename = filedialog.asksaveasfilename(
            defaultextension=".csv",
            filetypes=[("CSV files", "*.csv"), ("All files", "*.*")],
            title="Сохранить отчёт тестирования"
        )
        if not filename:
            return

        try:
            with open(filename, mode='w', newline='', encoding='utf-8') as f:
                writer = csv.DictWriter(
                    f, fieldnames=self.test_results[0].keys())
                writer.writeheader()
                writer.writerows(self.test_results)
            messagebox.showinfo("Успех", f"Отчёт сохранён в:\n{filename}")
        except Exception as e:
            messagebox.showerror(
                "Ошибка", f"Не удалось сохранить отчёт:\n{str(e)}")


if __name__ == "__main__":
    root = tk.Tk()
    app = NewtonTestApp(root)
    root.mainloop()
