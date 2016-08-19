#!/bin/bash
for i in {1..100}
do
   time python break_adj.py --watermarked=in/ --deduced=deduced.bmp --size=2592x1944 >> bench.out 2>> bench.err
   array=(in/*)
   rm "${array[0]}"
done
