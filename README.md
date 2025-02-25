# PhenoCam Time-lapse Scripts

A small tool to create a video time-lapse using PhenoCam images.

![Timelapse of Harvard](example.gif)

***

## Requirements

Requirements for rendering the video:

 - Linux (MacOS and Windows probably works too, but untested)
 - Python3
 - FFmpeg
   - Must be compiled libx264 support if rendering video
 - API access or a local copy of the archive
 
To playback the rendered video a device must have the ability to play h264 video.

## Generating the image List

Before rending the video, you must first generate a list of images. This can be done with the help of `imageList.py`. You must choose between including only midday images or including every daytime image. The former will result in a faster video and smaller file size, best for viewing change over the coarse of a year or so. The latter is best for viewing day-to-day changes on a smaller timescale.

To use the `imageList.py` script, you must provide: the site name, start date, end date, and specify weather you want only midday images or all daylight images. Running this script with the `--help` switch will list all available options.

This python script will generate a text file in a format that FFmpeg can read to create the time-lapse video. If you wish to, you may generate or curate this file by hand by adding or removing lines to `images.txt`.

### Using local archive backup

This section is only applicable if you have a backup of the PhenoCam archive, or direct access to the archive (such as NAU employees). **If you do not fit into either of these categories, continue to the next section.** By default, this script will assume the archive is located at `/data/archive/`. If the archive is elsewhere on your filesystem, specify using the flag `--archive`.

For midday images:

```bash
./imageList.py segaarboretummeadow 2021-01-01 2021-12-31 --midday
```

For all daytime images:

```bash
./imageList.py segaarboretummeadow 2021-01-01 2021-12-31 --all-daytime
```

### Using the API

If the local archive is not found, the script will instead use the PhenoCam API. Usage is simular to what is listed in the previous section. Only midday images are supported while using the API.

An additional flag `--download` must be specified in order to download the images from the PhenoCam server. They will be downloaded to the directory specified by the `--download-location` flag, by default that is `./archive`. The images will persist inbetween runs.


```bash
./imageList.py harvard 2025-01-01 9999-12-31 --midday --download
```

## Generating a Video

If you wish to use your own software or different FFmpeg options, you may use the `images.txt` from above to do so. Otherwise, `videoFile.sh` contains sane options to be played back on a wide range of devices. This includes scaling all videos to 960p (live2 cameras will be scaled down), applying a "deflicker" filter, which should reduce drastic light changes between frames, and encode images to a video stream.

To generate the video, simply run the `videoFile.sh` script in the same directory as `images.txt`.
Please note: depending on the length selected when generating the list of images, the power of the device you are using, and the speed which you can access the PhenoCam imagery, this command may take a very long time.

```bash
./videoFile.sh
```

### About the filters used in videoFile

This script uses multiple filters that are built into FFmpeg. These filters are primarily used to improve the quality of handheld, realtime video, not time lapses. These filters are still nice for viewing, but *will impare the accuracy of the data*.

The following filters are used:

 - deflicker
   - This filter is made to reduce the strobe effect of florescent light when being filmed in realtime. It tries to smooth out bright flashes of light. This may be helpful when there is massive changes in brightness over the course of a few frames
 - scale
   - The images are scaled to 960p to save space and create a consistant image. This may reduce graphical fidelity for some newer camera models.
 - deshake (disabled by default)
   - This filter is designed to stabalize the image from shaking caused by filming using a handheld camera. It tries to guess the movement of the camera by looking for change between frames. In some circumstances (such as with large shadows), this filter can add *more* movement to the final video than if it were not used. This filter is great for some sites with well mounted cameras and mild shadows.

### Generating a GIF

To create a looping GIF image, use the same process as creating a video, only replacing `videoFile.sh` with `gif.sh`

GIFs have much worse quality, but are easy to embed.

