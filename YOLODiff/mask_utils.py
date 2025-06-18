import cv2
import numpy as np


def clean_mask(mask_path):
  mask = cv2.imread(mask_path, cv2.IMREAD_GRAYSCALE)

  # 1. 小さな穴を閉じる
  kernel = np.ones((7, 7), np.uint8)
  closed = cv2.morphologyEx(mask, cv2.MORPH_CLOSE, kernel)

  # 2. スムージング
  smoothed = cv2.GaussianBlur(closed, (5, 5), 0)

  # 3. 再2値化
  _, binary = cv2.threshold(smoothed, 127, 255, cv2.THRESH_BINARY)

  return binary