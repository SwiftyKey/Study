import numpy as np

def solve_collocation(problem):
    """
    Метод коллокации с аналитической второй производной.
    Базис: psi_k(x) = x^k - x^{k+1}, k=1..M
    """
    a, b = problem.a, problem.b
    M = min(problem.N - 2, 4)  # уменьшено до 4
    if M <= 0:
        M = 1

    # phi0(x) = 0, так как alpha=beta=0 в тестовой задаче
    def phi0(x):
        return problem.alpha * (b - x) / (b - a) + problem.beta * (x - a) / (b - a)

    def phi0_dd(x):
        # Вторая производная линейной функции = 0
        return 0.0

    # Аналитическая вторая производная psi_k
    def psi_dd(k, x):
        if k == 1:
            # psi_1 = x - x^2 → psi_1'' = -2
            return -2.0
        else:
            term1 = k * (k - 1) * (x ** (k - 2)) if x != 0 or k > 2 else 0.0
            term2 = (k + 1) * k * (x ** (k - 1))
            return term1 - term2

    def psi(k, x):
        return (x ** k) - (x ** (k + 1))

    # Коллокационные точки — внутренние узлы
    x_coll = np.linspace(a, b, M + 2)[1:-1]

    A = np.zeros((M, M))
    F = np.zeros(M)

    for i, xi in enumerate(x_coll):
        # Правая часть: f(xi) + phi0''(xi) - q(xi)*phi0(xi)
        F[i] = problem.f(xi) + phi0_dd(xi) - problem.q(xi) * phi0(xi)

        for k in range(1, M + 1):
            # Уравнение: -psi_k''(xi) + q(xi)*psi_k(xi)
            A[i, k - 1] = -psi_dd(k, xi) + problem.q(xi) * psi(k, xi)

    try:
        coeffs = np.linalg.solve(A, F)
    except np.linalg.LinAlgError:
        coeffs = np.linalg.lstsq(A, F, rcond=None)[0]

    # Строим решение
    x_plot = np.linspace(a, b, problem.N)
    y_plot = np.array([
        phi0(x) + sum(coeffs[k] * psi(k + 1, x) for k in range(M))
        for x in x_plot
    ])
    return x_plot, y_plot
