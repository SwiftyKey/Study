import flet as ft
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import numpy as np
import io
import base64
from core.problem import BoundaryValueProblem
from core.tools import TOOLS_MAP
from utils.accuracy import estimate_accuracy

def main(page: ft.Page):
    page.title = "ППП: Краевые задачи ОДУ"
    page.scroll = "auto"

    # Поля ввода
    a_field = ft.TextField(label="a", value="0", width=100)
    b_field = ft.TextField(label="b", value="1", width=100)
    alpha_field = ft.TextField(label="y(a)", value="0", width=100)
    beta_field = ft.TextField(label="y(b)", value="0", width=100)
    N_field = ft.TextField(label="Число узлов", value="20", width=120)

    method_dropdown = ft.Dropdown(
        label="Метод",
        options=[ft.dropdown.Option(key=k, text=k) for k in TOOLS_MAP.keys()],
        width=250,
    )

    result_image = ft.Image(visible=False, width=600, height=400)
    error_text = ft.Text()

    def on_solve(e):
        try:
            a = float(a_field.value)
            b = float(b_field.value)
            alpha = float(alpha_field.value)
            beta = float(beta_field.value)
            N = int(N_field.value)
            if N < 3:
                raise ValueError("N должно быть >= 3")

            # Пример: y'' = -pi^2 sin(pi x), y(0)=y(1)=0 → y=sin(pi x)
            problem = BoundaryValueProblem(
                a=a, b=b, alpha=alpha, beta=beta,
                p=lambda x: 1.0,
                q=lambda x: 0.0,
                f=lambda x: - (np.pi ** 2) * np.sin(np.pi * x),
                exact=lambda x: np.sin(np.pi * x),
                N=N
            )

            solver = TOOLS_MAP[method_dropdown.value]
            x, y = solver(problem)

            if isinstance(y, str):  # заглушка
                error_text.value = y
                result_image.visible = False
                page.update()
                return

            # Оценка точности
            acc = estimate_accuracy(x, y, problem.exact)
            error_text.value = f"Погрешность L∞: {acc['L∞']:.2e} | L2: {acc['L2']:.2e}"

            # Визуализация
            plt.figure(figsize=(8, 5))
            plt.plot(x, y, 'o-', label='Численное решение')
            plt.plot(x, [problem.exact(xi) for xi in x], '--', label='Точное решение')
            plt.legend()
            plt.grid(True)
            plt.title(f"Решение ({method_dropdown.value})")

            buf = io.BytesIO()
            plt.savefig(buf, format="png")
            plt.close()
            buf.seek(0)
            img_base64 = base64.b64encode(buf.read()).decode("utf-8")
            result_image.src_base64 = img_base64
            result_image.visible = True

            page.update()
        except Exception as ex:
            error_text.value = f"Ошибка: {str(ex)}"
            result_image.visible = False
            page.update()

    solve_btn = ft.ElevatedButton("Решить", on_click=on_solve)

    page.add(
        ft.Text("ППП: Краевые задачи ОДУ", size=24, weight="bold"),
        ft.Row([a_field, b_field, alpha_field, beta_field, N_field]),
        method_dropdown,
        solve_btn,
        error_text,
        result_image,
        ft.Divider(),
        ft.Text("ℹ️ Текущая задача: y'' = -π²·sin(πx), y(0)=y(1)=0 → y=sin(πx)", italic=True)
    )

ft.app(target=main)
