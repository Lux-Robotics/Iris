# Tool to convert mrcal calibration to a normal .json

import argparse
import sys

import mrcal
import json

parser = argparse.ArgumentParser("mrcal_converter")

parser.add_argument("filepath", help="Path to your .cameramodel file", type=str)
args = parser.parse_args()

try:
    model = mrcal.cameramodel(args.filepath)
except:
    print("Error loading calibration file:", args.filepath)
    sys.exit()

id_num = input("Input camera identification number (ex. 002-1): ")

model_type, intrinsics_mrcal = model.intrinsics()

x_res, y_res = model.imagersize().tolist()

intrinsic_matrix_opencv = [
    [intrinsics_mrcal[0], 0, intrinsics_mrcal[2]],
    [0, intrinsics_mrcal[1], intrinsics_mrcal[3]],
    [0, 0, 1]
]

distortions_opencv = intrinsics_mrcal[4:].tolist()

calibration_out = {"resolution": [x_res, y_res], "cameraMatrix": intrinsic_matrix_opencv,
                   "distCoeffs": distortions_opencv}

out = open("calibration/" + id_num + "_" + str(x_res) + "x" + str(y_res) + ".json", "w")
out.write(json.dumps(calibration_out, indent=2))
out.close()
