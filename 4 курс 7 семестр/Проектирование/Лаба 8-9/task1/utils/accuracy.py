import numpy as np

def estimate_accuracy(x_num, y_num, exact_func):
    y_exact = np.array([exact_func(xi) for xi in x_num])
    abs_err = np.abs(y_num - y_exact)
    rel_err = abs_err / (np.abs(y_exact) + 1e-12)
    return {
        "L2": np.linalg.norm(abs_err) / np.sqrt(len(x_num)),
        "L∞": np.max(abs_err),
        "max_relative": np.max(rel_err),
    }
