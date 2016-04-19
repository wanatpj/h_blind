import Image
import operator
import numpy as np

f = "2016-02-12 16:11:16.jpg"

def linear_correlation(a, b):
  N = len(a)
  if N != len(b):
    raise 'VECTORS_WITH_DIFFERENT_LENGTH'
  correlation = 0L
  for i in range(N):
    correlation += a[i]*b[i]
  return correlation / float(N)
  
#def watermark_content(f):
#  global watermark_image, watermark
#  image = Image.open("photos/" + f).convert("L")
#  img = image.load()
#  for x, y in np.ndindex(image.size):
#    # img[x, y] = tuple(map(lambda z: z + watermark[x][y], img[x, y]))
#    img[x, y] = max(0, min(255, img[x, y] + watermark[x][y]))
#  image.save("watermarked/" + f)

def main():
  watermark_image = Image.open("watermark.bmp")
  watermark = [1 if pixel == 0 else -1 for pixel in watermark_image.getdata()]
  image = Image.open("photos/" + f).convert("L").getdata()
  wimage = Image.open("watermarked/" + f.split(".")[0] + ".bmp").getdata()
  print linear_correlation(image, watermark)
  print linear_correlation(wimage, watermark)
  print linear_correlation(map(operator.sub, image, wimage), watermark)
  #print map(operator.sub, image, wimage)
  

main()
