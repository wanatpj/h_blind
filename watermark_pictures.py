import Image
import numpy as np
import os
from multiprocessing import Pool

def size_filter(f):
  global watermark_image, watermark
  image = Image.open("photos/" + f)
  return image.size == watermark_image.size
  
def watermark_content(f):
  global watermark_image, watermark, width, height
  image = Image.open("photos/" + f).convert("L")
  img = image.load()
  for x, y in np.ndindex(image.size):
    # img[x, y] = tuple(map(lambda z: z + watermark[x][y], img[x, y]))
    img[x, y] = max(0, min(255, img[x, y] + watermark[x + y*width]))
  image.save("watermarked/" + f.split(".")[0] + ".bmp")
  

def main():
  global watermark_image, watermark, width, height
  watermark_image = Image.open("watermark.bmp")
  watermark = [1 if y == 0 else -1 for y in watermark_image.getdata()]
  width, height = watermark_image.size
  pool = Pool(10)
  pool.map(watermark_content, filter(size_filter, os.listdir("photos")))  # map as execute

main()
