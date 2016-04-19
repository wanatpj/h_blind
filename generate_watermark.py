import os
import Image

def main():
  Image.frombytes('1', (2592, 1944), os.urandom(1944 * 2592 / 8))\
      .save("watermark.bmp")
  #Image.frombytes('1', (20, 10), os.urandom(10 * 20 * 20 / 8))\
  #    .save("watermark.bmp")

main()
