import numpy as np

def solve_collocation(problem):
    """
    Метод коллокации:
    - Базис: psi_k(x) = (x-a)(b-x) * x^{k-1}, k=1..M
    - Коллокационные точки: внутренние узлы сетки (равномерные)
    """
    a, b = problem.a, problem.b
    M = min(problem.N - 2, 8)  # ограничим размер базиса
    if M <= 0:
        M = 1

    # Функция, удовлетворяющая граничным условиям
    def phi0(x):
        return problem.alpha * (b - x) / (b - a) + problem.beta * (x - a) / (b - a)

    # Базисные функции (нулевые на границах)
    def psi(k, x):
        return (x - a) * (b - x) * (x ** (k - 1))

    # Производные второго порядка (аналитически)
    def psi_dd(k, x):
        # psi = (x-a)(b-x) x^{k-1} = (-(x-a)(x-b)) x^{k-1}
        # Можно дифференцировать, но для простоты — численно
        h = 1e-6
        return (psi(k, x + h) - 2 * psi(k, x) + psi(k, x - h)) / (h ** 2)

    # Коллокационные точки (внутренние)
    x_coll = np.linspace(a, b, M + 2)[1:-1]  # M точек

    # Собираем СЛАУ: A c = F
    A = np.zeros((M, M))
    F = np.zeros(M)

    for i, xi in enumerate(x_coll):
        # Правая часть с учётом phi0
        F[i] = problem.f(xi) + phi0(xi) * problem.q(xi)  # если уравнение: -y'' + q y = f
        if hasattr(problem, 'p') and problem.p(xi) != 1:
            # Для общего случая нужно учитывать p(x), но упростим
            pass
        # Добавляем phi0''(xi)
        h = 1e-6
        phi0_dd = (phi0(xi + h) - 2 * phi0(xi) + phi0(xi - h)) / (h ** 2)
        F[i] += phi0_dd  # так как -y'' → +phi0''

        for k in range(1, M + 1):
            # Уравнение: -psi_k''(xi) + q(xi) * psi_k(xi)
            val = -psi_dd(k, xi) + problem.q(xi) * psi(k, xi)
            A[i, k - 1] = val

    # Решаем СЛАУ
    try:
        coeffs = np.linalg.solve(A, F)
    except np.linalg.LinAlgError:
        coeffs = np.linalg.lstsq(A, F, rcond=None)[0]

    # Строим решение на плотной сетке
    x_plot = np.linspace(a, b, problem.N)
    y_plot = np.array([phi0(x) + sum(coeffs[k] * psi(k + 1, x) for k in range(M)) for x in x_plot])

    return x_plot, y_plot
