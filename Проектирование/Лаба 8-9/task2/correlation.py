import numpy as np
from sklearn.metrics import r2_score

def fit_polynomial(x, y, degree=2):
    """
    Аппроксимация кривой полиномом заданной степени.
    Возвращает:
      - коэффициенты полинома,
      - R²,
      - функцию для предсказания,
      - уравнение в строке.
    """
    coeffs = np.polyfit(x, y, degree)
    poly = np.poly1d(coeffs)
    y_pred = poly(x)
    r2 = r2_score(y, y_pred)

    # Форматируем уравнение
    terms = []
    for i, c in enumerate(coeffs):
        power = degree - i
        if power == 0:
            terms.append(f"{c:.3f}")
        elif power == 1:
            terms.append(f"{c:.3f}·x")
        else:
            terms.append(f"{c:.3f}·x^{power}")
    equation = " + ".join(terms).replace("+ -", "- ")

    return coeffs, r2, poly, equation
