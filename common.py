import numpy
from multiprocessing import cpu_count, Pool
from PIL import Image

class ImageSizeFilter:
  def __init__(self, size):
    self.size = size
  def __call__(self, f):
    image = Image.open("photos/" + f)
    return image.size == self.size

def get_pool():
  return Pool(cpu_count() + 2)

def get_watermark(f):
  watermark_image = Image.open(f)
  return watermark_image.size,\
      numpy.array([1 if y == 0 else -1 for y in watermark_image.getdata()])\
          .astype(numpy.int8)

