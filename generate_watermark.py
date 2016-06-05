import os
import Image

def main():
  Image.frombytes('1', (2592, 1944), os.urandom(1944 * 2592 / 8))\
      .save("watermark.bmp")

main()
