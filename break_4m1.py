import cv2
import Image
import numpy
import operator
import os
from multiprocessing import Pool
from scipy import ndimage

def explore_efficiency(f):
  image = cv2.imread("w1/" + f, 0)
  print image
  edge_kernel = numpy.array([[0, -1, 0], [-1, 4, -1], [0, -1, 0]])
  result = ndimage.convolve(image, edge_kernel)
  return [
      1 if result[x][y] > 0 else (-1 if result[x][y] < 0 else 0)
      for y in range(len(result[0]))
      for x in range(len(result))
  ]

def main():
  watermark = [1 if x == 0 else -1 for x in Image.open("watermark.bmp").getdata()]
  files = os.listdir("w1")
  reduced = [0] * len(watermark)
  pool = Pool(8)
  while files:
    reduced = reduce(\
        lambda x, y: map(operator.add, x, y),\
        pool.map(explore_efficiency, files[0 : 8]),\
        reduced)
    files = files[8 : ]
  solution = [1 if x > 0 else -1 for x in reduced]
  # print solution
  print len(watermark)
  print len(solution)
  print sum([1 if solution[i] == watermark[i] else 0 for i in range(len(watermark))]) / float(len(solution))

main()
