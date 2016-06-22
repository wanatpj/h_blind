import numpy
from multiprocessing import cpu_count, Pool
from PIL import Image

class ImageSizeFilter:
  def __init__(self, size, indir):
    self.size = size
    self.indir = indir
  def __call__(self, f):
    with Image.open(self.indir + "/" + f) as image:
      return image.size == self.size

def get_pool():
  return Pool(cpu_count() + 2)

def get_watermark(f):
  watermark_image = Image.open(f)
  return watermark_image.size,\
      numpy.array([1 if y == 0 else -1 for y in watermark_image.getdata()])\
          .astype(numpy.int8)

def get_image_in_grayscale(f):
  with Image.open(f) as image:
    return numpy.array(image.convert("L").getdata()).astype(numpy.uint8)

def linear_correlation(a, b):
  N = a.size
  if N != b.size:
    raise Exception('VECTORS_WITH_DIFFERENT_LENGTH')
  correlation = 0.
  for i in range(N):
    correlation += a[i]*float(b[i])
  return correlation / float(N)

def map_reduce(data, map_fn, reduce_fn, reduced, chunk_size = 8, sync = False):
  while data.size != 0:
    mapped = map(map_fn, data[0 : chunk_size])\
        if sync else get_pool().map(map_fn, data[0 : chunk_size])
    reduced = reduce(\
        reduce_fn,\
        mapped,\
        reduced)
    data = data[chunk_size : ]
    print "Remaining elements for map-reduce: " + str(len(data))
  return reduced
