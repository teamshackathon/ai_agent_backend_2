import os
from string import digits

import cv2
import extract_furniture as ef
from inpainting import run_inpainting
from mask_utils import clean_mask

FURNITURES = [
    'chair', 'couch', 'bed', 'dining_table',
    'tv', 'laptop', 'keyboard', 'refrigerator',
    'oven', 'toaster', 'sink', 'potted_plant', 'vase'
]

def yolodiff():
  img_path = ef.select_image()
  base_dir = ef.make_dir()
  model, results = ef.segment_image(img_path)
  extract_names = ef.extract_furnitures(model,results,img_path,base_dir,FURNITURES)
  for name in extract_names:
    crop_path = os.path.join(base_dir, "crop", f"{name}.png")
    mask_path = os.path.join(base_dir, "mask", f"{name}_mask.png")

    clean = clean_mask(mask_path)
    # clean = cv2.bitwise_not(clean_mask(mask_path))
    clean_path = os.path.join(base_dir, "mask", f"{name}_cleaned_mask.png")
    cv2.imwrite(clean_path, clean)

    prompt = (
      f"a clean, a realistic {name.replace('_', ' ').translate(str.maketrans('', '', digits))} with complete structure, no items on top, isolated, "
      "perfectly symmetrical, realistic lighting, studio shot"
    )
    output = run_inpainting(crop_path, mask_path, prompt)
    output.save(os.path.join(base_dir, "inpaint", f"{name}_inpainted.png"))
  return extract_names

if __name__ == "__main__":
  result = yolodiff()
  print("抽出された家具:", result)