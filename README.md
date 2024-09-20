# PhenoCam Time-lapse Scripts

A small tool to create a video time-lapse using PhenoCam images.

***

## Requirements

Requirements for rendering the video:

 - Linux or macOS
 - Python3
 - FFmpeg
   - Must be compiled libx264 support
 - Access to the PhenoCam archive and related metadata (currently no API integration)
 
To playback the rendered video a device must have the ability to play h264 video.

## Generating the image List

Before rending the video, you must first generate a list of images. This can be done with the help of `imageList.py`. You must choose between including only midday images or including every daytime image. The former will result in a faster video and smaller file size, best for viewing change over the coarse of a year or so. The latter is best for viewing day-to-day changes on a smaller timescale.

To use the `imageList.py` script, you must provide: the site name, start date, end date, and specify weather you want only midday images or all daylight images. Running this script with the `--help` switch will list all available options.

For midday images:

```bash
./imageList.py segaarboretummeadow 2021-01-01 2021-12-31 --midday
```

For all daytime images:

```bash
./imageList.py segaarboretummeadow 2021-01-01 2021-12-31 --all-daytime
```

This python script will generate a text file in a format that FFmpeg can read to create the time-lapse video. If you wish to, you may generate or curate this file by hand by adding or removing lines to `images.txt`.

## Generating a Video

If you wish to use your own software or different FFmpeg options, you may use the `images.txt` from above to do so. Otherwise, `videoFile.sh` contains sane options to be played back on a wide range of devices. This includes scaling all videos to 960p (live2 cameras will be scaled down), applying a "deflicker" filter, which should reduce drastic light changes between frames, and encode images to a video stream.

To generate the video, simply run the `videoFile.sh` script in the same directory as `images.txt`.
Please note: depending on the length selected when generating the list of images, the power of the device you are using, and the speed which you can access the PhenoCam archive, this command may take a very long time.

```bash
./videoFile.sh
```

*This will generate a MP4 file in the same directory that you are currently in with the current date as the name. If you are creating multiple files in the same day, remember to rename or move the MP4 files before rerunning the command*

### Generating a GIF

To create a looping GIF image, use the same process as creating a video, only replacing `videoFile.sh` with `gif.sh`

GIFs have much worse quality, but are easy to embed.

