#!/bin/bash

OKAY='PNG image data, 1480 x 625, 1-bit colormap, non-interlaced'
find ./Animalia/ | grep .png | xargs file | grep -v "$OKAY" | cut -d: -f 1 > /tmp/temp.txt

for FILE in `cat /tmp/temp.txt`;
do 
~/Desktop/ImageMagick-6.7.3-1/utilities/convert $FILE -define png:bit-depth=1 -define png:color-type=3 $FILE
done;

rm /tmp/temp.txt
