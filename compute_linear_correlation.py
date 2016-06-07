import os
import numpy
from matplotlib import pyplot
from optparse import OptionParser
from PIL import Image

from common import *

def _parse_flags():
  global indir, referencefile
  parser = OptionParser()
  parser.add_option("-i",
      "--in",
      dest="indir",
      help="location to directory that containes images to watermark",
      metavar="DIR")
  parser.add_option("-w",
      "--reference",
      dest="reference",
      help="monochrome image; black pixel denotes 1, white pixel denotes -1",
      metavar="FILE")
  (options, args) = parser.parse_args()
  indir = options.indir
  referencefile = options.reference

class ComputeLinearCorrelation:
  def __init__(self, reference, indir):
    self.reference = reference
    self.indir = indir
  def __call__(self, f):
    return linear_correlation(
        numpy.array(Image.open(self.indir + "/" + f).convert("L").getdata()),
        self.reference)

def main():
  global indir, referencefile
  _parse_flags()
  (width, height), reference = get_watermark(referencefile)
  lcs = get_pool().map(
      ComputeLinearCorrelation(reference, indir),
      filter(ImageSizeFilter((width, height), indir), os.listdir(indir)))
  print "Mean: " + str(numpy.mean(lcs))
  print "Median: " + str(numpy.median(lcs))
  print "Variance: " + str(numpy.var(lcs))
  bins = numpy.linspace(-2, 2, 200)
  pyplot.hist(lcs, bins, alpha=0.5, label='lc')
  pyplot.show()

main()
