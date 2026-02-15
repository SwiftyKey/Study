import matplotlib.pyplot as plt
import numpy as np
import os
from pathlib import Path

BASE_DIR = Path(os.path.dirname(os.path.abspath(__file__)))

def plot_gamma_curves(gammas=None, save_path=BASE_DIR / "gamma_curves.png"):
    if gammas is None:
        gammas = [0.5, 1.0, 2.2]

    x = np.arange(256)

    plt.figure(figsize=(10, 6))

    colors = ['blue', 'green', 'red']
    for gamma, color in zip(gammas, colors):
        y = 255 * ((x / 255.0) ** gamma)
        plt.plot(x, y, label=f'γ = {gamma}', color=color, linewidth=2.5)

    plt.plot(x, x, 'k--', label='y = x (линейное)', linewidth=1.5, alpha=0.7)

    plt.title('Гамма-коррекция: входная яркость → выходная яркость', fontsize=14, fontweight='bold')
    plt.xlabel('Входная яркость (V_in)', fontsize=12)
    plt.ylabel('Выходная яркость (V_out)', fontsize=12)
    plt.grid(True, linestyle='--', alpha=0.7)
    plt.legend(fontsize=11)
    plt.xlim(0, 255)
    plt.ylim(0, 255)

    plt.annotate('γ < 1: осветление теней\n(тёмные участки становятся ярче)',
                xy=(64, 180), fontsize=9, color='blue',
                bbox=dict(boxstyle='round,pad=0.5', facecolor='lightblue', alpha=0.7))

    plt.annotate('γ > 1: затемнение светов\n(светлые участки становятся темнее)',
                xy=(192, 80), fontsize=9, color='red',
                bbox=dict(boxstyle='round,pad=0.5', facecolor='lightcoral', alpha=0.7))

    plt.tight_layout()
    plt.savefig(save_path, dpi=150)
    plt.show()

    print(f"График сохранён: {save_path}")
    return plt.gcf()

plot_gamma_curves([0.5, 1.0, 2.2], BASE_DIR / "gamma_curves.png")
