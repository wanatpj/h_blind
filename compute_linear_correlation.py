import Image
import os
import numpy
from matplotlib import pyplot

from common import *

def _parse_flags():
  global indir, outdir, watermarkfile, usecuda
  parser = OptionParser()
  parser.add_option("-i",
      "--in",
      dest="indir",
      help="location to directory that containes images to watermark",
      metavar="DIR")
  parser.add_option("-w",
      "--watermark",
      dest="watermark",
      help="watermark file",
      metavar="FILE")
  parser.add_option("-c",
      "--usecuda",
      dest="usecuda",
      help="true iff should use gpu compiting (cuda)",
      metavar="FILE")
  (options, args) = parser.parse_args()
  indir = options.indir
  outdir = options.outdir
  watermarkfile = options.watermark
  usecuda = True\
      if options.usecuda != None and options.usecuda.lower()[0] == 't'\
      else False

def linear_correlation(a, b):
  N = len(a)
  if N != len(b):
    raise 'VECTORS_WITH_DIFFERENT_LENGTH'
  correlation = 0L
  for i in range(N):
    correlation += a[i]*b[i]
  return correlation / float(N)

def compute_lc(f):
  global width, height, watermark
  image = Image.open("watermarked/" + f)

class ComputeLinearCorrelation:
  def __init__(self, watermark):
    self.watermark = watermark
  def __call__(self, f):
    Image.open("watermarked/" + f)
    return linear_correlation(list(image.convert("L").getdata()), watermark)

def main():
  global width, height, watermark
  (width, height), watermark = get_watermark("watermark.bmp")
  lclist = get_pool().map(
      ComputeLinearCorrelation,
      filter(ImageSizeFilter(size), os.listdir("watermarked")))
  bins = numpy.linspace(-2, 2, 200)
  pyplot.hist(lclist, bins, alpha=0.5, label='lc')
  pyplot.show()

main()
