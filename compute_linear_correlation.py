import os
import numpy
from matplotlib import pyplot
from optparse import OptionParser
from PIL import Image

from common import *

def _parse_flags():
  global indir, referencefile, usecuda
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
  parser.add_option("-c",
      "--usecuda",
      dest="usecuda",
      help="true iff should use gpu compiting (cuda)",
      metavar="FILE")
  (options, args) = parser.parse_args()
  indir = options.indir
  referencefile = options.reference
  usecuda = True\
      if options.usecuda != None and options.usecuda.lower()[0] == 't'\
      else False

class ComputeLinearCorrelation:
  def __init__(self, reference, indir):
    self.reference = reference
    self.indir = indir
  def __call__(self, f):
    return linear_correlation(
        numpy.array(Image.open(self.indir + "/" + f).convert("L").getdata()),
        self.reference)

class GPUComputeLinearCorrelation:
  def __init__(self, gpu_reference, indir):
    self.gpu_reference = gpu_reference
    self.indir = indir
  def __call__(self, f):
    global cudalib
    return cudalib.linear_correlation(
        numpy.array(Image.open(indir + "/" + f).convert("L").getdata()),
        self.gpu_reference)

def main():
  global indir, referencefile, usecuda
  _parse_flags()
  (width, height), reference = get_watermark(referencefile)
  if usecuda:
    global cudalib
    import cudalib
    lcs = map(
        GPUComputeLinearCorrelation(
            cudalib.prepare_gpuarray(reference),
            indir),
        filter(ImageSizeFilter((width, height), indir), os.listdir(indir)))
    print lcs
  else:
    lcs = get_pool().map(
        ComputeLinearCorrelation(reference, indir),
        filter(ImageSizeFilter((width, height), indir), os.listdir(indir)))
    print lcs
  print "Mean: " + str(numpy.mean(lcs))
  print "Median: " + str(numpy.median(lcs))
  print "Variance: " + str(numpy.var(lcs))
  bins = numpy.linspace(-2, 2, 200)
  pyplot.hist(lcs, bins, alpha=0.5, label='lc')
  pyplot.show()

main()
