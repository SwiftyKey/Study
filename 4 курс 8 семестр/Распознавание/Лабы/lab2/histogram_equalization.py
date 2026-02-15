from PIL import Image
import numpy as np
import matplotlib.pyplot as plt
import os
from pathlib import Path

BASE_DIR = Path(os.path.dirname(os.path.abspath(__file__)))

def compute_histogram(image_array):
    image_array = np.clip(image_array, 0, 255).astype(np.uint8)
    histogram = [0] * 256
    for pixel in image_array.flat:
        histogram[pixel] += 1
    return histogram

def compute_cdf(histogram):
    cdf = [0] * 256
    cumulative = 0
    for i in range(256):
        cumulative += histogram[i]
        cdf[i] = cumulative
    return cdf

def equalize_channel(channel_array):
    hist = compute_histogram(channel_array)

    cdf = compute_cdf(hist)

    cdf_min = next((v for v in cdf if v > 0), 0)

    total_pixels = channel_array.size

    lookup_table = [0] * 256
    for i in range(256):
        if total_pixels == cdf_min:
            lookup_table[i] = i
        else:
            lookup_table[i] = int(round(((cdf[i] - cdf_min) / (total_pixels - cdf_min)) * 255))
            lookup_table[i] = max(0, min(255, lookup_table[i]))

    equalized = np.array([lookup_table[pixel] for pixel in channel_array.flat], dtype=np.uint8)
    equalized = equalized.reshape(channel_array.shape)

    return equalized

def histogram_equalization_grayscale(image_path, output_path=None):
    img = Image.open(image_path).convert('L')
    img_array = np.array(img, dtype=np.uint8)

    equalized_array = equalize_channel(img_array)

    equalized_img = Image.fromarray(equalized_array.astype(np.uint8))

    if output_path:
        equalized_img.save(output_path)
        print(f"Выровненное изображение сохранено: {output_path}")

    return equalized_img, img_array, equalized_array

def histogram_equalization_color(image_path, output_path=None):
    img = Image.open(image_path).convert('RGB')
    img_array = np.array(img, dtype=np.uint8)

    R, G, B = img_array[:, :, 0], img_array[:, :, 1], img_array[:, :, 2]

    Y = 0.299 * R + 0.587 * G + 0.114 * B
    Cb = 128 - 0.168736 * R - 0.331264 * G + 0.5 * B
    Cr = 128 + 0.5 * R - 0.418688 * G - 0.081312 * B

    Y_equalized = equalize_channel(Y.astype(np.uint8))

    R_out = Y_equalized + 1.402 * (Cr - 128)
    G_out = Y_equalized - 0.344136 * (Cb - 128) - 0.714136 * (Cr - 128)
    B_out = Y_equalized + 1.772 * (Cb - 128)

    R_out = np.clip(R_out, 0, 255).astype(np.uint8)
    G_out = np.clip(G_out, 0, 255).astype(np.uint8)
    B_out = np.clip(B_out, 0, 255).astype(np.uint8)

    equalized_array = np.stack([R_out, G_out, B_out], axis=2)

    equalized_img = Image.fromarray(equalized_array)

    if output_path:
        equalized_img.save(output_path)
        print(f"Выровненное цветное изображение сохранено: {output_path}")

    return equalized_img, img_array, equalized_array


def plot_histograms(original_array, equalized_array, title_prefix=""):
    fig, axes = plt.subplots(2, 2, figsize=(14, 10))

    if original_array.ndim == 2:
        axes[0, 0].imshow(original_array, cmap='gray')
        axes[0, 0].set_title(f'{title_prefix}Оригинал', fontsize=12, fontweight='bold')
    else:
        axes[0, 0].imshow(original_array)
        axes[0, 0].set_title(f'{title_prefix}Оригинал', fontsize=12, fontweight='bold')
    axes[0, 0].axis('off')

    if equalized_array.ndim == 2:
        axes[0, 1].imshow(equalized_array, cmap='gray')
        axes[0, 1].set_title(f'{title_prefix}После выравнивания', fontsize=12, fontweight='bold')
    else:
        axes[0, 1].imshow(equalized_array)
        axes[0, 1].set_title(f'{title_prefix}После выравнивания', fontsize=12, fontweight='bold')
    axes[0, 1].axis('off')

    hist_orig = compute_histogram(original_array if original_array.ndim == 2
                                  else original_array[:, :, 0] * 0.299 +
                                       original_array[:, :, 1] * 0.587 +
                                       original_array[:, :, 2] * 0.114)
    axes[1, 0].bar(range(256), hist_orig, color='steelblue', width=1.0)
    axes[1, 0].set_title('Гистограмма (оригинал)', fontsize=11)
    axes[1, 0].set_xlabel('Яркость')
    axes[1, 0].set_ylabel('Количество пикселей')
    axes[1, 0].grid(True, alpha=0.3)

    hist_eq = compute_histogram(equalized_array if equalized_array.ndim == 2
                                else equalized_array[:, :, 0] * 0.299 +
                                     equalized_array[:, :, 1] * 0.587 +
                                     equalized_array[:, :, 2] * 0.114)
    axes[1, 1].bar(range(256), hist_eq, color='coral', width=1.0)
    axes[1, 1].set_title('Гистограмма (после выравнивания)', fontsize=11)
    axes[1, 1].set_xlabel('Яркость')
    axes[1, 1].set_ylabel('Количество пикселей')
    axes[1, 1].grid(True, alpha=0.3)

    plt.tight_layout()
    plt.savefig(f"histogram_comparison_{title_prefix.lower().strip()}.png", dpi=150)
    plt.show()

if __name__ == "__main__":
    from PIL import Image, ImageDraw

    test_img = Image.new('L', (400, 300), 100)
    draw = ImageDraw.Draw(test_img)
    for i in range(10):
        shade = 70 + i * 6
        draw.rectangle([i*40, 0, (i+1)*40, 300], fill=shade)
    test_img.save(BASE_DIR / "low_contrast_test.png")

    eq_img, orig_arr, eq_arr = histogram_equalization_grayscale(
        BASE_DIR / "low_contrast_test.png",
        BASE_DIR / "equalized_result.png"
    )

    eq_img_color, orig_arr_color, eq_arr_color = histogram_equalization_color(
        BASE_DIR / "input.png",
        BASE_DIR / "equalized_input.png"
    )

    plot_histograms(orig_arr, eq_arr, title_prefix="Тестовое изображение: ")
    plot_histograms(orig_arr_color, eq_arr_color, title_prefix="Цветное изображение: ")

    print("\nВыравнивание гистограммы выполнено!")
