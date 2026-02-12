import tkinter as tk
from tkinter import ttk, messagebox, filedialog
import math
import csv
from pathlib import Path
import os

BASE_DIR = Path(os.path.dirname(os.path.abspath(__file__)))

try:
    from PIL import Image, ImageTk
    PIL_AVAILABLE = True
except Exception:
    PIL_AVAILABLE = False

# --- Корректный алгоритм (схема а) ) ---


def correct_algorithm(a, b, c, x):
    a = float(a)
    b = float(b)
    c = float(c)
    x = float(x)
    if a < 0 and x != 0:
        return a * x**2 + (b**2) * x
    elif a > 0 and x == 0:
        denom = x - c
        if denom == 0.0:
            raise ZeroDivisionError("division by zero in a/(x-c)")
        return x - a/denom
    else:
        if c == 0.0:
            raise ZeroDivisionError("division by zero in x/c")
        return 1 + x/c

# --- Ошибочный алгоритм (схема б) ) ---


def buggy_algorithm(a, b, c, x):
    a = float(a)
    b = float(b)
    c = float(c)
    x = float(x)
    if a < 0 and x != 0:
        return a * x**2 + (b * 2) * x
    elif a > 0 or x == 0:
        denom = x - c
        if denom == 0.0:
            raise ZeroDivisionError("division by zero in a/(x-c)")
        return x - a/denom
    else:
        if c == 0.0:
            raise ZeroDivisionError("division by zero in x/c")
        return 1 + x/c


# --- Базовый набор тестов (из отчёта) ---
BASIC_TESTS = [
    ("T1", -2, 1, 5, 3),
    ("T2", 3, 2, 5, 0),
    ("T3", 3, 2, 2, 1),
    ("T4", -2, 1, 5, 0),
    ("T5", 0, 2, 4, 2),
    ("T6", 3, 2, 0, 0),
    ("T7", 0, 1, 0, 2),
    ("T8", -1, -3, 2, 2),
]

# Имена тестов для режимов
TEST_OPERATORS = ["T1"]
TEST_DECISIONS = ["T1", "T2", "T3"]
TEST_CONDITIONS = ["T1", "T2", "T3"]
TEST_DECISION_COND = ["T1", "T2", "T3"]
TEST_COMBINATORIAL = ["T1", "T4", "T3", "T2"]

# Словарь по именам для быстрого поиска
TEST_MAP = {name: (name, a, b, c, x) for (name, a, b, c, x) in BASIC_TESTS}

# --- GUI класс ---


