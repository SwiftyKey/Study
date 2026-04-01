from PIL import Image
import numpy as np
import matplotlib.pyplot as plt
import os
from pathlib import Path

BASE_DIR = Path(os.path.dirname(os.path.abspath(__file__)))


def clip_histogram(histogram, clip_limit):
    if clip_limit <= 0:
        return histogram[:]

    clipped_hist = histogram[:]
    total_excess = 0

    for i in range(256):
        if clipped_hist[i] > clip_limit:
            excess = clipped_hist[i] - clip_limit
            total_excess += excess
            clipped_hist[i] = clip_limit

    bins_under_limit = [i for i in range(256) if clipped_hist[i] < clip_limit]
    if bins_under_limit:
        while total_excess > 0:
            distributed = 0
            for i in bins_under_limit:
                clipped_hist[i] += 1
                total_excess -= 1
                distributed += 1
                if total_excess <= 0:
                    break
            if distributed == 0:
                break

    return clipped_hist

def compute_cdf(histogram):
    cdf = [0] * 256
    cumulative = 0
    for i in range(256):
        cumulative += histogram[i]
        cdf[i] = cumulative
    return cdf

def create_mapping_function(histogram, total_pixels):
    cdf = compute_cdf(histogram)

    cdf_min = next((v for v in cdf if v > 0), 0)

    mapping = [0] * 256
    if total_pixels > cdf_min:
        scale = 255.0 / (total_pixels - cdf_min)
        for i in range(256):
            mapping[i] = int(round((cdf[i] - cdf_min) * scale))
            mapping[i] = max(0, min(255, mapping[i]))
    else:
        for i in range(256):
            mapping[i] = i

    return mapping

