import os
import numpy
from matplotlib import pyplot
from optparse import OptionParser
from PIL import Image

from common import *

def _parse_flags():
  global indir, inreferencefile, referencefile, versuswatermark
  parser = OptionParser()
  parser.add_option("-i",
      "--in",
      dest="indir",
      help="location to directory that containes images to watermark",
      metavar="DIR")
  parser.add_option("-v",
      "--inreference",
      dest="inreference",
      help="monochrome image; black pixel denotes 1, white pixel denotes -1",
      metavar="FILE")
  parser.add_option("-w",
      "--reference",
      dest="reference",
      help="monochrome image; black pixel denotes 1, white pixel denotes -1",
      metavar="FILE")
  (options, args) = parser.parse_args()
  if (options.indir != None and options.inreference != None) \
      or (options.indir == None and options.inreference == None):
    raise Exception("define: indir xor inreference")
  if options.indir != None:
    indir = options.indir
    versuswatermark = False
  elif options.inreference != None:
    inreferencefile = options.inreference
    versuswatermark = True
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
  global indir, inreferencefile, referencefile, versuswatermark
  _parse_flags()
  (width, height), reference = get_watermark(referencefile)
  if versuswatermark:
    (inwidth, inheight), inreference = get_watermark(inreferencefile)
    lcs = [linear_correlation(reference, inreference)]
  else:
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
