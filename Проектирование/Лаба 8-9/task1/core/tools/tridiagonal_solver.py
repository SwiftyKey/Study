import numpy as np

def thomas_algorithm(a, b, c, d):
    """
    Решение трёхдиагональной системы Ax = d методом прогонки.
    a — поддиагональ (длина n-1)
    b — диагональ (длина n)
    c — наддиагональ (длина n-1)
    d — правая часть (длина n)
    """
    n = len(b)
    if n == 1:
        return np.array([d[0] / b[0]])

    c_prime = np.zeros(n - 1)
    d_prime = np.zeros(n)

    c_prime[0] = c[0] / b[0]
    d_prime[0] = d[0] / b[0]

    for i in range(1, n - 1):
        denom = b[i] - a[i - 1] * c_prime[i - 1]
        c_prime[i] = c[i] / denom
        d_prime[i] = (d[i] - a[i - 1] * d_prime[i - 1]) / denom

    d_prime[-1] = (d[-1] - a[-2] * d_prime[-2]) / (b[-1] - a[-2] * c_prime[-2])

    # Обратный ход
    x = np.zeros(n)
    x[-1] = d_prime[-1]
    for i in range(n - 2, -1, -1):
        x[i] = d_prime[i] - c_prime[i] * x[i + 1]

    return x
