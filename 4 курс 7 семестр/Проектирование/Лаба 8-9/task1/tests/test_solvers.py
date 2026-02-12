import pytest
import numpy as np
from core.problem import BoundaryValueProblem
from core.tools import (
    solve_finite_difference,
    solve_collocation,
    solve_least_squares,
    solve_galerkin
)

# Точное решение тестовой задачи
def exact_solution(x):
    return np.sin(np.pi * x)

def test_finite_difference_accuracy():
    """Тест: метод конечных разностей на задаче y'' = -pi^2 sin(pi x)"""
    problem = BoundaryValueProblem(
        a=0.0,
        b=1.0,
        alpha=0.0,
        beta=0.0,
        p=lambda x: 1.0,
        q=lambda x: 0.0,
        f=lambda x: - (np.pi ** 2) * np.sin(np.pi * x),
        exact=exact_solution,
        N=50
    )

    x, y_num = solve_finite_difference(problem)
    y_exact = exact_solution(x)

    # Погрешность должна быть < 1e-3 при N=50 (второй порядок)
    error = np.max(np.abs(y_num - y_exact))
    assert error < 1e-3, f"Погрешность слишком велика: {error}"

def test_finite_difference_boundary_conditions():
    """Граничные условия должны выполняться точно"""
    problem = BoundaryValueProblem(
        a=0.0, b=2.0, alpha=1.0, beta=3.0,
        p=lambda x: 1.0,
        q=lambda x: 0.0,
        f=lambda x: 0.0,
        N=20
    )
    x, y = solve_finite_difference(problem)
    assert abs(y[0] - 1.0) < 1e-12
    assert abs(y[-1] - 3.0) < 1e-12

def test_collocation_method():
    problem = BoundaryValueProblem(
        a=0.0, b=1.0, alpha=0.0, beta=0.0,
        p=lambda x: 1.0,
        q=lambda x: 0.0,
        f=lambda x: - (np.pi ** 2) * np.sin(np.pi * x),
        exact=exact_solution,
        N=10
    )
    x, y_num = solve_collocation(problem)
    y_exact = exact_solution(x)
    error = np.max(np.abs(y_num - y_exact))
    assert error < 2

def test_least_squares_method():
    """МНК должен работать без ошибок и давать разумный результат"""
    problem = BoundaryValueProblem(
        a=0.0, b=1.0, alpha=0.0, beta=0.0,
        p=lambda x: 1.0,
        q=lambda x: 0.0,
        f=lambda x: - (np.pi ** 2) * np.sin(np.pi * x),
        exact=exact_solution,
        N=10
    )
    x, y_num = solve_least_squares(problem)
    y_exact = exact_solution(x)
    error = np.max(np.abs(y_num - y_exact))
    assert error < 2

def test_galerkin_method():
    """Метод Галеркина должен работать"""
    problem = BoundaryValueProblem(
        a=0.0, b=1.0, alpha=0.0, beta=0.0,
        p=lambda x: 1.0,
        q=lambda x: 0.0,
        f=lambda x: - (np.pi ** 2) * np.sin(np.pi * x),
        exact=exact_solution,
        N=10
    )
    x, y_num = solve_galerkin(problem)
    y_exact = exact_solution(x)
    error = np.max(np.abs(y_num - y_exact))
    assert error < 2

def test_invalid_N():
    """N должно быть >= 3"""
    problem = BoundaryValueProblem(
        a=0.0, b=1.0, alpha=0.0, beta=0.0,
        p=lambda x: 1.0,
        q=lambda x: 0.0,
        f=lambda x: -x,
        N=2
    )
    with pytest.raises(ValueError):
        solve_finite_difference(problem)

# Тест для метода прогонки (он же конечные разности)
def test_tridiagonal_same_as_fd():
    """Метод прогонки = метод конечных разностей"""
    from core.tools import solve_tridiagonal
    problem = BoundaryValueProblem(
        a=0.0, b=1.0, alpha=0.0, beta=0.0,
        p=lambda x: 1.0,
        q=lambda x: 0.0,
        f=lambda x: - (np.pi ** 2) * np.sin(np.pi * x),
        N=20
    )
    x1, y1 = solve_finite_difference(problem)
    x2, y2 = solve_tridiagonal(problem)
    assert np.allclose(x1, x2)
    assert np.allclose(y1, y2, atol=1e-12)
