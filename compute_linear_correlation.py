import Image
import os
import numpy
from matplotlib import pyplot
from multiprocessing import Pool

def linear_correlation(a, b):
  N = len(a)
  if N != len(b):
    raise 'VECTORS_WITH_DIFFERENT_LENGTH'
  correlation = 0L
  for i in range(N):
    correlation += a[i]*b[i]
  return correlation / float(N)

def compute_lc(f):
  global watermark_image, watermark
  image = Image.open("watermarked/" + f)
  return linear_correlation(list(image.convert("L").getdata()), watermark), f

def size_filter(f):
  global watermark_image, watermark
  image = Image.open("watermarked/" + f)
  return image.size == watermark_image.size
  

def main():
  global watermark_image, watermark
  watermark_image = Image.open("watermark.bmp")
  watermark = [1 if pixel == 0 else -1 for pixel in watermark_image.getdata()]
  pool = Pool(10)
  lclist = pool.map(compute_lc, filter(size_filter, os.listdir("watermarked")))
  lclist = sorted(lclist)
  print lclist
  lclist = map(lambda x: x[0], lclist)
  
  bins = numpy.linspace(-2, 2, 200)
  pyplot.hist(lclist, bins, alpha=0.5, label='lc')
  pyplot.show()

main()
