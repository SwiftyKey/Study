import tkinter as tk
import random
import csv
import os

from tkinter import ttk, messagebox, filedialog
from PIL import Image, ImageTk
from pathlib import Path

from mfuncs import fcorr, fincorr
from setup import get_base_test_cases

BASE_DIR = Path(os.path.dirname(os.path.abspath(__file__)))


class App:
    def __init__(self, root):
        self.root = root
        self.root.title("Контрольная работа")
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

        columns = ("№", "(a,b,c,x)", "Ожидаемое значение", "Фактическое значение", "Результат")
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

        tab_control_graph = tk.Frame(help_notebook)
        help_notebook.add(tab_control_graph, text="Потоковый граф")

        canvas_control_graph = tk.Canvas(tab_control_graph)
        scrollbar_control_graph = ttk.Scrollbar(tab_control_graph, orient="vertical", command=canvas_control_graph.yview)
        scrollable_frame_control_graph = tk.Frame(canvas_control_graph)

        scrollable_frame_control_graph.bind(
            "<Configure>",
            lambda e: canvas_control_graph.configure(
                scrollregion=canvas_control_graph.bbox("all"))
        )

        canvas_control_graph.create_window(
            (0, 0), window=scrollable_frame_control_graph, anchor="nw")
        canvas_control_graph.configure(yscrollcommand=scrollbar_control_graph.set)

        canvas_control_graph.pack(side="left", fill="both", expand=True)
        scrollbar_control_graph.pack(side="right", fill="y")

        help_text = (
            "Метод базового пути:\n"
            "- E=10, N=8\n"
            "- Предикатных узлов p = 3\n"
            "\t - Предикатные узла: x < 0, b != 0, c != 0\n"
            "- Цикломатическая сложность V(G) = 4\n"
            "- Требуется 4 независимых путей\n"
        )

        ttk.Label(scrollable_frame_control_graph, text=help_text, justify=tk.LEFT).pack(anchor=tk.W, padx=10, pady=5)

        try:
            tk.Label(scrollable_frame_control_graph, text='Управляющий потоковый граф', justify="left", font=("Courier", 10), padx=10, pady=10).pack(pady=10, fill='x')

            img_path = BASE_DIR / "control_graph.png"
            img = Image.open(img_path)
            img = img.resize((800, 400), Image.LANCZOS)
            self.img1_tk = ImageTk.PhotoImage(img)
            label1 = tk.Label(scrollable_frame_control_graph, image=self.img1_tk)
            label1.pack(pady=5)
        except Exception as e:
            error_label = tk.Label(scrollable_frame_control_graph, text=f"⚠️ Не удалось загрузить изображения:\n{str(e)}\nУбедитесь, что файлы exist.", bg="yellow", justify="left", padx=10, pady=10)
            error_label.pack(pady=10)

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
            img_path = BASE_DIR / "flowchart.png"
            img = Image.open(img_path)
            img = img.resize((1200, 600), Image.LANCZOS)
            self.img2_tk = ImageTk.PhotoImage(img)
            label3 = tk.Label(scrollable_frame_flow, image=self.img2_tk)
            label3.pack(pady=10)
        except Exception as e:
            tk.Label(scrollable_frame_flow,
                     text=f"⚠️ Не удалось загрузить блок-схему:\n{str(e)}", bg="yellow", justify="left", padx=10, pady=10).pack(pady=10)

    def run_tests(self):
        n = int(self.entry_n.get())
        if n < 0:
            messagebox.showerror("Ошибка", "Количество тестов должно быть неотрицательным числом!")
            return

        for item in self.tree.get_children():
            self.tree.delete(item)

        base_tests = get_base_test_cases()
        tests = [data for data, _ in base_tests] + [[round(random.uniform(-10, 10), 2) for _ in range(4)] for _ in range(n)]

        self.test_results = []

        for i, data in enumerate(tests, 1):
            status, tag = "", ""
            try:
                expected = round(fcorr(*data), 2)
            except ZeroDivisionError as e:
                expected = f"{e}"

            try:
                actual = round(fincorr(*data), 2)
            except ZeroDivisionError as e:
                actual = f"{e}"

            if isinstance(actual, str) and isinstance(expected, str):
                status = "УСПЕШНО" if actual != expected else "НЕУСПЕШНО"
                tag = "pass" if status == "УСПЕШНО" else "fail"
            elif isinstance(actual, float) and isinstance(expected, float):
                status = "УСПЕШНО" if abs(actual - expected) >= 1e-8 else "НЕУСПЕШНО"
                tag = "pass" if status == "УСПЕШНО" else "fail"
            else:
                status = "УСПЕШНО"
                tag = "pass"

            self.tree.insert("", "end", values=(i, str(data), expected, actual, status), tags=(tag,))

            self.test_results.append({
                '№': i,
                '(a,b,c,x)': str(data),
                'Ожидаемое значение': expected,
                'Фактическое значение': actual,
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
    app = App(root)
    root.mainloop()
