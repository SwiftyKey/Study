import tkinter as tk
from tkinter import ttk, messagebox, filedialog
from PIL import Image, ImageTk
import random
import csv
import os
from pathlib import Path

BASE_DIR = Path(os.path.dirname(os.path.abspath(__file__)))

# ----------------------------
# Алгоритмы
# ----------------------------

def correct_algorithm(arr, C):
    indices = []
    count = 0
    for i, val in enumerate(arr):
        if val < C:
            indices.append(i)
            count += 1
    return count, indices


def buggy_algorithm(arr, C):
    indices = []
    count = 0
    for i in range(1, len(arr)):
        if arr[i] < C:
            indices.append(i)
            count += 1
    return count, indices

# ----------------------------
# Генерация тестов по классам эквивалентности
# ----------------------------

def generate_representative_tests(n, C):
    tests = []

    if n == 0:
        tests.append(([], C))
    else:
        arr1 = [C + i for i in range(n)]
        tests.append((arr1, C))

        arr2 = [C + i + 1 for i in range(n)]
        tests.append((arr2, C))

        arr3 = [C - i - 1 for i in range(n)]
        tests.append((arr3, C))

        arr4 = [C - 1] + [C + i for i in range(n - 1)] if n > 1 else [C - 1]
        tests.append((arr4, C))

        if n >= 3:
            arr5 = [C - 1 if i % 2 == 0 else C + 1 for i in range(n)]
            tests.append((arr5, C))
        else:
            arr5 = [C - 0.5, C + 0.5][:n]
            tests.append((arr5, C))

    return tests


def generate_random_test(n, C):
    if n == 0:
        return [], C
    arr = [round(C + random.uniform(-10, 10), 2) for _ in range(n)]
    return arr, C

# ----------------------------
# Основное GUI-приложение
# ----------------------------

class TestApp:
    def __init__(self, root):
        self.root = root
        self.root.title(
            "Тестирование методом классов эквивалентности (Вариант 9)")
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

        tk.Label(frame_input, text="n (количество элементов):").grid(
            row=0, column=0, padx=5, sticky='e')
        self.entry_n = tk.Entry(frame_input, width=10)
        self.entry_n.grid(row=0, column=1, padx=5)

        tk.Label(frame_input, text="C (порог):").grid(
            row=0, column=2, padx=5, sticky='e')
        self.entry_c = tk.Entry(frame_input, width=10)
        self.entry_c.grid(row=0, column=3, padx=5)

        tk.Label(frame_input, text="k (количество тестов):").grid(
            row=0, column=4, padx=5, sticky='e')
        self.entry_k = tk.Entry(frame_input, width=10)
        self.entry_k.grid(row=0, column=5, padx=5)

        tk.Button(frame_input, text="Запустить тесты",
                  command=self.run_tests).grid(row=0, column=6, padx=10)
        tk.Button(frame_input, text="Сохранить отчёт",
                  command=self.save_report).grid(row=0, column=7, padx=10)

        frame_table = tk.Frame(self.tab_test)
        frame_table.pack(fill='both', expand=True, padx=10, pady=10)

        columns = ("#", "Массив", "Ожидаемо", "Фактически", "Результат")
        self.tree = ttk.Treeview(
            frame_table, columns=columns, show='headings', height=15)
        for col in columns:
            self.tree.heading(col, text=col)
            self.tree.column(col, width=100 if col == "#" else 150)

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
        canvas = tk.Canvas(self.tab_help)
        scrollbar = ttk.Scrollbar(
            self.tab_help, orient="vertical", command=canvas.yview)
        scrollable_frame = tk.Frame(canvas)

        scrollable_frame.bind(
            "<Configure>",
            lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
        )

        canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)

        canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")

        try:
            img1_path = BASE_DIR / "diagram.png"
            img1 = Image.open(img1_path)
            img1 = img1.resize((800, 300), Image.LANCZOS)
            self.img1_tk = ImageTk.PhotoImage(img1)
            label1 = tk.Label(scrollable_frame, image=self.img1_tk)
            label1.pack(pady=10)

            img2_path = BASE_DIR / "tree.png"
            img2 = Image.open(img2_path)
            img2 = img2.resize((800, 400), Image.LANCZOS)
            self.img2_tk = ImageTk.PhotoImage(img2)
            label2 = tk.Label(scrollable_frame, image=self.img2_tk)
            label2.pack(pady=10)

        except Exception as e:
            pass

    def run_tests(self):
        try:
            n = int(self.entry_n.get())
            C = float(self.entry_c.get())
            k = int(self.entry_k.get())
            if n < 0 or k <= 0:
                raise ValueError
        except ValueError:
            messagebox.showerror(
                "Ошибка ввода", "Проверьте корректность n, C и k (n ≥ 0, k ≥ 1).")
            return

        for item in self.tree.get_children():
            self.tree.delete(item)

        rep_tests = generate_representative_tests(n, C)
        all_tests = []

        if k <= len(rep_tests):
            all_tests = rep_tests[:k]
        else:
            all_tests = rep_tests[:]
            for _ in range(k - len(rep_tests)):
                all_tests.append(generate_random_test(n, C))

        self.test_results = []
        for idx, (arr, c_val) in enumerate(all_tests, 1):
            expected = correct_algorithm(arr, c_val)
            actual = buggy_algorithm(arr, c_val)
            status = "Успешно" if expected != actual else "НЕУСПЕШНО"

            arr_str = "[" + ", ".join(f"{x:.2f}" if isinstance(x,
                                      float) else str(x) for x in arr) + "]"
            exp_str = f"({expected[0]}, {expected[1]})"
            act_str = f"({actual[0]}, {actual[1]})"

            tag = "fail" if status == "НЕУСПЕШНО" else "pass"
            self.tree.insert("", "end", values=(
                idx, arr_str, exp_str, act_str, status), tags=(tag,))

            self.test_results.append({
                '№': idx,
                'Массив': arr_str,
                'Ожидаемый результат': exp_str,
                'Фактический результат': act_str,
                'Результат теста': status
            })

    def save_report(self):
        if not hasattr(self, 'test_results') or len(self.test_results) == 0:
            messagebox.showwarning("Нет данных", "Сначала запустите тесты!")
            return

        filename = filedialog.asksaveasfilename(
            defaultextension=".csv",
            filetypes=[("CSV files", "*.csv"), ("All files", "*.*")],
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
            messagebox.showinfo("Успех", f"Отчёт сохранён в:\n{filename}")
        except Exception as e:
            messagebox.showerror(
                "Ошибка", f"Не удалось сохранить отчёт:\n{str(e)}")


# ----------------------------
# Запуск
# ----------------------------

if __name__ == "__main__":
    root = tk.Tk()
    app = TestApp(root)
    root.mainloop()
