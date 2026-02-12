import tkinter as tk
from tkinter import ttk, messagebox, filedialog
import random
import networkx as nx
from matplotlib.figure import Figure
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import csv

# ----------------------------
# Логика алгоритма
# ----------------------------


def sum_before_last_positive(arr):
    n = len(arr)
    last_positive_index = -1

    for i in range(n):
        if arr[i] > 0:
            last_positive_index = i

    if last_positive_index == -1:
        return 0

    total = 0
    for i in range(last_positive_index):
        total += arr[i]

    return total

def sum_before_last_positive_buggy(arr):
    n = len(arr)
    last_positive_index = 1

    for i in range(n):
        if arr[i] > 0:
            last_positive_index = i

    if last_positive_index == -1:
        return 0

    total = 0
    for i in range(last_positive_index):
        total += arr[i]

    return total

# ----------------------------
# Базовые тесты с ожидаемыми результатами
# ----------------------------


def get_base_test_cases():
    return [
        ([-1, -2, -3], 0, "Путь A: нет положительных"),
        ([5, -1, -2], 0, "Путь B: первый элемент положительный"),
        ([-1, 3, -2], -1, "Путь C: положительный в середине"),
        ([1, -2, 4, -1, 2, -3], 2, "Путь D: несколько положительных"),
        ([-1, 2, 3], 1, "Путь E: последний элемент положительный")
    ]

# ----------------------------
# Построение графа УПГ
# ----------------------------


def draw_flow_graph(parent_frame):
    G = nx.DiGraph()

    nodes = [
        "1: Start",
        "2: init last=-1",
        "3: i=0",
        "4: i < n?",
        "5: arr[i] > 0?",
        "6: last=i",
        "7: i++",
        "8: last == -1?",
        "9: return 0",
        "10: total=0, i=0",
        "11: i < last?",
        "12: total += arr[i]",
        "13: i++",
        "14: return total",
        "15: End"
    ]

    for node in nodes:
        G.add_node(node)

    edges = [
        ("1: Start", "2: init last=-1"),
        ("2: init last=-1", "3: i=0"),
        ("3: i=0", "4: i < n?"),
        ("4: i < n?", "5: arr[i] > 0?"),
        ("5: arr[i] > 0?", "6: last=i"),
        ("6: last=i", "7: i++"),
        ("5: arr[i] > 0?", "7: i++"),
        ("7: i++", "4: i < n?"),
        ("4: i < n?", "8: last == -1?"),
        ("8: last == -1?", "9: return 0"),
        ("9: return 0", "15: End"),
        ("8: last == -1?", "10: total=0, i=0"),
        ("10: total=0, i=0", "11: i < last?"),
        ("11: i < last?", "12: total += arr[i]"),
        ("12: total += arr[i]", "13: i++"),
        ("13: i++", "11: i < last?"),
        ("11: i < last?", "14: return total"),
        ("14: return total", "15: End")
    ]

    G.add_edges_from(edges)

    fig = Figure(figsize=(8, 6), dpi=100)
    ax = fig.add_subplot(111)
    pos = nx.spring_layout(G, seed=42)
    nx.draw(G, pos, ax=ax, with_labels=True, node_size=2000, node_color="lightblue",
            font_size=8, font_weight="bold", arrows=True)
    canvas = FigureCanvasTkAgg(fig, parent_frame)
    canvas.draw()
    canvas.get_tk_widget().pack(fill=tk.BOTH, expand=True)

# ----------------------------
# Основное приложение
# ----------------------------


