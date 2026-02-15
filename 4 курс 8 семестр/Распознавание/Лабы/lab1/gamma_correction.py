import math
import os
from PIL import Image
from pathlib import Path

BASE_DIR = Path(os.path.dirname(os.path.abspath(__file__)))

def gamma_correction(image_path, gamma, output_path):
    img = Image.open(image_path)

    if img.mode != 'RGB':
        img = img.convert('RGB')

    width, height = img.size

    corrected_img = Image.new('RGB', (width, height))

    # Предвычисляем таблицу преобразования для ускорения
    lookup_table = [int(255 * ((i / 255.0) ** gamma)) for i in range(256)]

    for y in range(height):
        for x in range(width):
            r, g, b = img.getpixel((x, y))

            r_corrected = lookup_table[r]
            g_corrected = lookup_table[g]
            b_corrected = lookup_table[b]

            corrected_img.putpixel((x, y), (r_corrected, g_corrected, b_corrected))

    corrected_img.save(output_path)
    print(f"Гамма-коррекция (γ={gamma}) применена. Результат сохранён в {output_path}")
    return corrected_img

if __name__ == "__main__":
    original = BASE_DIR / "input.png"

    gamma_correction(original, gamma=0.5, output_path=BASE_DIR / "output_gamma_0.5.png")  # осветление
    gamma_correction(original, gamma=1.0, output_path=BASE_DIR / "output_gamma_1.0.png")  # оригинал
    gamma_correction(original, gamma=2.2, output_path=BASE_DIR / "output_gamma_2.2.png")  # затемнение
