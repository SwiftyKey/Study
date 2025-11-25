import tkinter as tk
from tkinter import ttk, messagebox, filedialog
import random
import csv
import os
from pathlib import Path

from PIL import Image, ImageTk

from module1 import max_elem_correct, max_elem_incorrect, dummy as dummy1
from module2 import sum_between_positives_correct, sum_between_positives_incorrect, dummy as dummy2
from module3 import zeros_to_end_correct, zeros_to_end_incorrect, dummy as dummy3

BASE_DIR = Path(os.path.dirname(os.path.abspath(__file__)))

class ArrayTestApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Лабораторная работа №6")
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

        tk.Label(frame_input, text="Количество тестов:").grid(
            row=0, column=0, padx=5, sticky='e')
        self.entry_n_tests = tk.Entry(frame_input, width=10)
        self.entry_n_tests.insert(0, "3")
        self.entry_n_tests.grid(row=0, column=1, padx=5)

        tk.Label(frame_input, text="Размер массива:").grid(
            row=0, column=2, padx=5, sticky='e')
        self.entry_n = tk.Entry(frame_input, width=10)
        self.entry_n.insert(0, "5")
        self.entry_n.grid(row=0, column=3, padx=5)

        frame_modules = tk.Frame(self.tab_test)
        frame_modules.pack(pady=5)

        self.var_mod1 = tk.BooleanVar()
        self.var_mod2 = tk.BooleanVar()
        self.var_mod3 = tk.BooleanVar()

        tk.Checkbutton(frame_modules, text="Модуль 1: Максимум по модулю",
                       variable=self.var_mod1).pack(side=tk.LEFT, padx=10)
        tk.Checkbutton(frame_modules, text="Модуль 2: Сумма между первыми двумя положительными",
                       variable=self.var_mod2).pack(side=tk.LEFT, padx=10)
        tk.Checkbutton(frame_modules, text="Модуль 3: Нули в конец",
                       variable=self.var_mod3).pack(side=tk.LEFT, padx=10)

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
        except ValueError:
            messagebox.showerror(
                "Ошибка", "Количество тестов и размер массива должны быть целыми > 0")
            return

        selected = [self.var_mod1.get(), self.var_mod2.get(),
                    self.var_mod3.get()]
        if not any(selected):
            messagebox.showwarning(
                "Внимание", "Выберите хотя бы один модуль для тестирования!")
            return

        for item in self.tree.get_children():
            self.tree.delete(item)

        self.test_results = []

        for test_id in range(1, n_tests + 1):
            arr = [round(random.uniform(-10, 10), 2) for _ in range(n)]

            actual = [None, None, None]
            if selected[0]:
                try:
                    actual[0] = max_elem_correct(arr)
                except Exception as e:
                    actual[0] = f"Ошибка: {e}"
            else:
                actual[0] = dummy1(arr)

            if selected[1]:
                try:
                    actual[1] = sum_between_positives_correct(arr)
                except Exception as e:
                    actual[1] = f"Ошибка: {e}"
            else:
                actual[1] = dummy2(arr)

            if selected[2]:
                try:
                    actual[2] = zeros_to_end_correct(arr)
                except Exception as e:
                    actual[2] = f"Ошибка: {e}"
            else:
                actual[2] = dummy3(arr)

            expected = [None, None, None]
            if selected[0]:
                try:
                    expected[0] = max_elem_incorrect(arr)
                except Exception as e:
                    expected[0] = f"Ошибка: {e}"
            else:
                expected[0] = dummy1(arr)

            if selected[1]:
                try:
                    expected[1] = sum_between_positives_incorrect(arr)
                except Exception as e:
                    expected[1] = f"Ошибка: {e}"
            else:
                expected[1] = dummy2(arr)

            if selected[2]:
                try:
                    expected[2] = zeros_to_end_incorrect(arr)
                except Exception as e:
                    expected[2] = f"Ошибка: {e}"
            else:
                expected[2] = dummy3(arr)

            actual_tuple = tuple(
                val for i, val in enumerate(actual) if selected[i])
            expected_tuple = tuple(
                val for i, val in enumerate(expected) if selected[i])

            if actual_tuple != expected_tuple:
                status = "УСПЕШНО"
                tag = "success"
            else:
                status = "НЕУСПЕШНО"
                tag = "fail"

            arr_str = "[" + ", ".join(f"{x:.2f}" for x in arr) + "]"
            actual_str = str(actual_tuple)
            expected_str = str(expected_tuple)

            self.tree.insert("", "end", values=(
                test_id, arr_str, actual_str, expected_str, status), tags=(tag,))

            self.test_results.append({
                '№': test_id,
                'Массив': arr_str,
                'Фактический результат': actual_str,
                'Ожидаемый результат': expected_str,
                'Результат теста': status
            })

    def save_report(self):
        if not hasattr(self, 'test_results') or len(self.test_results) == 0:
            messagebox.showwarning("Нет данных", "Сначала запустите тесты!")
            return

        filename = filedialog.asksaveasfilename(
            defaultextension=".csv",
            filetypes=[("CSV files", "*.csv")],
            title="Сохранить отчёт"
        )
        if not filename:
            return

        try:
            with open(filename, mode='w', newline='', encoding='utf-8') as f:
                writer = csv.DictWriter(
                    f, fieldnames=self.test_results[0].keys())
                writer.writeheader()
                writer.writerows(self.test_results)
            messagebox.showinfo("Успех", f"Отчёт сохранён:\n{filename}")
        except Exception as e:
            messagebox.showerror("Ошибка", f"Не удалось сохранить:\n{str(e)}")


if __name__ == "__main__":
    root = tk.Tk()
    app = ArrayTestApp(root)
    root.mainloop()
