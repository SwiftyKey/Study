import cv2


folderPath = "c:\\users\\swifty\\downloads\\panorama"

images = [cv2.imread(f"{folderPath}\\image_{i}.png") for i in range(1, 4)]
stitcher = cv2.Stitcher.create(cv2.Stitcher_PANORAMA)
status, panorama = stitcher.stitch(images)

if status == cv2.Stitcher_OK:
    cv2.imwrite(f"{folderPath}\\panorama.png", panorama)
else:
    print("Ошибка сшивки, код:", status)
