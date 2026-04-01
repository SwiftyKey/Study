import cv2
import numpy as np

folderPath = r"c:\\users\\swifty\\downloads\\panorama"

images = []
for i in range(1, 4):
    img = cv2.imread(f"{folderPath}\\image_{i}.png")
    if img is not None:
        images.append(img)

sift = cv2.SIFT_create()

processed_images = []
colors = [(0, 0, 255), (0, 255, 0), (255, 0, 0)]

print("Поиск и отрисовка ключевых точек...")
for i, img in enumerate(images):
    keypoints, descriptors = sift.detectAndCompute(img, None)

    img_with_kp = img.copy()

    color = colors[i % len(colors)]
    cv2.drawKeypoints(img, keypoints, img_with_kp, color=color,
                      flags=cv2.DRAW_MATCHES_FLAGS_DRAW_RICH_KEYPOINTS)

    processed_images.append(img_with_kp)
    cv2.imwrite(f"{folderPath}\\image_with_landmark_{i+1}.png", img_with_kp)
    print(f"Изображение {i+1}: найдено {len(keypoints)} точек.")

stitcher = cv2.Stitcher.create(cv2.Stitcher_PANORAMA)
status, panorama = stitcher.stitch(images)

if status == cv2.Stitcher_OK:
    output_path = f"{folderPath}\\panorama_with_points.png"
    cv2.imwrite(output_path, panorama)
    print(f"Успех! Панорама с точками сохранена в: {output_path}")
    print("Цвета точек соответствуют разным исходным кадрам.")
else:
    print("Ошибка сшивки, код:", status)
