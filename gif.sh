#!/bin/bash

nice -n 19 ffmpeg \
    -safe 0 -f concat -i images.txt \
    -vf "deflicker,fps=30,scale=480:-1:flags=lanczos,split[s0][s1];[s0]palettegen[p];[s1][p]paletteuse" \
    -loop 0 PhenoCam_Timelapse.gif
