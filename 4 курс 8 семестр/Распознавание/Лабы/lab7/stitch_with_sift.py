import cv2
import numpy as np


def stitch_panorama_correctly(image_paths):

    images = [cv2.imread(path) for path in image_paths]
    images = [img for img in images if img is not None]

    sift = cv2.SIFT_create()

    result = images[0]

    for i in range(1, len(images)):
        gray1 = cv2.cvtColor(result, cv2.COLOR_BGR2GRAY)
        gray2 = cv2.cvtColor(images[i], cv2.COLOR_BGR2GRAY)

        kp1, des1 = sift.detectAndCompute(gray1, None)
        kp2, des2 = sift.detectAndCompute(gray2, None)

        matcher = cv2.BFMatcher()
        matches = matcher.knnMatch(des1, des2, k=2)

        good_matches = []
        for m, n in matches:
            if m.distance < 0.75 * n.distance:
                good_matches.append(m)

        print(f"Изображение {i}: найдено {len(good_matches)} совпадений")


        src_pts = np.float32([kp1[m.queryIdx].pt for m in good_matches]).reshape(-1, 1, 2)
        dst_pts = np.float32([kp2[m.trainIdx].pt for m in good_matches]).reshape(-1, 1, 2)

        H, mask = cv2.findHomography(dst_pts, src_pts, cv2.RANSAC, 5.0)

        h1, w1 = result.shape[:2]
        h2, w2 = images[i].shape[:2]

        corners = np.float32([
            [0, 0],
            [w2, 0],
            [w2, h2],
            [0, h2]
        ]).reshape(-1, 1, 2)

        transformed_corners = cv2.perspectiveTransform(corners, H)

        min_x = min(transformed_corners[:, 0, 0].min(), 0)
        max_x = max(transformed_corners[:, 0, 0].max(), w1)
        min_y = min(transformed_corners[:, 0, 1].min(), 0)
        max_y = max(transformed_corners[:, 0, 1].max(), h1)

        width = int(max_x - min_x)
        height = int(max_y - min_y)

        translation = np.array([[1, 0, -min_x], [0, 1, -min_y], [0, 0, 1]])
        H_shifted = translation @ H

        warped = cv2.warpPerspective(images[i], H_shifted, (width, height))

        result_new = np.zeros((height, width, 3), dtype=np.uint8)
        result_new[int(-min_y):int(-min_y + h1), int(-min_x):int(-min_x + w1)] = result

        mask1 = (result_new[:, :, 0] != 0) | (result_new[:, :, 1] != 0) | (result_new[:, :, 2] != 0)
        mask2 = (warped[:, :, 0] != 0) | (warped[:, :, 1] != 0) | (warped[:, :, 2] != 0)
        overlap = mask1 & mask2

        result_final = result_new.copy()
        result_final[mask2 & ~overlap] = warped[mask2 & ~overlap]

        if np.any(overlap):
            alpha = 0.5
            for y in range(height):
                for x in range(width):
                    if overlap[y, x]:
                        result_final[y, x] = (alpha * result_new[y, x] +
                                              (1 - alpha) * warped[y, x]).astype(np.uint8)

        result = result_final
        print(f"Изображение {i} добавлено. Размер: {result.shape[1]}x{result.shape[0]}")

    return result


def crop_black_borders(img):
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    coords = cv2.findNonZero(gray)
    x, y, w, h = cv2.boundingRect(coords)
    return img[y:y + h, x:x + w]


if __name__ == "__main__":
    image_paths = ['c:\\users\\swifty\\downloads\\panorama\\part_1.png', 'c:\\users\\swifty\\downloads\\panorama\\part_2.png', 'c:\\users\\swifty\\downloads\\panorama\\part_3.png']

    panorama = stitch_panorama_correctly(image_paths)

    if panorama is not None:
        panorama = crop_black_borders(panorama)

        cv2.imwrite('stitched_panorama_sift.jpg', panorama)
        print(f"\nПанорама сохранена: stitched_panorama_sift.jpg")
        print(f"Размер: {panorama.shape[1]}x{panorama.shape[0]}")