def apply_clahe_channel(channel_array, clip_limit=2.0, grid_size=(8, 8)):
    height, width = channel_array.shape
    grid_rows, grid_cols = grid_size

    tile_h = height // grid_rows
    tile_w = width // grid_cols

    # Создаём массив для хранения lookup-таблиц каждого блока
    # tables[row][col] = lookup_table (список из 256 значений)
    tables = [[None for _ in range(grid_cols + 1)] for _ in range(grid_rows + 1)]

    # 1. Обрабатываем все блоки сетки + краевые блоки
    for row in range(grid_rows + 1):
        for col in range(grid_cols + 1):
            # Определяем границы блока (с перекрытием для краёв)
            y_start = max(0, row * tile_h - tile_h // 2)
            y_end = min(height, y_start + tile_h)

            if row == 0:
                y_start = 0
            if row == grid_rows:
                y_start = height - tile_h
                y_end = height

            x_start = max(0, col * tile_w - tile_w // 2)
            x_end = min(width, x_start + tile_w)

            if col == 0:
                x_start = 0
            if col == grid_cols:
                x_start = width - tile_w
                x_end = width

            # Извлекаем блок
            tile = channel_array[y_start:y_end, x_start:x_end]
            tile_pixels = tile.size

            # Вычисляем гистограмму блока
            hist = [0] * 256
            for pixel in tile.flat:
                hist[pixel] += 1

            # Определяем порог клиппинга
            clip_value = int(round(clip_limit * (tile_pixels / 256.0)))

            # Применяем клиппинг и создаём таблицу преобразования
            clipped_hist = clip_histogram(hist, clip_value)
            mapping = create_mapping_function(clipped_hist, tile_pixels)

            tables[row][col] = mapping

    # 2. Применяем интерполяцию для каждого пикселя
    result = np.zeros_like(channel_array, dtype=np.uint8)

    for y in range(height):
        # Определяем, между какими строками блоков находится пиксель
        row = min(y * grid_rows // height, grid_rows - 1)
        y_block_start = row * tile_h
        y_weight = (y - y_block_start) / tile_h if tile_h > 0 else 0.0
        y_weight = max(0.0, min(1.0, y_weight))

        for x in range(width):
            # Определяем, между какими столбцами блоков находится пиксель
            col = min(x * grid_cols // width, grid_cols - 1)
            x_block_start = col * tile_w
            x_weight = (x - x_block_start) / tile_w if tile_w > 0 else 0.0
            x_weight = max(0.0, min(1.0, x_weight))

            # Получаем значение пикселя
            pixel_val = int(channel_array[y, x])

            # Билинейная интерполяция между 4 соседними блоками
            # Блоки: (row, col), (row, col+1), (row+1, col), (row+1, col+1)
            v00 = tables[row][col][pixel_val]
            v01 = tables[row][col + 1][pixel_val]
            v10 = tables[row + 1][col][pixel_val]
            v11 = tables[row + 1][col + 1][pixel_val]

            # Горизонтальная интерполяция
            v0 = v00 * (1 - x_weight) + v01 * x_weight
            v1 = v10 * (1 - x_weight) + v11 * x_weight

            # Вертикальная интерполяция
            v_final = v0 * (1 - y_weight) + v1 * y_weight

            result[y, x] = int(round(v_final))

    return result

def clahe_grayscale(image_path, clip_limit=2.0, grid_size=(8, 8), output_path=None):
    img = Image.open(image_path).convert('L')
    img_array = np.array(img, dtype=np.uint8)

    equalized_array = apply_clahe_channel(img_array, clip_limit, grid_size)
    equalized_img = Image.fromarray(equalized_array, mode='L')

    if output_path:
        equalized_img.save(output_path)
        print(f"CLAHE применён (γ={clip_limit}, сетка={grid_size}). Результат: {output_path}")

    return equalized_img, img_array, equalized_array

def clahe_color(image_path, clip_limit=2.0, grid_size=(8, 8), output_path=None):
    img = Image.open(image_path).convert('RGB')
    rgb_array = np.array(img, dtype=np.uint8)

    # Конвертация RGB -> LAB
    # Используем линейное приближение для учебных целей
    R, G, B = rgb_array[:, :, 0], rgb_array[:, :, 1], rgb_array[:, :, 2]

    # Приближённое преобразование RGB -> LAB
    L = 0.299 * R + 0.587 * G + 0.114 * B

    # Применяем CLAHE только к каналу яркости
    L_uint8 = np.clip(L, 0, 255).astype(np.uint8)
    L_equalized = apply_clahe_channel(L_uint8, clip_limit, grid_size).astype(np.float32)

    # Масштабируем цветовые каналы относительно изменения яркости
    # Сохраняем соотношение цветов: (R/G/B) / L = const
    epsilon = 1e-5
    R_out = np.where(L > epsilon, R * (L_equalized / (L + epsilon)), R)
    G_out = np.where(L > epsilon, G * (L_equalized / (L + epsilon)), G)
    B_out = np.where(L > epsilon, B * (L_equalized / (L + epsilon)), B)

    # Ограничиваем диапазон
    R_out = np.clip(R_out, 0, 255).astype(np.uint8)
    G_out = np.clip(G_out, 0, 255).astype(np.uint8)
    B_out = np.clip(B_out, 0, 255).astype(np.uint8)

    equalized_array = np.stack([R_out, G_out, B_out], axis=2)
    equalized_img = Image.fromarray(equalized_array, mode='RGB')

    if output_path:
        equalized_img.save(output_path)
        print(f"Цветное CLAHE применено (γ={clip_limit}, сетка={grid_size}). Результат: {output_path}")

    return equalized_img, rgb_array, equalized_array

def plot_comparison(original, clahe_result, output_path, title="CLAHE Сравнение"):
    fig, axes = plt.subplots(2, 2, figsize=(14, 12))
    fig.suptitle(title, fontsize=16, fontweight='bold')

    if original.ndim == 2:
        axes[0, 0].imshow(original, cmap='gray')
    else:
        axes[0, 0].imshow(original)
    axes[0, 0].set_title('Оригинал', fontsize=13, fontweight='bold')
    axes[0, 0].axis('off')

    if clahe_result.ndim == 2:
        axes[0, 1].imshow(clahe_result, cmap='gray')
    else:
        axes[0, 1].imshow(clahe_result)
    axes[0, 1].set_title('После CLAHE', fontsize=13, fontweight='bold')
    axes[0, 1].axis('off')

    # Гистограмма оригинала
    if original.ndim == 2:
        gray_orig = original
    else:
        gray_orig = (0.299 * original[:, :, 0] + 0.587 * original[:, :, 1] + 0.114 * original[:, :, 2]).astype(np.uint8)

    hist_orig, _ = np.histogram(gray_orig, bins=256, range=(0, 256))
    axes[1, 0].bar(range(256), hist_orig, color='steelblue', width=1.0)
    axes[1, 0].set_title('Гистограмма (оригинал)', fontsize=12)
    axes[1, 0].set_xlabel('Яркость')
    axes[1, 0].set_ylabel('Пиксели')
    axes[1, 0].grid(True, alpha=0.3)

    if clahe_result.ndim == 2:
        gray_clahe = clahe_result
    else:
        gray_clahe = (0.299 * clahe_result[:, :, 0] + 0.587 * clahe_result[:, :, 1] + 0.114 * clahe_result[:, :, 2]).astype(np.uint8)

    hist_clahe, _ = np.histogram(gray_clahe, bins=256, range=(0, 256))
    axes[1, 1].bar(range(256), hist_clahe, color='coral', width=1.0)
    axes[1, 1].set_title('Гистограмма (после CLAHE)', fontsize=12)
    axes[1, 1].set_xlabel('Яркость')
    axes[1, 1].set_ylabel('Пиксели')
    axes[1, 1].grid(True, alpha=0.3)

    plt.tight_layout(rect=[0, 0.03, 1, 0.95])
    plt.savefig(output_path, dpi=150)
    plt.show()


if __name__ == "__main__":
    from PIL import Image, ImageDraw

    def create_test_image(path, width=512, height=512):
        img = Image.new('L', (width, height), 128)
        draw = ImageDraw.Draw(img)

        for x in range(0, width//3):
            shade = 30 + (x % 40) * 2
            draw.rectangle([x, 0, x+1, height//2], fill=shade)

        for x in range(width//3, 2*width//3):
            shade = 180 + (x % 30) * 2
            draw.rectangle([x, 0, x+1, height//2], fill=shade)

        for x in range(2*width//3, width):
            shade = 80 + int((x - 2*width//3) * 100 / (width//3))
            draw.rectangle([x, 0, x+1, height//2], fill=shade)

        for y in range(height//2, height):
            for x in range(width):
                base = 100
                noise = ((x * 17 + y * 23) % 15) - 7  # псевдошум
                draw.point((x, y), fill=base + noise)

        img.save(path)
        print(f"Тестовое изображение создано: {path}")
        return img

    test_img = create_test_image(BASE_DIR / "clahe_test_input.png")

    from PIL import ImageOps
    histeq_img = ImageOps.equalize(test_img)
    histeq_img.save(BASE_DIR / "clahe_test_histeq.png")

    print("\nОбработка CLAHE с разными параметрами...")

    # Вариант 1: умеренное ограничение контраста
    clahe1, orig_arr, res_arr1 = clahe_grayscale(
        BASE_DIR / "clahe_test_input.png",
        clip_limit=2.0,
        grid_size=(8, 8),
        output_path=BASE_DIR / "clahe_result_2.0_8x8.png"
    )

    # Вариант 2: сильное ограничение (меньше шума)
    clahe2, _, res_arr2 = clahe_grayscale(
        BASE_DIR / "clahe_test_input.png",
        clip_limit=1.0,
        grid_size=(8, 8),
        output_path=BASE_DIR / "clahe_result_1.0_8x8.png"
    )

    # Вариант 3: крупная сетка (меньше адаптивности)
    clahe3, _, res_arr3 = clahe_grayscale(
        BASE_DIR / "clahe_test_input.png",
        clip_limit=2.0,
        grid_size=(4, 4),
        output_path=BASE_DIR / "clahe_result_2.0_4x4.png"
    )

    print("\nПостроение сравнительных гистограмм...")
    plot_comparison(orig_arr, res_arr1, BASE_DIR / "clahe_comparison_2_88.png", title="CLAHE: clip_limit=2.0, сетка 8X8")
    plot_comparison(orig_arr, res_arr2, BASE_DIR / "clahe_comparison_1_88.png", title="CLAHE: clip_limit=1.0, сетка 8X8")
    plot_comparison(orig_arr, res_arr3, BASE_DIR / "clahe_comparison_2_44.png", title="CLAHE: clip_limit=2.0, сетка 4x4")

    print("\nОбработка завершена!")
    print("\nРекомендации по параметрам CLAHE:")
    print("  • clip_limit = 1.0–2.0: для изображений с шумом (меньше артефактов)")
    print("  • clip_limit = 3.0–4.0: для чистых изображений (максимальный контраст)")
    print("  • grid_size = (8,8): баланс между локальной адаптацией и скоростью")
    print("  • grid_size = (4,4): для крупных объектов, меньше артефактов на границах")
