from collections import Counter
import Image
import os

def main():
  files = os.listdir("photos/")
  sizes = []
  for f in files:
    im = Image.open("photos/" + f)
    sizes.append(im.size)
  sizes_count = Counter(sizes).most_common(2)
  s1, s2 = sizes_count[0][0], sizes_count[1][0]
  for f in files:
    im = Image.open("photos/" + f)
    if im.size == s2:
      im.rotate(90)
      print im.size
    elif im.size != s1:
      pass

main()
