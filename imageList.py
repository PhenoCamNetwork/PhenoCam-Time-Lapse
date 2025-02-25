#!/usr/bin/env python3
"""
This is the first scipt needed to create a time lapse video using FFmpeg.
In particular, this scrit will gather a list of images, select images based on user input, download the images (if requested), and finally organize the list in a structure that FFmpeg can read.
"""

from os import path, walk
from datetime import datetime, time
from urllib import request, parse
import json
import argparse



# If reported exposure is above this value, do not include the image (too dark), only relevant when accessing the archive locally
EXPOSURE_THRESHOLD = 1000
PHENOCAM_URL = "https://phenocam.nau.edu/"


# Command line variables
parser = argparse.ArgumentParser(prog="imageList.py",
    description="Make a list of images in the PhenoCam archive that can be processed by FFmpeg to make a timelapse video")
# Site name to make time lapse of
parser.add_argument('sitename', action='store',
    help="The site name which you want to make a timelapse of (case sensitive).")
# First date to start video (or earleist the site has)
parser.add_argument('startDate', action='store', default="2000-01-01",
    help="The first day to include. Format: YYYY-MM-DD")
# The last date to end the video with (or present date)
parser.add_argument('endDate', action='store', default="9999-12-31",
    help="The Last day to include. Format: YYYY-MM-DD")
# Terminal verbosity
parser.add_argument('--verbose', '-v', action='count', default=0,
	help="Post more messages useful for debugging")
# Path to PhenoCam imagery
parser.add_argument('--archive', action='store', default="/data/archive/",
    help="Filesystem path to PhenoCam image archive")
# Path to use when downloading images (if applicable)
parser.add_argument('--download-location', action='store', default="./archive/",
    help="Filesystem path to use when downloading images")
# Path to PhenoCam imagery (or where it should be downloaded to)
parser.add_argument('--download', action='store_true',
    help="Download images from the website. Please be nice to our servers!")
# Cant do both all images and only midday
imageSelection = parser.add_mutually_exclusive_group(required=True)
imageSelection.add_argument('--midday', action='store_true',
    help="Include only midday images within specified time")
imageSelection.add_argument('--all-daytime', action='store_true',
    help="Include all daytime images within specified time. Not reccomended!")

args = parser.parse_args()

# Start date for including images
startDate = datetime.strptime(args.startDate,'%Y-%m-%d')
# End time for including images
endDate = datetime.strptime(args.endDate,'%Y-%m-%d')
# Check that dates are valid
if startDate > endDate:
    raise Exception("Your start date must be before your end date!")

# Absolute filesystem path to the site, i.e. /data/archive/harvard/
sitePath = path.join(args.archive, args.sitename)
    
# list which valid images will be added
imageList = []




#
# First, generate list of images to use
#
# If only using midday images
if args.midday:
    # Check that the metadata file exists
    if not path.exists(path.join(sitePath, "ROI", f"{args.sitename}-midday.txt")):
        # GET the list of midday images, convert it to a dictionary
        middayimgs = json.loads(request.urlopen(parse.urljoin(PHENOCAM_URL,
            f"/api/middayimages/{args.sitename}")).read())
        # Add each midday image to the list (will be sorted later)
        for day in middayimgs:
            imageList.append(parse.urljoin(PHENOCAM_URL, day["imgpath"]))
    else:
        # Read in file containing list of midday images
        with open(path.join(sitePath, "ROI", f"{args.sitename}-midday.txt"), 'r') as f:
            for line in f.readlines():
                # Sometimes there is extra whitespace which messes up processing
                line = line.strip()
                if path.exists(line):
                    imageList.append(file)
                    if args.verbose > 0:
                        print(f"ADDED: {line}")
                else:
                    if args.verbose > 2:
                        print(f"IGNORED: {line}")

# If using all daytime images
elif args.all_daytime:
    # If there is no local archive
    # TODO filter out black images when using API
    if not path.exists(sitePath):
        # GET the list of all images for site
        if args.verbose > 0:
            print("DOWNLOADING METADATA\nThis may take a long time for old sites!")
        allimgs = json.loads(request.urlopen(parse.urljoin(PHENOCAM_URL,
            f"/api/siteimagelist/{args.sitename}/")).read())
        # Add every image to the list
        imageList = allimgs["imagelist"]
    else:
        for root, dirs, files in walk(sitePath):
            for file in files:
                file = path.join(root, '/'.join(dirs), file)
                # Make sure the file is a jpeg and not an IR image
                if file.endswith(".jpg") and not "ROI" in file and not "IR" in file:
                    # By default, include images which are missing metadata (may cause some images to appear like static)
                    exposure = 0
                    try:
                        # Open the corresponding metadata file
                        with open(file.replace(".jpg", ".meta"), 'r') as f:
                            for line in f.readlines():
                                if line.startswith("exposure="):
                                    # Record the exposure value
                                    exposure = int(line.split("=")[-1])
                                    # Dont read the rest of the metadata file
                                    break
                    # If the metadata file is not found
                    except FileNotFoundError:
                        # Ocassionally, there is no metadata file
                        print("No metadata found for {imageDate}!")
    
                    # if the image is bright enough
                    if exposure < EXPOSURE_THRESHOLD:
                        # Add the image to the list
                        imageList.append(file)
                        if args.verbose > 0:
                            print(f"ADDED: {file}; EXPOSURE: {exposure}")
                    elif args.verbose > 1:
                        print(f"TOO DARK: {file}; EXPOSURE: {exposure}")


# Filter images based on date
selectedImages = []
for image in imageList:
    # ONLY works on standard names, i.e.:
    # segaarboretummeadow_2020_07_11_213405.jpg
    imageDate = datetime.strptime(image[-21:-11],'%Y_%m_%d')
    # If the image is not within range
    if startDate <= imageDate <= endDate:
        # Remove this image from the list
        selectedImages.append(image)
        if args.verbose > 2:
            print(f"IMAGE ADDED: {image}")


# Download images
# TODO FFmpeg supports network sources, but concat doesn't seem to. Is there another workaround to avoid downloading the images here?
for i, image in enumerate(selectedImages):
    if args.download:
        # Get the path where image will be downloaded to
        saveFP =  path.join(args.download_location, path.basename(image))
        # Rename the image (so FFmpeg knows where to look)
        selectedImages[i] = saveFP
        if not path.exists(saveFP):
            if args.verbose > 1:
                print(f"DOWNLOADING: {image}")
            if args.verbose > 2:
                print(f"SAVED TO: {saveFP}")
            # Download the image from the server
            request.urlretrieve(image, saveFP)
        # Don't download existing images
        elif args.verbose > 0:
            print(f"NOT DOWNLOADED: {saveFP} (already exists)")



#
# Finally, write image list to a FFmpeg readable file
#
if args.verbose > 1:
    print("Writing list to file...")
# Images must be sorted now, FFmpeg renders the images in the same order as here
selectedImages.sort()
with open('images.txt', 'w') as f:
    for image in selectedImages:
        # Expected format by FFmpeg concat:
        # file 'filepath'
        f.write(f"file '{image}'\n")

if args.verbose > 0:
    print("\nDONE! You can now render the video with `videoFile.sh` or turn it into a gif with `gif.sh`.")
