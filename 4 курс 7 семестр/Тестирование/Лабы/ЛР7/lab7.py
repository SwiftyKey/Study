import tkinter as tk
import random
import csv
import os

from module1 import sum_negatives_correct, sum_negatives_incorrect
from module2 import prod_between_minmax_correct, prod_between_minmax_incorrect
from module3 import arr_sort_correct, arr_sort_incorrect
from main_processor import cluster_driver, terminal_driver
from pathlib import Path
from PIL import Image, ImageTk
from tkinter import ttk, messagebox, filedialog

BASE_DIR = Path(os.path.dirname(os.path.abspath(__file__)))

class AscendingTestApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Лабоработрная работа №7")
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

        tk.Label(frame_input, text="Количество групп тестов:").grid(
            row=0, column=0, padx=5, sticky='e')
        self.entry_n_tests = tk.Entry(frame_input, width=10)
        self.entry_n_tests.insert(0, "3")
        self.entry_n_tests.grid(row=0, column=1, padx=5)

        tk.Label(frame_input, text="Размер массива:").grid(
            row=0, column=2, padx=5, sticky='e')
        self.entry_n = tk.Entry(frame_input, width=10)
        self.entry_n.insert(0, "5")
        self.entry_n.grid(row=0, column=3, padx=5)

        self.test_type = tk.StringVar(value="terminal")
        tk.Radiobutton(self.tab_test, text="Терминальные модули",
                       variable=self.test_type, value="terminal").pack()
        tk.Radiobutton(self.tab_test, text="Кластер",
                       variable=self.test_type, value="cluster").pack()

        frame_btn = tk.Frame(self.tab_test)
        frame_btn.pack(pady=5)
        tk.Button(frame_btn, text="Запустить тесты",
                  command=self.run_tests).pack(side=tk.LEFT, padx=10)
        tk.Button(frame_btn, text="Сохранить отчёт",
                  command=self.save_report).pack(side=tk.LEFT, padx=10)

        frame_table = tk.Frame(self.tab_test)
        frame_table.pack(fill='both', expand=True, padx=10, pady=10)

        columns = ("№", "Массив", "Фактический результат",
                   "Ожидаемый результат", "Результат теста")
        self.tree = ttk.Treeview(
            frame_table, columns=columns, show='headings', height=15)

        for col in columns:
            self.tree.heading(col, text=col)
            self.tree.column(col, width=180)

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

        self.tree.tag_configure(
            "success", background="#ccffcc")
        self.tree.tag_configure("fail", background="#ffcccc")

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
        except Exception as e:
            tk.Label(
                scrollable_flow, text=f"⚠️ Не удалось загрузить блок-схемы:\n{e}", bg="yellow", padx=10, pady=10).pack()

        tab_struct = tk.Frame(help_notebook)
        help_notebook.add(tab_struct, text="Структурная схема")

        canvas_struct = tk.Canvas(tab_struct)
        scrollbar_struct = ttk.Scrollbar(
            tab_struct, orient="vertical", command=canvas_struct.yview)
        scrollable_struct = tk.Frame(canvas_struct)

        scrollable_struct.bind("<Configure>", lambda e: canvas_struct.configure(
            scrollregion=canvas_struct.bbox("all")))
        canvas_struct.create_window(
            (0, 0), window=scrollable_struct, anchor="nw")
        canvas_struct.configure(yscrollcommand=scrollbar_struct.set)

        canvas_struct.pack(side="left", fill="both", expand=True)
        scrollbar_struct.pack(side="right", fill="y")

        try:
            img3 = Image.open(BASE_DIR / "structure_diagram.png")
            img3 = img3.resize((900, 500), Image.LANCZOS)
            self.img3_tk = ImageTk.PhotoImage(img3)
            tk.Label(scrollable_struct, image=self.img3_tk).pack(pady=10)
        except Exception as e:
            tk.Label(scrollable_struct,
                     text=f"⚠️ Не удалось загрузить структурную схему:\n{e}", bg="yellow", padx=10, pady=10).pack()

    def run_tests(self):
        try:
            n_tests = int(self.entry_n_tests.get())
            n = int(self.entry_n.get())
            if n_tests <= 0 or n <= 0:
                raise ValueError
        except:
            messagebox.showerror("Ошибка", "Введите корректные числа > 0")
            return

        test_mode = self.test_type.get()
        self.test_results, funcs = [], (
            (sum_negatives_correct, sum_negatives_incorrect),
            (prod_between_minmax_correct, prod_between_minmax_incorrect),
            (arr_sort_correct, arr_sort_incorrect)
        )

        for item in self.tree.get_children():
            self.tree.delete(item)

        for tid in range(1, n_tests + 1):
            arr, results = [round(random.uniform(-10, 10), 2) for _ in range(n)], []

            if test_mode == "terminal":
                results = terminal_driver(arr, funcs)
            else:
                results = cluster_driver(arr, funcs)
                print(results)

            for tres in results:
                actual, expected = 0, 0
                if isinstance(tres[0], tuple):
                    actual, expected = [r[0] for r in tres], [r[1] for r in tres]
                else:
                    actual, expected = tres

                arr_str = "[" + ", ".join(f"{x:.2f}" for x in arr) + "]"
                actual_str = str(actual)
                expected_str = str(expected)

                if actual != expected:
                    status = "УСПЕШНО"
                    tag = "success"
                else:
                    status = "НЕУСПЕШНО"
                    tag = "fail"

                self.tree.insert("", "end", values=(
                    tid, arr_str, actual_str, expected_str, status), tags=(tag,))
                self.test_results.append({
                    '№': tid,
                    'Массив': arr_str,
                    'Фактический результат': actual_str,
                    'Ожидаемый результат': expected_str,
                    'Результат теста': status
                })

    def save_report(self):
        if not self.test_results:
            messagebox.showwarning("Нет данных", "Запустите тесты!")
            return
        filename = filedialog.asksaveasfilename(
            defaultextension=".csv", filetypes=[("CSV", "*.csv")])
        if not filename:
            return
        with open(filename, 'w', newline='', encoding='utf-8') as f:
            writer = csv.DictWriter(f, fieldnames=self.test_results[0].keys())
            writer.writeheader()
            writer.writerows(self.test_results)
        messagebox.showinfo("Успех", f"Отчёт сохранён:\n{filename}")


if __name__ == "__main__":
    root = tk.Tk()
    app = AscendingTestApp(root)
    root.mainloop()
