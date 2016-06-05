import itertools
import numpy
import operator
import os
import random
from matplotlib import pyplot
from multiprocessing import Pool
from PIL import Image

def linear_correlation(a, b):
  N = len(a)
  if N != len(b):
    raise 'VECTORS_WITH_DIFFERENT_LENGTH'
  correlation = 0L
  for i in range(N):
    correlation += a[i]*b[i]
  return correlation / float(N)

def _read_watermark():
  global watermark_size
  global watermark
  watermark_image = Image.open("watermark.bmp")
  watermark_size = watermark_image.size
  watermark = [1 if x == 0 else -1 for x in watermark_image.getdata()]

def _prepare_reduction():
  global reduced
  global watermark_size
  wwidth, wheight = watermark_size
  return numpy.zeros((wwidth - 1, wheight)), numpy.zeros((wwidth, wheight - 1))

def map_reduce(data, map_fn, reduce_fn, reduced):
  while data:
    reduced = reduce(\
        reduce_fn,\
        map(map_fn, data[0 : 8]),\
        reduced)
    data = data[8 : ]
    print "Remaining elements for map-reduce: " + str(len(data))
  return reduced

def comparator(pixel1, pixel2):
  return 1 if pixel1 < pixel2 else 0 if pixel1 == pixel2 else -1

def extract_inequalities(f):
  with Image.open("photos2/" + f) as image:
    loaded = image.convert("L").load()
    width, height = image.size
    horizontal = numpy.zeros((width - 1, height))
    vertical = numpy.zeros((width, height - 1))
    for x in range(width - 1):
      for y in range(height):
        horizontal[x][y] = comparator(loaded[x, y], loaded[x + 1, y])
    for x in range(width):
      for y in range(height - 1):
        vertical[x][y] = comparator(loaded[x, y], loaded[x, y + 1])
    return horizontal, vertical

def size_filter(f):
  global watermark_size
  with Image.open("photos2/" + f) as image:
    result = image.size == watermark_size
  return result

def matadd(x, y):
  x1, x2 = x
  y1, y2 = y
  result1 = []
  for i in range(len(x1)):
    result1.append(map(operator.add, x1[i], y1[i]))
  result2 = []
  for i in range(len(x2)):
    result2.append(map(operator.add, x2[i], y2[i]))
  return result1, result2

def divide_all(m, d):
  for i in range(len(m)):
    for j in range(len(m[i])):
      m[i][j] /= d

def get_random_edge(width, height):
  if random.randint(0, 1) == 0:
    return { 'typ': 0, 'x': random.randint(0, width - 2), 'y': random.randint(0, height - 1) }
  else:
    return { 'typ': 1, 'x': random.randint(0, width - 1), 'y': random.randint(0, height - 2) }

def prepare(width, height):
  global hidden_watermark
  hidden_watermark = numpy.zeros((width, height))

def update(delta, x1, y1, x2, y2):
  global hidden_watermark
  _sum = hidden_watermark[x1][y1] + hidden_watermark[x2][y2]
  delta = min(delta, 2 - _sum)
  delta = min(delta, 2 + _sum)
  hidden_watermark[x1][y1] = (_sum - delta)/2.
  hidden_watermark[x2][y2] = (_sum + delta)/2.

def save_hidden_watermark():
  global hidden_watermark
  global watermark
  global watermark_size
  global reduced
  width, height = watermark_size
  hidden_watermark =\
      [hidden_watermark[x][y] for y in range(height) for x in range(width)]
  #bins = numpy.linspace(-2, 2, 200)
  #pyplot.hist(hidden_watermark, bins, alpha=0.5, label='hw')
  #pyplot.show()
  for i in range(width * height):
    hidden_watermark[i] = -1 if hidden_watermark[i] < 0 else\
        0 if hidden_watermark[i] == 0 else 1
  Image\
      .frombytes(\
          'RGB',
          (width, height),
          "".join(map(
              lambda x, y: 
                  chr(0)*3 if x == 1 else
                      chr(255)*3 if x == -1 else
                      chr(0) + chr(255) + chr(0) if y == -1 else
                      chr(0) + chr(0) + chr(255),
              hidden_watermark,
              watermark)))\
      .save("hidden_watermark.bmp")
  Image\
      .frombytes(\
          'RGB',
          (width, height),
          "".join(map(
              lambda x, y: 
                  chr(0)*3 if x == 0 else
                      chr(0) + chr(255) + chr(0) if x == y else
                      chr(255) + chr(0) + chr(0),
              hidden_watermark,
              watermark)))\
      .save("hidden_watermark-diff.bmp")
  horizontal, vertical = reduced
  
def main():
  global graph
  global reduced
  global watermark_size
  global watermark
  global hidden_watermark
  _read_watermark()
  width, height = watermark_size
  files = os.listdir("photos2")
  files = filter(size_filter, files)
  print len(files)
  horizontal, vertical = map_reduce(files,\
      extract_inequalities,\
      matadd,
      _prepare_reduction())
  divide_all(horizontal, float(len(files)))
  divide_all(vertical, float(len(files)))
  print "divide all finished"
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
  horizontal = map(
      lambda x: map(lambda y: -1 if y < -0.3 else 0 if y <= 0.3 else 1, x),
      horizontal)
  vertical = map(
      lambda x: map(lambda y: -1 if y < -0.3 else 0 if y <= 0.3 else 1, x),
      vertical)
  reduced = horizontal, vertical
  iterations = 5000
  wwidth, wheight = watermark_size
  prepare(wwidth, wheight)
  while iterations > 0:
    if not (iterations & 0b111111111111111111):
      print iterations
    edge = get_random_edge(wwidth, wheight)
    if edge['typ'] == 0:
      update(2*horizontal[edge['x']][edge['y']],\
          edge['x'],\
          edge['y'],\
          edge['x'] + 1,\
          edge['y'])
    else:
      update(2*vertical[edge['x']][edge['y']],\
          edge['x'],\
          edge['y'],\
          edge['x'],\
          edge['y'] + 1)
    iterations -= 1
  save_hidden_watermark()
  print len(filter(lambda x: x != 0, hidden_watermark)) / float(len(hidden_watermark))
  print linear_correlation(watermark, hidden_watermark)

main()