class App:
    def __init__(self, root):
        self.root = root
        self.root.title("Тестирование методом базового пути")
        self.root.geometry("1000x700")

        # Ввод
        input_frame = ttk.Frame(root, padding="10")
        input_frame.pack(fill=tk.X)

        ttk.Label(input_frame, text="Количество элементов в массиве:").grid(
            row=0, column=0, sticky=tk.W)
        self.n_var = tk.IntVar(value=5)
        ttk.Entry(input_frame, textvariable=self.n_var,
                  width=10).grid(row=0, column=1, padx=5)

        ttk.Label(input_frame, text="Количество тестов:").grid(
            row=1, column=0, sticky=tk.W)
        self.tests_var = tk.IntVar(value=3)
        ttk.Entry(input_frame, textvariable=self.tests_var,
                  width=10).grid(row=1, column=1, padx=5)

        button_frame = ttk.Frame(input_frame)
        button_frame.grid(row=2, column=0, columnspan=2, pady=10)
        ttk.Button(button_frame, text="Запустить тесты",
                   command=self.run_tests).pack(side=tk.LEFT, padx=5)
        ttk.Button(button_frame, text="Сохранить в CSV",
                   command=self.save_to_csv).pack(side=tk.LEFT, padx=5)

        # Вкладки
        notebook = ttk.Notebook(root)
        notebook.pack(fill=tk.BOTH, expand=True, padx=10, pady=5)

        self.results_frame = ttk.Frame(notebook)
        self.help_frame = ttk.Frame(notebook)

        notebook.add(self.results_frame, text="Результаты")
        notebook.add(self.help_frame, text="Справка")

        # Таблица результатов
        self.tree = ttk.Treeview(self.results_frame, columns=(
            "№", "Массив", "Ожидаемый", "Фактический", "Результат"), show="headings")
        self.tree.heading("№", text="№")
        self.tree.heading("Массив", text="Массив")
        self.tree.heading("Ожидаемый", text="Ожидаемый")
        self.tree.heading("Фактический", text="Фактический")
        self.tree.heading("Результат", text="Результат")

        self.tree.column("№", width=40, anchor="center")
        self.tree.column("Массив", width=250)
        self.tree.column("Ожидаемый", width=100, anchor="center")
        self.tree.column("Фактический", width=100, anchor="center")
        self.tree.column("Результат", width=100, anchor="center")

        vsb = ttk.Scrollbar(self.results_frame,
                            orient="vertical", command=self.tree.yview)
        hsb = ttk.Scrollbar(self.results_frame,
                            orient="horizontal", command=self.tree.xview)
        self.tree.configure(yscrollcommand=vsb.set, xscrollcommand=hsb.set)

        self.tree.grid(row=0, column=0, sticky="nsew")
        vsb.grid(row=0, column=1, sticky="ns")
        hsb.grid(row=1, column=0, sticky="ew")

        self.results_frame.grid_rowconfigure(0, weight=1)
        self.results_frame.grid_columnconfigure(0, weight=1)

        # Справка
        help_text = (
            "Метод базового пути:\n"
            "- E=18, N=15\n"
            "- Предикатных узлов p = 4\n"
            "\t - Предикатные узла: i < n, arr[i] > 0, last_positive_index == -1, i < last_positive_index\n"
            "- Цикломатическая сложность V(G) = 5\n"
            "- Требуется 5 независимых путей\n"
            "- Управляющий потоковый граф программы:\n\n"
        )
        ttk.Label(self.help_frame, text=help_text, justify=tk.LEFT).pack(
            anchor=tk.W, padx=10, pady=5)
        draw_flow_graph(self.help_frame)

    def run_tests(self):
        try:
            n = self.n_var.get()
            num_tests = self.tests_var.get()
            if n <= 0 or num_tests < 0:
                raise ValueError

            # Очистка таблицы
            for item in self.tree.get_children():
                self.tree.delete(item)

            base_tests = get_base_test_cases()
            test_id = 1

            # Базовые тесты (метод базового пути)
            for arr, expected, _ in base_tests:
                actual = sum_before_last_positive(arr)
                buggy = sum_before_last_positive_buggy(arr)
                status = "Успешно" if actual == buggy else "Ошибка"
                self.tree.insert("", "end", values=(
                    test_id, str(arr), expected, actual, status))
                test_id += 1

            # Случайные тесты
            for _ in range(num_tests):
                arr = [random.randint(-5, 5) for _ in range(n)]
                actual = sum_before_last_positive(arr)
                buggy = sum_before_last_positive_buggy(arr)

                status = "Успешно" if actual == buggy else "Ошибка"
                self.tree.insert("", "end", values=(
                    test_id, str(arr), expected, actual, status))
                test_id += 1

        except Exception as e:
            messagebox.showerror(
                "Ошибка", "Введите корректные положительные числа!")

    def save_to_csv(self):
        # Получаем все строки из Treeview
        items = self.tree.get_children()
        if not items:
            messagebox.showwarning(
                "Предупреждение", "Нет данных для сохранения!")
            return

        # Диалог сохранения
        filepath = filedialog.asksaveasfilename(
            defaultextension=".csv",
            filetypes=[("CSV files", "*.csv"), ("All files", "*.*")],
            title="Сохранить результаты тестирования"
        )
        if not filepath:
            return  # Отмена

        try:
            with open(filepath, mode='w', newline='', encoding='utf-8') as file:
                writer = csv.writer(file)
                # Заголовки
                writer.writerow(
                    ["№", "Массив", "Ожидаемый результат", "Фактический результат", "Результат"])
                # Данные
                for item in items:
                    values = self.tree.item(item, 'values')
                    writer.writerow(values)
            messagebox.showinfo(
                "Успех", f"Результаты сохранены в:\n{filepath}")
        except Exception as e:
            messagebox.showerror(
                "Ошибка", f"Не удалось сохранить файл:\n{str(e)}")


# ----------------------------
# Запуск
# ----------------------------
if __name__ == "__main__":
    root = tk.Tk()
    app = App(root)
    root.mainloop()
