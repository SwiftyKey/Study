from dataclasses import dataclass
from typing import Callable, Optional
import numpy as np

@dataclass
class BoundaryValueProblem:
    """
    Представление краевой задачи:
    - (p(x) * y')' + q(x) * y = f(x)  на [a, b]
    - y(a) = alpha, y(b) = beta
    """
    a: float
    b: float
    alpha: float
    beta: float
    p: Callable[[float], float]
    q: Callable[[float], float]
    f: Callable[[float], float]
    exact: Optional[Callable[[float], float]] = None
    N: int = 50

    def get_grid(self):
        return np.linspace(self.a, self.b, self.N)
