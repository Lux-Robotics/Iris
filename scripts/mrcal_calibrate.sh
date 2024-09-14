#!/bin/bash

# Check if an argument was provided
if [ "$#" -ne 1 ]; then
    echo "Usage: $0 <video_file>"
    exit 1
fi

VIDEO_FILE="$1"
IMAGE_DIR="img"

# Extract the base name of the video (without the path and extension)
VIDEO_NAME=$(basename "$VIDEO_FILE" | sed 's/\.[^.]*$//')

# Create image directory if it doesn't exist
mkdir -p "$IMAGE_DIR"

# Extract frames from the provided video file
ffmpeg -i "$VIDEO_FILE" -vsync 0 "$IMAGE_DIR"/"${VIDEO_NAME}_output_%04d.png"

# Run mrgingham to find corners
mrgingham --jobs $(nproc) --gridn 13 "$IMAGE_DIR"/"${VIDEO_NAME}_*.png" > "${VIDEO_NAME}_corners.vnl"

# Run camera calibration
mrcal-calibrate-cameras --corners-cache "${VIDEO_NAME}_corners.vnl" --lensmodel LENSMODEL_OPENCV8 --focal 900 --object-spacing 0.012 --object-width-n 13 "$IMAGE_DIR"/"${VIDEO_NAME}_*.png"

# Remove the images directory
rm -r "$IMAGE_DIR"
