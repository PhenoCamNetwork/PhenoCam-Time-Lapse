#!/bin/bash

# README
#  `deshake` has been removed as it chases shadows, add it back when poorly mounted
#  faststart flag removed to reduce IO
FILE_NAME=`awk -f getFileName.awk images.txt`
nice -n 19 ffmpeg \
    -threads 0 \
    -safe 0 -f concat -i images.txt \
    -vf "deflicker, scale=-1:960" \
    -c:v libx264 -crf 21 -preset veryslow \
    -an \
    $FILE_NAME.mp4
