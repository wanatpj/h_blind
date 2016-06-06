import numpy
from multiprocessing import cpu_count, Pool
from PIL import Image

class ImageSizeFilter:
  def __init__(self, size, indir):
    self.size = size
    self.indir = indir
  def __call__(self, f):
    image = Image.open(self.indir + "/" + f)
    return image.size == self.size

def get_pool():
  return Pool(cpu_count() + 2)

def get_watermark(f):
  watermark_image = Image.open(f)
  return watermark_image.size,\
      numpy.array([1 if y == 0 else -1 for y in watermark_image.getdata()])\
          .astype(numpy.int8)

def linear_correlation(a, b):
  a = numpy.array(a)
  b = numpy.array(b)
  N = a.size
  if N != b.size:
    raise Exception('VECTORS_WITH_DIFFERENT_LENGTH')
  correlation = 0L
  for i in range(N):
    correlation += a[i]*long(b[i])
  return correlation / float(N)
