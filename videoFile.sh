#!/bin/bash

# README
#  `deshake` has been removed as it chases shadows, add it back when poorly mounted
#  faststart flag removed to reduce IO

nice -n 19 ffmpeg \
    -threads 0 \
    -safe 0 -f concat -i images.txt \
    -vf "deflicker, scale=-1:960" \
    -c:v libx264 -crf 21 -preset veryslow \
    -an \
    $(date --iso-8601).mp4
