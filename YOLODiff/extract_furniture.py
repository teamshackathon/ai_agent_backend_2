import cv2
import os
import math
import numpy as np
from typing import List
from datetime import datetime
from tkinter import Tk, filedialog
from ultralytics import YOLO

def select_image():
  Tk().withdraw()  # Tkウィンドウ非表示
  img_path = filedialog.askopenfilename(title="画像を選択してください", filetypes=[("Image Files", "*.jpg *.png *.jpeg")])
  if not img_path:
    print("画像が選択されませんでした。")
    exit()
  return img_path

def make_dir(dir_name: str = "img"):
  timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
  base_dir = os.path.join(dir_name, timestamp)
  os.makedirs(os.path.join(base_dir, "original"), exist_ok=True)
  os.makedirs(os.path.join(base_dir, "mask"), exist_ok=True)
  os.makedirs(os.path.join(base_dir, "crop"), exist_ok=True)
  os.makedirs(os.path.join(base_dir, "inpaint"), exist_ok=True)
  return base_dir

def segment_image(img_path: str, model_name: str = "yolov8x-seg.pt"):
  model = YOLO(model_name)
  return model, model(img_path, task="segment")

def extract_furniture(img,mask,bb,width,height,base_dir,count_map,class_name):
  raw_mask = (mask * 255).astype(np.uint8)
  resized_mask = cv2.resize(raw_mask, (width, height), interpolation=cv2.INTER_NEAREST)

  x1, y1, x2, y2 = map(int, [max(0,math.floor(bb[0])), max(0,math.floor(bb[1])), min(width,math.ceil(bb[2])), min(height,math.ceil(bb[3]))])
  crop = img[y1:y2, x1:x2]
  if crop.size == 0:
    print(f"スキップ: 空のcrop領域（{class_name}_{index}）")
    return None
  _, crop_mask = cv2.threshold(resized_mask[y1:y2, x1:x2], 127, 255, cv2.THRESH_BINARY) # 安全用

  # 同じクラス名のカウントを保持
  count_map[class_name] = count_map.get(class_name, 0) + 1
  index = count_map[class_name]

  # RGBA画像を作成（αチャンネル＝マスク）
  if crop_mask.shape != crop.shape[:2]:
    h, w = crop.shape[:2]
    crop_mask = cv2.resize(crop_mask, (w, h), interpolation=cv2.INTER_NEAREST)

  # 3チャンネル → 4チャンネルに変換（透明背景）
  rgba = cv2.merge((crop, crop_mask))  # (B, G, R, A)

  # ファイル名にクラス名を含める
  crop_path = os.path.join(base_dir, "crop", f"{class_name}_{index}.png")
  mask_path = os.path.join(base_dir, "mask", f"{class_name}_{index}_mask.png")

  cv2.imwrite(crop_path, rgba)         # 透過付きPNGで保存
  cv2.imwrite(mask_path, crop_mask)
  return f"{class_name}_{index}"

def extract_furnitures(model,results,img_path:str,base_dir:str,furniture_classes: List[str] = ['chair', 'dining_table', 'sofa', 'couch', 'bed', 'desk', 'table']):
  extract_names = []
  names = model.model.names
  result = results[0]
  masks = result.masks.data.cpu().numpy()
  boxes = result.boxes.data.cpu().numpy()
  classes = result.boxes.cls.cpu().numpy()
  img = cv2.imread(img_path)
  if img is None:
    raise ValueError(f"画像が読み込めませんでした: {img_path}")
  h, w = img.shape[:2]

  count_map = {}
  for i, cls_id in enumerate(classes):
    class_name = names[int(cls_id)].replace(" ", "_").lower() # 安全用
    if class_name not in furniture_classes:
      continue
    extract_name = extract_furniture(img,masks[i],boxes[i],w,h,base_dir,count_map,class_name)
    if extract_name:
      extract_names.append(extract_name)

  cv2.imwrite(os.path.join(base_dir, "original", os.path.basename(img_path)), img)
  print(f"\n✅ 保存完了: {base_dir}")
  return extract_names