class App:
    def __init__(self, root):
        self.root = root
        root.title("Тестирование функции — белый ящик")
        self._load_images()
        self._create_widgets()

    def _load_images(self):
        # пути с ожидаемыми именами файлов; замените при необходимости
        p_correct = BASE_DIR / "correct.png"
        p_buggy = BASE_DIR / "buggy.png"
        self.img_correct = p_correct if p_correct.exists() else None
        self.img_buggy = p_buggy if p_buggy.exists() else None

    def _create_widgets(self):
        frm = ttk.Frame(self.root, padding=8)
        frm.pack(fill="both", expand=True)

        # Controls: radio modes + buttons
        ctrl = ttk.Frame(frm)
        ctrl.pack(fill="x", pady=(0, 8))

        ttk.Label(ctrl, text="Режим тестирования:").grid(
            row=0, column=0, sticky="w")
        self.mode = tk.StringVar(value="operators")
        modes = [("Покрытие операторов", "operators"),
                 ("Покрытие решений", "decisions"),
                 ("Покрытие условий", "conditions"),
                 ("Покрытие решений/условий", "decision_cond"),
                 ("Комбинаторное покрытие", "combinatorial")]
        col = 1
        for (lab, val) in modes:
            ttk.Radiobutton(ctrl, text=lab, variable=self.mode,
                            value=val).grid(row=0, column=col, padx=6)
            col += 1

        ttk.Button(ctrl, text="Справка (блок-схемы)",
                   command=self.show_help).grid(row=0, column=col, padx=6)
        ttk.Button(ctrl, text="Запустить тесты", command=self.run_selected_tests).grid(
            row=0, column=col+1, padx=6)
        ttk.Button(ctrl, text="Экспорт в CSV", command=self.export_csv).grid(
            row=0, column=col+2, padx=6)

        # Таблица результатов
        cols = ("Тест", "Ввод (a,b,c,x)", "Ожидаемый результат", "Фактический результат", "Результат теста")
        self.tree = ttk.Treeview(frm, columns=cols, show="headings", height=14)
        for c in cols:
            self.tree.heading(c, text=c)
            self.tree.column(c, width=150)
        self.tree.pack(fill="both", expand=True)

        self.status = ttk.Label(frm, text="Готово")
        self.status.pack(fill="x", pady=(6, 0))

    def show_help(self):
        top = tk.Toplevel(self.root)
        top.title("Справка — блок-схемы")
        lbl = ttk.Label(
            top, text="Слева: правильная схема. Справа: схема с ошибкой.")
        lbl.pack(padx=8, pady=(8, 4))

        canvas = ttk.Frame(top)
        canvas.pack(fill="both", expand=True, padx=8, pady=8)

        if self.img_correct and PIL_AVAILABLE:
            im = Image.open(self.img_correct)
            im.thumbnail((420, 300))
            ph = ImageTk.PhotoImage(im)
            l1 = ttk.Label(canvas, image=ph)
            l1.image = ph
            l1.pack(side="left", padx=6)
        elif self.img_correct:
            ttk.Label(canvas, text=f"Правильная схема: {self.img_correct}").pack(
                side="left", padx=6)
        else:
            ttk.Label(canvas, text="(Файл правильной схемы не найден)").pack(
                side="left", padx=6)

        if self.img_buggy and PIL_AVAILABLE:
            im2 = Image.open(self.img_buggy)
            im2.thumbnail((420, 300))
            ph2 = ImageTk.PhotoImage(im2)
            l2 = ttk.Label(canvas, image=ph2)
            l2.image = ph2
            l2.pack(side="left", padx=6)
        elif self.img_buggy:
            ttk.Label(canvas, text=f"Ошибочная схема: {self.img_buggy}").pack(
                side="left", padx=6)
        else:
            ttk.Label(canvas, text="(Файл ошибочной схемы не найден)").pack(
                side="left", padx=6)

    def run_selected_tests(self):
        mode = self.mode.get()
        if mode == "operators":
            names = TEST_OPERATORS
        elif mode == "decisions":
            names = TEST_DECISIONS
        elif mode == "conditions":
            names = TEST_CONDITIONS
        elif mode == "decision_cond":
            names = TEST_DECISION_COND
        elif mode == "combinatorial":
            names = TEST_COMBINATORIAL
        else:
            names = []

        tests = []
        for n in names:
            if n in TEST_MAP:
                nm, a, b, c, x = TEST_MAP[n]
                tests.append((nm, a, b, c, x))
            else:
                # fallback - search in BASIC_TESTS
                for it in BASIC_TESTS:
                    if it[0] == n:
                        tests.append(it)
                        break

        # Выполнить тесты
        self.tree.delete(*self.tree.get_children())
        rows = []
        for (nm, a, b, c, x) in tests:
            try:
                expected = correct_algorithm(a, b, c, x)
            except ZeroDivisionError as e:
                expected = f"Error: {e}"
            try:
                actual = buggy_algorithm(a, b, c, x)
            except ZeroDivisionError as e:
                actual = f"Error: {e}"
            match = "Успешно" if expected != actual else "Неуспешно"
            self.tree.insert("", "end", values=(
                nm, f"({a},{b},{c},{x})", expected, actual, match))
            rows.append((nm, f"({a},{b},{c},{x})", expected, actual, match))
        self.status.config(text=f"Запущено {len(rows)} тестов.")

    def export_csv(self):
        fname = filedialog.asksaveasfilename(
            defaultextension=".csv", filetypes=[("CSV files", "*.csv")])
        if not fname:
            return
        rows = []
        for iid in self.tree.get_children():
            rows.append(self.tree.item(iid)["values"])
        try:
            with open(fname, "w", newline="", encoding="utf-8") as f:
                writer = csv.writer(f)
                writer.writerow(["Тест", "Ввод (a,b,c,x)", "Ожидаемый результат",
                                "Фактический результат", "Результат теста"])
                for r in rows:
                    writer.writerow(r)
            messagebox.showinfo(
                "Экспорт", f"Экспортировано {len(rows)} строк в {fname}")
        except Exception as e:
            messagebox.showerror("Ошибка экспорта", str(e))


# --- Запуск приложения ---
if __name__ == "__main__":
    root = tk.Tk()
    app = App(root)
    root.mainloop()
