"""
Проект: Построение правильного n-угольника со стороной a (Tkinter)
Автор: Чернов С.Ю.
Дата: 2025-09-09
"""

import tkinter as tk
from tkinter import ttk, filedialog, messagebox
import math
import re


def compute_circumradius(n: int, side: float) -> float:
    if n < 3 or side <= 0:
        raise ValueError("n must be >=3 and side must be >0")
    return side / (2 * math.sin(math.pi / n))


def polygon_vertices(n: int, side: float, cx: float, cy: float, rotation: float = 0.0):
    R = compute_circumradius(n, side)
    verts = []
    for k in range(n):
        theta = 2 * math.pi * k / n + rotation - math.pi / 2
        x = cx + R * math.cos(theta)
        y = cy + R * math.sin(theta)
        verts.append((x, y))
    return verts


def bounding_box(verts):
    xs = [p[0] for p in verts]
    ys = [p[1] for p in verts]
    return min(xs), min(ys), max(xs), max(ys)


def validate_integer(value: str, minimum: int = 3) -> int:
    if not value.strip().isdigit():
        raise ValueError("Значение n должно быть целым числом")
    n = int(value)
    if n < minimum:
        raise ValueError(f"Значение n должно быть >= {minimum}")
    return n


def validate_float(value: str, minimum: float = 0.0) -> float:
    try:
        num = float(value)
    except ValueError:
        raise ValueError("Значение a должно быть числом")
    if num <= minimum:
        raise ValueError(f"Значение a должно быть > {minimum}")
    return num


def validate_color(value: str) -> str:
    if not value:
        return ""
    if re.match(r"^#[0-9A-Fa-f]{6}$", value):
        return value
    try:
        tmp = tk.Tk()
        tmp.withdraw()
        tmp.winfo_rgb(value)
        tmp.destroy()
        return value
    except tk.TclError:
        raise ValueError(f"Некорректный цвет: {value}")


