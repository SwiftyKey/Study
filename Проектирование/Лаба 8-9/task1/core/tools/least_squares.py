import numpy as np
from scipy import integrate

def solve_least_squares(problem):
    """
    Метод наименьших квадратов:
    Минимизируем ||L[y_N] - f||^2 по L2-норме.
    """
    a, b = problem.a, problem.b
    M = min(problem.N - 2, 6)

    def phi0(x):
        return problem.alpha * (b - x) / (b - a) + problem.beta * (x - a) / (b - a)

    def psi(k, x):
        return (x - a) * (b - x) * (x ** (k - 1))

    def psi_dd(k, x):
        h = 1e-6
        return (psi(k, x + h) - 2 * psi(k, x) + psi(k, x - h)) / (h ** 2)

    h = 1e-6
    def phi0_dd(x):
        return (phi0(x + h) - 2 * phi0(x) + phi0(x - h)) / (h ** 2)

    # Матрица Грама G_ij = ∫ (L[psi_i]) (L[psi_j]) dx
    G = np.zeros((M, M))
    rhs = np.zeros(M)

    def L_psi(k, x):
        return -psi_dd(k, x) + problem.q(x) * psi(k, x)

    def L_phi0(x):
        return -phi0_dd(x) + problem.q(x) * phi0(x)

    # Интегрирование по Гауссу (или простое)
    x_quad = np.linspace(a, b, 200)
    w = (b - a) / (len(x_quad) - 1)

    for i in range(M):
        for j in range(M):
            integrand = L_psi(i + 1, x_quad) * L_psi(j + 1, x_quad)
            G[i, j] = np.sum(integrand) * w

        integrand_f = (problem.f(x_quad) - L_phi0(x_quad)) * L_psi(i + 1, x_quad)
        rhs[i] = np.sum(integrand_f) * w

    try:
        coeffs = np.linalg.solve(G, rhs)
    except np.linalg.LinAlgError:
        coeffs = np.linalg.lstsq(G, rhs, rcond=None)[0]

    x_plot = np.linspace(a, b, problem.N)
    y_plot = np.array([phi0(x) + sum(coeffs[k] * psi(k + 1, x) for k in range(M)) for x in x_plot])
    return x_plot, y_plot
