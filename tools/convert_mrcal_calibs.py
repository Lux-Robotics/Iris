# Tool to convert mrcal calibration to a normal .json

import argparse
import sys

import mrcal

parser = argparse.ArgumentParser("mrcal_converter")

parser.add_argument("filepath", help="Path to your .cameramodel file", type=str)
args = parser.parse_args()

try:
    model = mrcal.cameramodel(args.filename)
except:
    print("Error loading calibration file:", args.filename)
    sys.exit()
