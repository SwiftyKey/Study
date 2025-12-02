from .finite_difference import solve_finite_difference

# Прогонка = конечные разности
solve_tridiagonal = solve_finite_difference

# Остальные методы
from .collocation import solve_collocation
from .least_squares import solve_least_squares
from .galerkin import solve_galerkin

TOOLS_MAP = {
    "Метод конечных разностей": solve_finite_difference,
    "Метод прогонки": solve_tridiagonal,
    "Метод коллокации": solve_collocation,
    "Метод наименьших квадратов": solve_least_squares,
    "Метод Галеркина": solve_galerkin,
}
