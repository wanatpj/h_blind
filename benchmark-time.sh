#!/bin/bash
for i in {1..25}
do
   time python break_adj.py --watermarked=in/ --deduced=deduced.bmp --size=2592x1944 >> /dev/null 2>> /dev/null
   array=(in/*)
   rm "${array[0]}"
done
