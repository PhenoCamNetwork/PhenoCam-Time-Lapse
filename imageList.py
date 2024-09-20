#!/usr/bin/env python3

from os import path, walk
from datetime import datetime, time
import argparse



# If reported exposure is above this value, do not include the image (too dark)
EXPOSURE_THRESHOLD = 1000


# Command line variables
parser = argparse.ArgumentParser(prog="imageList.py",
    description="Make a list of images in the PhenoCam archive that can be processed by FFmpeg to make a timelapse video.")
parser.add_argument('sitename', action='store',
    help="The site name which you want to make a timelapse of (case sensitive).")
parser.add_argument('startDate', action='store', default="2000-01-01",
    help="The first day to include. Format: YYYY-MM-DD")
parser.add_argument('endDate', action='store', default="9999-12-31",
    help="The Last day to include. Formate: YYYY-MM-DD")
parser.add_argument('--verbose', '-v', action='count', default=0,
	help="Post more messages useful for debugging.")
parser.add_argument('--archive', action='store', default='/data/archive/',
    help="Absolute filesystem path to PhenoCam image archive.")
# Cant do both all images and only midday
imageSelection = parser.add_mutually_exclusive_group(required=True)
imageSelection.add_argument('--midday', action='store_true',
    help="Include only midday images within specified time.")
imageSelection.add_argument('--all-daytime', action='store_true',
    help="Include all daytime images within specified time.")

args = parser.parse_args()

# Start date for including images
startDate = datetime.strptime(args.startDate,'%Y-%m-%d')
# End time for including images 
endDate = datetime.strptime(args.endDate,'%Y-%m-%d')
# Absolute filesystem path to the site, i.e. /data/archive/harvard/
sitePath = path.join(args.archive, args.sitename)

# list which valid images will be added
imageList = []


# If only using midday images
if args.midday:
    # Read in file containing list of midday images
    with open(path.join(sitePath, "ROI", f"{args.sitename}-midday.txt"), 'r') as f:
        for line in f.readlines():
            # Sometimes there is extra whitespace which messes up processing
            line = line.strip()
            if args.verbose > 2:
                print(f"IGNORED: {line}")
            if path.exists(line):
                # ONLY works on standard names, i.e.:
                # segaarboretummeadow_2020_07_11_213405.jpg
                imageDate = datetime.strptime(line[-21:-11],'%Y_%m_%d')
                # If the image is within range
                if startDate <= imageDate <= endDate:
                    # TODO replace /data/archive/ with user specified path
                    imageList.append(line)
                    if args.verbose > 0:
                            print(f"ADDED: {line}")

# If using all daytime images
elif args.all_daytime:
    for root, dirs, files in walk(sitePath):
        for file in files:
            file = path.join(root, '/'.join(dirs), file)
            # Make sure the file is a jpeg and not an IR image
            if file.endswith(".jpg") and not "ROI" in file and not "IR" in file:
                # ONLY works on standard names, i.e.:
                # segaarboretummeadow_2020_07_11_213405.jpg
                imageDate = datetime.strptime(file[-21:-11],'%Y_%m_%d')
                # If the image is within range
                if startDate <= imageDate <= endDate:
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


if args.verbose > 1:
    print("Writing list to file.")
# Images must be sorted now, FFmpeg renders the images in the same order as here
imageList.sort()
with open('images.txt', 'w') as f:
    for image in imageList:
        # Expected format by FFmpeg concat:
        # file 'filepath'
        f.write(f"file '{image}'\n")

if args.verbose > 0:
    print("\nDONE! You can now render the video with `videoFile.sh` or turn it into a gif with `gif.sh`.")