class NGonApp(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Правильный n-угольник — Tkinter")
        self.geometry("900x600")

        self.n_var = tk.StringVar(value="5")
        self.a_var = tk.StringVar(value="100")
        self.stroke_var = tk.StringVar(value="#000000")
        self.fill_var = tk.StringVar(value="")

        self.error_var = tk.StringVar(value="")

        self.create_widgets()
        self.create_menu()
        self.bind_events()
        self.redraw_polygon()

    def create_widgets(self):
        control_frame = ttk.Frame(self)
        control_frame.pack(side=tk.LEFT, fill=tk.Y, padx=10, pady=10)

        ttk.Label(control_frame, text="n (>=3):").pack(anchor=tk.W)
        ttk.Entry(control_frame, textvariable=self.n_var).pack(fill=tk.X)

        ttk.Label(control_frame, text="a (>0):").pack(anchor=tk.W)
        ttk.Entry(control_frame, textvariable=self.a_var).pack(fill=tk.X)

        ttk.Label(control_frame, text="Цвет обводки:").pack(anchor=tk.W)
        ttk.Entry(control_frame, textvariable=self.stroke_var).pack(fill=tk.X)

        ttk.Label(control_frame, text="Цвет заливки:").pack(anchor=tk.W)
        ttk.Entry(control_frame, textvariable=self.fill_var).pack(fill=tk.X)

        ttk.Button(control_frame, text="Перерисовать",
                   command=self.redraw_polygon).pack(pady=5)
        ttk.Button(control_frame, text="Сохранить",
                   command=self.save_polygon).pack(pady=5)

        ttk.Label(control_frame, textvariable=self.error_var,
                  foreground="red", wraplength=200).pack(pady=5)

        self.canvas = tk.Canvas(self, bg="white")
        self.canvas.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True)

    def create_menu(self):
        menubar = tk.Menu(self)
        self.config(menu=menubar)

        help_menu = tk.Menu(menubar, tearoff=0)
        help_menu.add_command(label="Справка", command=self.show_help)
        menubar.add_cascade(label="Помощь", menu=help_menu)

    def bind_events(self):
        self.n_var.trace_add("write", lambda *args: self.schedule_redraw())
        self.a_var.trace_add("write", lambda *args: self.schedule_redraw())
        self.stroke_var.trace_add(
            "write", lambda *args: self.schedule_redraw())
        self.fill_var.trace_add("write", lambda *args: self.schedule_redraw())
        self.canvas.bind("<Configure>", lambda event: self.redraw_polygon())

    def schedule_redraw(self):
        self.after(500, self.redraw_polygon)

    def redraw_polygon(self):
        self.error_var.set("")
        try:
            n = validate_integer(self.n_var.get())
            a = validate_float(self.a_var.get(), minimum=0.0)
            stroke = validate_color(self.stroke_var.get())
            fill = validate_color(self.fill_var.get())
        except ValueError as e:
            self.error_var.set(str(e))
            self.canvas.delete("all")
            return

        w = self.canvas.winfo_width()
        h = self.canvas.winfo_height()
        cx, cy = w / 2, h / 2

        verts = polygon_vertices(n, a, cx, cy)
        minx, miny, maxx, maxy = bounding_box(verts)

        scale = min(w / (maxx - minx + 20), h / (maxy - miny + 20), 1.0)
        scaled = [(cx + (x - cx) * scale, cy + (y - cy) * scale)
                  for x, y in verts]

        self.canvas.delete("all")
        self.canvas.create_polygon(scaled, outline=stroke, fill=fill, width=2)

    def save_polygon(self):
        file = filedialog.asksaveasfilename(
            defaultextension=".ps", filetypes=[("PostScript", "*.ps")])
        if file:
            self.canvas.postscript(file=file)
            messagebox.showinfo("Сохранение", f"Файл сохранён: {file}")

    def show_help(self):
        help_win = tk.Toplevel(self)
        help_win.title("Справка")
        help_win.geometry("700x500")

        notebook = ttk.Notebook(help_win)
        notebook.pack(fill=tk.BOTH, expand=True)

        # Пользовательская документация
        user_text = tk.Text(notebook, wrap="word")
        user_scroll = ttk.Scrollbar(notebook, command=user_text.yview)
        user_text.configure(yscrollcommand=user_scroll.set)
        user_text.insert("1.0", """
Пользовательская документация (П-документация)

Общее функциональное описание ПС
- Приложение рисует правильный n-угольник с параметрами (n, a, цвета).
- Поддерживает ввод параметров и сохранение результата.

Руководство по инсталляции ПС (для администраторов)
- Требования: Python 3.8+, Tkinter.
- Установка: скачать task3.py и запустить `python task3.py`.

Инструкция по применению ПС (для ординарных пользователей)
- Введите n >= 3, a > 0, выберите цвета.
- Фигура обновляется автоматически или через кнопку "Перерисовать".
- Кнопка "Сохранить" сохраняет рисунок в файл .ps.

Справочник по применению ПС (для ординарных пользователей)
- n ≥ 3, a > 0.
- Цвет в hex (#RRGGBB) или по имени (red, blue, green).
- Ошибки отображаются под полями.

Руководство по управлению ПС (для администраторов)
- При ошибке проверить корректность данных.
- Если фигура не рисуется — проверить ввод.
- Для сохранения использовать PostScript.
""")
        user_text.config(state="disabled")
        user_text.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        user_scroll.pack(side=tk.RIGHT, fill=tk.Y)
        notebook.add(user_text, text="Пользовательская документация")

        # Документация по сопровождению
        dev_text = tk.Text(notebook, wrap="word")
        dev_scroll = ttk.Scrollbar(notebook, command=dev_text.yview)
        dev_text.configure(yscrollcommand=dev_scroll.set)
        dev_text.insert("1.0", """
Документация по сопровождению (С-документация)

Внешнее описание ПС (Requirements document)
- Программа строит правильный n-угольник со стороной a.
- Поддерживает ввод параметров, перерисовку, сохранение.

Описание архитектуры ПС
- Модули
\t- main (инициализация приложения)
\t- gui (виджеты ввода, кнопки, холст)
\t- geometry (вычисление вершин правильного n-угольника по стороне a)
\t- renderer (отрисовка на холсте, масштабирование)
\t- io (сохранение изображения)
\t- validation (валидация пользовательских данных)
- Взаимодействие модулей
\t- main (инициализация приложения)
\t\t- Запускает программу, создаёт главное окно и инициализирует все остальные модули;
\t\t- Организует поток данных: пользователь → gui → validation/geometry → renderer → io.
\t- gui (графический интерфейс: виджеты ввода, кнопки, холст)
\t\t- Обеспечивает ввод параметров (n, a, цвета);
\t\t- Передаёт введённые данные в validation для проверки;
\t\t- При корректных данных вызывает geometry для вычисления координат вершин;
\t\t- Передаёт результат в renderer для отрисовки;
\t\t- Запускает io, если пользователь выбрал сохранение.
\t- validation (валидация пользовательских данных)
\t\t- Проверяет правильность ввода:
\t\t\t- n — целое число ≥ 3;
\t\t\t- a — положительное число;
\t\t\t- цвета — допустимые hex или имена цветов.
\t\t- При ошибках возвращает сообщение в gui, чтобы отобразить его пользователю.
\t- geometry (вычисление вершин правильного n-угольника по стороне a)
\t\t- Получает параметры n, a и координаты центра (cx, cy);
\t\t- Вычисляет радиус описанной окружности;
\t\t- Возвращает список координат вершин многоугольника.
\t- renderer (отрисовка на холсте, масштабирование)
\t\t- Получает вершины от geometry;
\t\t- Вычисляет границы (bounding box) и масштабирует фигуру под размеры холста;
\t\t- Отрисовывает фигуру на gui.canvas с выбранными цветами.
\t- io (сохранение изображения)
\t\t- Получает текущее состояние холста (Canvas);
\t\t- Сохраняет изображение в формате PostScript (.ps), выбранное пользователем через диалог.

Описание модульной структуры
- Для каждого модуля — функции, входы/выходы.
- Пример: geometry.polygon_vertices(n, a, cx, cy).

Спецификации модулей
- Описаны входные параметры, возвращаемые значения, исключения.

Тексты модулей
- Исходный код приведён в программе (Python).

Документы установления достоверности
- Тесты: n=3,a=100 (треугольник), n=4,a=100 (квадрат), n=50,a=5 (почти окружность).
- Результаты тестов: успешная отрисовка.
""")
        dev_text.config(state="disabled")
        dev_text.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        dev_scroll.pack(side=tk.RIGHT, fill=tk.Y)
        notebook.add(dev_text, text="Документация по сопровождению")


if __name__ == "__main__":
    app = NGonApp()
    app.mainloop()
