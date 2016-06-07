import os
from optparse import OptionParser
from PIL import Image

def _parse_flags():
  global out
  parser = OptionParser()
  parser.add_option("-o",
      "--out",
      dest="out",
      help="a file name without extension where to save the new watermark",
      metavar="FILE")
  (options, args) = parser.parse_args()
  out = options.out

def main():
  global out
  _parse_flags()
  Image.frombytes('1', (2592, 1944), os.urandom(1944 * 2592 / 8))\
      .save(out + ".bmp")

main()
