import numpy as np
import os
from optparse import OptionParser
from PIL import Image

from common import ImageSizeFilter, get_pool, get_watermark

def _parse_flags():
  global indir, outdir, watermarkfile, alpha, usecuda
  parser = OptionParser()
  parser.add_option("-i",
      "--in",
      dest="indir",
      help="location to directory that containes images to watermark",
      metavar="DIR")
  parser.add_option("-o",
      "--out",
      dest="outdir",
      help="location to directory where to save watermarked images",
      metavar="DIR")
  parser.add_option("-w",
      "--watermark",
      dest="watermark",
      help="watermark file",
      metavar="FILE")
  parser.add_option("-a",
      "--alpha",
      dest="alpha",
      help="magnitude multiplier for watermark, by default = 1",
      metavar="INTEGER")
  parser.add_option("-c",
      "--usecuda",
      dest="usecuda",
      help="true iff should use gpu compiting (cuda)",
      metavar="true")
  (options, args) = parser.parse_args()
  indir = options.indir
  outdir = options.outdir
  watermarkfile = options.watermark
  alpha = 1 if options.alpha == None else int(options.alpha)
  usecuda = True\
      if options.usecuda != None and options.usecuda.lower()[0] == 't'\
      else False

def bounded(val):
  return min(255, max(0, val))

class WatermarkContentExecutor:
  def __init__(self, width, height, watermark, alpha, indir, outdir):
    self.width = width
    self.height = height
    self.watermark = watermark
    self.alpha = alpha
    self.indir = indir
    self.outdir = outdir
  def __call__(self, f):
    infile = self.indir + "/" + f
    outfile = self.outdir + "/" + f.split(".")[0] + ".bmp"
    image = Image.open(infile)
    img = image.load()
    for x, y in np.ndindex((self.width, self.height)):
      img[x, y] = tuple(map(\
          lambda z: bounded(z + self.alpha * self.watermark[x + y*self.width]),\
          img[x, y]))
    image.save(outfile)

class GpuWatermarkContentExecutor:
  def __init__(self, gpu_watermark, indir, outdir):
    self.gpu_watermark = gpu_watermark
    self.indir = indir
    self.outdir = outdir
  def __call__(self, f):
    global cudalib
    infile = self.indir + "/" + f
    outfile = self.outdir + "/" + f.split(".")[0] + ".bmp"
    cudalib.watermark_content(infile, outfile, self.gpu_watermark)

def main():
  global indir, outdir, watermarkfile, alpha, usecuda
  _parse_flags()
  (width, height), watermark = get_watermark(watermarkfile)
  images_to_map = filter(
      ImageSizeFilter((width, height), indir),
      os.listdir(indir))
  if usecuda:
    global cudalib
    import cudalib
    if alpha != 1:
      # TODO: make it work
      raise Exception("No support for cuda watermarking with alpha != 1")
    map(GpuWatermarkContentExecutor(
        cudalib.prepare_gpu_array(watermark),
        indir,
        outdir), images_to_map)
  else:
    get_pool().map(
        WatermarkContentExecutor(
            width,
            height,
            watermark,
            alpha,
            indir,
            outdir),
        images_to_map)

main()
