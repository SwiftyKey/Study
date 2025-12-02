import numpy as np
from .tridiagonal_solver import thomas_algorithm

def solve_finite_difference(problem):
    a, b = problem.a, problem.b
    N = problem.N
    h = (b - a) / (N - 1)
    x = np.linspace(a, b, N)

    # Если N <= 2, невозможно решить внутренние узлы
    if N < 3:
        raise ValueError("Число узлов N должно быть >= 3")

    # Вектор решения: сначала ставим граничные условия
    y = np.zeros(N)
    y[0] = problem.alpha
    y[-1] = problem.beta

    # Количество внутренних узлов
    n_inner = N - 2
    if n_inner == 0:
        return x, y

    # Инициализируем диагонали для внутренней системы (размер n_inner)
    a_inner = np.zeros(n_inner - 1)  # поддиагональ (длина n_inner - 1)
    b_inner = np.zeros(n_inner)      # главная диагональ
    c_inner = np.zeros(n_inner - 1)  # наддиагональ
    d_inner = np.zeros(n_inner)      # правая часть

    # Заполняем коэффициенты для внутренних узлов i = 1 ... N-2
    for i in range(1, N - 1):
        idx = i - 1  # индекс в уменьшенной системе (0 ... n_inner-1)
        xi = x[i]

        # Полуузлы
        x_left = (x[i - 1] + x[i]) / 2
        x_right = (x[i] + x[i + 1]) / 2

        p_left = problem.p(x_left)
        p_right = problem.p(x_right)

        # Коэффициенты
        b_inner[idx] = -(p_left + p_right) / (h ** 2) + problem.q(xi)
        d_inner[idx] = problem.f(xi)

        # Поправка от граничных условий
        if i == 1:
            d_inner[idx] -= p_left / (h ** 2) * problem.alpha
        if i == N - 2:
            d_inner[idx] -= p_right / (h ** 2) * problem.beta

        # Связи с соседями (если есть)
        if idx > 0:
            a_inner[idx - 1] = p_left / (h ** 2)
        if idx < n_inner - 1:
            c_inner[idx] = p_right / (h ** 2)

    # Решаем внутреннюю систему методом прогонки
    if n_inner == 1:
        y_inner = np.array([d_inner[0] / b_inner[0]])
    else:
        y_inner = thomas_algorithm(a_inner, b_inner, c_inner, d_inner)

    # Вставляем решение во внутренние узлы
    y[1:N-1] = y_inner

    return x, y
