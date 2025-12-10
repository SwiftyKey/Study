import numpy as np

def solve_galerkin(problem):
    """
    Метод Галеркина:
    ∫ (L[y_N] - f) * psi_j dx = 0  →  ∫ L[psi_i] psi_j dx = ∫ (f - L[phi0]) psi_j dx
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

    def L_psi(k, x):
        return -psi_dd(k, x) + problem.q(x) * psi(k, x)

    def L_phi0(x):
        return -phi0_dd(x) + problem.q(x) * phi0(x)

    # Интегрирование
    x_quad = np.linspace(a, b, 200)
    w = (b - a) / (len(x_quad) - 1)

    A = np.zeros((M, M))
    F = np.zeros(M)

    for i in range(M):
        for j in range(M):
            integrand = L_psi(i + 1, x_quad) * psi(j + 1, x_quad)
            A[i, j] = np.sum(integrand) * w

        integrand_f = (problem.f(x_quad) - L_phi0(x_quad)) * psi(i + 1, x_quad)
        F[i] = np.sum(integrand_f) * w

    try:
        coeffs = np.linalg.solve(A, F)
    except np.linalg.LinAlgError:
        coeffs = np.linalg.lstsq(A, F, rcond=None)[0]

    x_plot = np.linspace(a, b, problem.N)
    y_plot = np.array([-1 * phi0(x) - sum(coeffs[k] * psi(k + 1, x) for k in range(M)) for x in x_plot])
    return x_plot, y_plot
