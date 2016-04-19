import Image
import itertools
import numpy
import operator
import os
import random
from matplotlib import pyplot
from multiprocessing import Pool
from pygraph.algorithms.minmax import maximum_flow
from pygraph.classes.digraph import digraph

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
  reduced = numpy.zeros((wwidth - 1, wheight)), numpy.zeros((wwidth, wheight - 1))

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

def comparator(pixel1, pixel2):
  return 1 if pixel1 < pixel2 else 0 if pixel1 == pixel2 else -1

def extract_inequalities(f):
  global watermark_size
  print "start"
  wwidth, wheight = watermark_size
  horizontal = numpy.zeros((wwidth - 1, wheight))
  vertical = numpy.zeros((wwidth, wheight - 1))
  print "open image"
  with Image.open("photos2/" + f) as image:
    print "image opened"
    loaded = image.convert("L").load()
    print "image loaded"
    width, height = image.size
    for x in range(width - 1):
      for y in range(height):
        horizontal[x][y] = comparator(loaded[x, y], loaded[x + 1, y])
    for x in range(width):
      for y in range(height - 1):
        vertical[x][y] = comparator(loaded[x, y], loaded[x, y + 1])
    print "image processed"
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

def get_id(x):
  if x == 1:
    return 0
  if x == -1:
    return 1

def get_id_(x, y):
  global watermark_size
  wwidth, wheight = watermark_size
  return 2 + x*wheight + y

def vertices():
  global watermark_size
  wwidth, wheight = watermark_size
  return range(2 + wwidth*wheight)

def build_graph(horizontal, vertical):
  global watermark_size
  global graph
  wwidth, wheight = watermark_size
  graph = digraph()
  graph.add_nodes(vertices())
  ones = {}
  mones = {}
  one = get_id(1)
  mone = get_id(-1)
  print "adding edges"
  for x in range(wwidth - 1):
    print x
    for y in range(wheight):
      i = get_id_(x, y)
      j = get_id_(x, y + 1)
      if horizontal[x][y] == 0:
        graph.add_edge((i, j))
        graph.add_edge((j, i))
      elif horizontal[x][y] == 1:
        ones[i] = ones[i] + 1 if i in ones else 1
        mones[j] = mones[j] + 1 if j in mones else 1
      elif horizontal[x][y] == -1:
        mones[i] = mones[i] + 1 if i in mones else 1
        ones[j] = ones[j] + 1 if j in ones else 1
      else:
        raise 'INCORRECT_REPRESENTATION'
  print len(ones)
  print len(mones)
  cnt = 0
  for key, value in ones.iteritems():
    graph.add_edge((one, key), wt=value)
    graph.add_edge((key, one), wt=value)
    cnt += 1
    if cnt % 1000 == 0:
      print cnt
  for key, value in mones.iteritems():
    graph.add_edge((key, mone), wt=value)
    graph.add_edge((mone, key), wt=value)

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
  bins = numpy.linspace(-2, 2, 200)
  pyplot.hist(hidden_watermark, bins, alpha=0.5, label='hw')
  pyplot.show()
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
  pool = Pool(8)
  _read_watermark()
  width, height = watermark_size
  files = os.listdir("photos2")
  files = filter(size_filter, files)
  print len(files)
  map_reduce(files,\
      extract_inequalities,\
      matadd)
  print "map reduce finished"
  horizontal, vertical = reduced
  divide_all(horizontal, float(len(files)))
  divide_all(vertical, float(len(files)))
  print "divide all finished"
  hori =\
      [horizontal[x][y] for y in range(height) for x in range(width - 1)]
  verti =\
      [vertical[x][y] for y in range(height - 1) for x in range(width)]
  bins = numpy.linspace(-2, 2, 200)
  pyplot.hist(hori, bins, alpha=0.5, label='hw')
  pyplot.show()
  bins = numpy.linspace(-2, 2, 200)
  pyplot.hist(verti, bins, alpha=0.5, label='hw')
  pyplot.show()
  horizontal = map(
      lambda x: map(lambda y: -1 if y < -0.3 else 0 if y <= 0.3 else 1, x),
      horizontal)
  vertical = map(
      lambda x: map(lambda y: -1 if y < -0.3 else 0 if y <= 0.3 else 1, x),
      vertical)
  reduced = horizontal, vertical
  iterations = 50000000
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
  #print "mapping finished"
  #build_graph(horizontal, vertical)
  #print "graph done"
  #sgn0 = maximum_flow(graph, get_id(1), get_id(-1))[1]
  #sgn1 = maximum_flow(graph, get_id(-1), get_id(1))[1]
  #guess_size = 0
  #wwidth, wheight = watermark_size
  #result = [0] * (wwidth * wheight)
  #for y in range(wheight):
  #  for x in range(wwidth):
  #    i = get_id_(x, y)
  #    if sgn0[i] != sgn1[i]:
  #      result[i] = 1 if sgn0[i] == 0 else -1
  #      guess_size += 1
  print len(filter(lambda x: x != 0, hidden_watermark)) / float(len(hidden_watermark))
  print linear_correlation(watermark, hidden_watermark)

main()
