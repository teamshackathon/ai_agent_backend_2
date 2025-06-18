import torch
from diffusers import StableDiffusionInpaintPipeline
from PIL import Image

pipe = StableDiffusionInpaintPipeline.from_pretrained(
  "stabilityai/stable-diffusion-2-inpainting",
  torch_dtype=torch.float16,
  use_safetensors=True
).to("cuda")

def run_inpainting(img_path: str, mask_path: str, prompt: str):
  image = Image.open(img_path).convert("RGB")
  mask = Image.open(mask_path).convert("L")
  result = pipe(prompt=prompt, image=image, mask_image=mask).images[0]
  return result