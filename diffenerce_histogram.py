import Image
import matplotlib.pyplot as plt
import numpy
import operator
import os
from multiprocessing import Pool

def _prepare_reduction():
  global reduced
  reduced = []

def size_filter(f):
  global watermark_size
  with Image.open("photos2/" + f) as image:
    result = image.size == watermark_size
  return result

def _read_watermark():
  global watermark_size
  global watermark
  watermark_image = Image.open("watermark.bmp")
  watermark_size = watermark_image.size
  watermark = watermark_image.load()

def map_reduce(data, map_fn, reduce_fn):
  global reduced
  _prepare_reduction()
  pool = Pool(8)
  while data:
    reduced = reduce(\
        reduce_fn,\
        pool.map(map_fn, data[0 : 8]),\
        reduced)
    data = data[8 : ]
    print "Remaining elements for map-reduce: " + str(len(data))

def extract_differences(f):
  with Image.open("photos2/" + f) as image:
    width, height = image.size
    result = []
    img = image.convert("L").load()
    for x in range(width - 1):
      for y in range(height):
        result.append(img[x, y] - img[x + 1, y])
    for x in range(width):
      for y in range(height - 1):
        result.append(img[x, y] - img[x, y + 1])
  return result

def main():
  global reduced
  _read_watermark()
  files = os.listdir("photos2")
  files = filter(size_filter, files)
  print len(files)
  map_reduce(files,\
      extract_differences,\
      operator.add)
  print reduced.count(0)
  plt.hist(reduced, numpy.linspace(-40, 40, 80))
  plt.show()

main()
