import numpy
import os
import random
from matplotlib import pyplot
from multiprocessing import Pool
from optparse import OptionParser
from PIL import Image
from scipy import misc

from common import *

def _prepare_reduction(size):
  wwidth, wheight = size
  return numpy.zeros((wwidth - 1, wheight)), numpy.zeros((wwidth, wheight - 1))

def delta(pixel1, pixel2):
  return 1 if pixel1 < pixel2 else 0 if pixel1 == pixel2 else -1

def extract_delta(f):
  with Image.open(f) as image:
    width, height = image.size
    loaded = numpy.transpose(
        numpy.array(image.convert("L").getdata())
            .reshape((height, width)))
    horizontal = numpy.zeros((width - 1, height))
    vertical = numpy.zeros((width, height - 1))
    for x in range(width - 1):
      for y in range(height):
        horizontal[x][y] = delta(loaded[x][y], loaded[x + 1][y])
    for x in range(width):
      for y in range(height - 1):
        vertical[x][y] = delta(loaded[x][y], loaded[x][y + 1])
    return horizontal, vertical

def matadd(x, y):
  h1, v1 = x
  h2, v2 = y
  return numpy.add(h1, h2), numpy.add(v1, v2)

def get_random_edge(size):
  width, height = size
  if random.randint(0, 1) == 0:
    return {
        'type': 0,
        'x': random.randint(0, width - 2),
        'y': random.randint(0, height - 1) }
  else:
    return {
        'type': 1,
        'x': random.randint(0, width - 1),
        'y': random.randint(0, height - 2) }

def update(watermark, delta, x1, y1, x2, y2):
  _sum = watermark[x1][y1] + watermark[x2][y2]
  delta = min(delta, 2 - _sum)
  delta = min(delta, 2 + _sum)
  delta = max(delta, -2 - _sum)
  delta = max(delta, -2 + _sum)
  watermark[x1][y1] = (_sum - delta)/2.
  watermark[x2][y2] = (_sum + delta)/2.

def _parse_flags():
  global watermarked, deduced, size, usecuda
  parser = OptionParser()
  parser.add_option("-i",
      "--watermarked",
      dest="watermarked",
      help="location to directory that containes potentialy watermarked "\
          + "images",
      metavar="DIR")
  parser.add_option("-o",
      "--deduced",
      dest="deduced",
      help="a file where to save watermarked images",
      metavar="FILE")
  parser.add_option("-s",
      "--size",
      dest="size",
      help="width x height, par example: 2592x1944",
      metavar="SIZE")
  parser.add_option("-c",
      "--usecuda",
      dest="usecuda",
      help="true iff should use gpu compiting (cuda)",
      metavar="true")
  (options, args) = parser.parse_args()
  watermarked = options.watermarked
  deduced = options.deduced
  size = tuple(map(lambda x: int(x), options.size.split('x')))
  usecuda = True\
      if options.usecuda != None and options.usecuda.lower()[0] == 't'\
      else False

def deduce_edge_model(files, size):
  horizontal, vertical =\
      map_reduce(files, extract_delta, matadd, _prepare_reduction(size))
  numpy.divide(horizontal, float(len(files)))
  numpy.divide(vertical, float(len(files)))
  guess_edge_fn = numpy.vectorize(
      lambda x: -1 if x < -0.3 else 0 if x <= 0.3 else 1)
  horizontal = guess_edge_fn(horizontal)
  vertical = guess_edge_fn(vertical)
  return horizontal, vertical

def deduce_watermark(size, edge_model):
  width, height = size
  watermark = numpy.zeros(size)
  horizontal, vertical = edge_model
  iterations = 10 * width * height
  while iterations > 0:
    if not (iterations & 0b111111111111111111):
      print iterations
    edge = get_random_edge(size)
    if edge['type'] == 0:
      update(watermark,
          2*horizontal[edge['x']][edge['y']],\
          edge['x'],\
          edge['y'],\
          edge['x'] + 1,\
          edge['y'])
    else:
      update(watermark,
          2*vertical[edge['x']][edge['y']],\
          edge['x'],\
          edge['y'],\
          edge['x'],\
          edge['y'] + 1)
    iterations -= 1
  return numpy\
      .array([watermark[x][y] for y in range(height) for x in range(width)])

def save_hidden_watermark(hidden_watermark):
  global deduced, size
  width, height = size
  hidden_watermark_stream =\
      [chr(255) if val < 0 else chr(0) for val in hidden_watermark]
  Image.frombytes('L', (width, height), "".join(hidden_watermark_stream))\
      .convert('1')\
      .save(deduced)

def main():
  global watermarked, deduced, size, usecuda
  _parse_flags()
  files = filter(
      ImageSizeFilter(size, watermarked),
      os.listdir(watermarked))
  make_exact_path_fn = numpy.vectorize(lambda x: watermarked + "/" + x)
  files = make_exact_path_fn(files)
  if usecuda:
    import cudalib
    hidden_watermark = cudalib.deduce_watermark(size, files)
  else:
    edge_model = deduce_edge_model(files, size)
    hidden_watermark = deduce_watermark(size, edge_model)
  width, height = size
  
  #hori =\
  #    [horizontal[x][y] for y in range(height) for x in range(width - 1)]
  #verti =\
  #    [vertical[x][y] for y in range(height - 1) for x in range(width)]
  #bins = numpy.linspace(-2, 2, 200)
  #pyplot.hist(hori, bins, alpha=0.5, label='hw')
  #pyplot.show()
  #bins = numpy.linspace(-2, 2, 200)
  #pyplot.hist(verti, bins, alpha=0.5, label='hw')
  #pyplot.show()
  save_hidden_watermark(hidden_watermark)

main()
