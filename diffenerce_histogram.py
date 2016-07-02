import Image
import matplotlib.pyplot as plt
import numpy
import os
from optparse import OptionParser

from common import *

def _parse_flags():
  global indir, rangeradius
  parser = OptionParser()
  parser.add_option("-i",
      "--in",
      dest="indir",
      help="directory that containes images for which the difference histogram"\
          + " will be computed",
      metavar="DIR")
  parser.add_option("-r",
      "--rangeradius",
      dest="rangeradius",
      help="range of the histogram",
      metavar="NUMBER")
  (options, args) = parser.parse_args()
  if not options.indir or not options.rangeradius:
    parser.error('Not all flags specified; run with --help to see the flags;')
  indir = options.indir
  rangeradius = int(options.rangeradius)

def extract_differences(f):
  with Image.open(f) as image:
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

def histogram_reduce(histogram, values):
  for value in values:
    histogram[value + 255] += 1
  return histogram

def main():
  global indir, rangeradius
  _parse_flags()
  normalize_file_names_fn = numpy.vectorize(lambda x: indir + "/" + x)
  result = map_reduce(normalize_file_names_fn(os.listdir(indir)),\
      extract_differences,\
      histogram_reduce,
      numpy.zeros(256 + 255, dtype=numpy.uint64))
  plt.bar(numpy.arange(-rangeradius, rangeradius + 1),
      result[255 - rangeradius : 255 + rangeradius + 1],
      align='center')
  plt.show()

main()
