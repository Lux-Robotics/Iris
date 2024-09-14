import os
import subprocess
import uuid

from util.state import logger, exec_dir


def generate_calibration_images(model_name: str, dir: str):
    subprocess.run(
        [
            "mrcal-show-projection-uncertainty",
            "/tmp/camera-0.cameramodel",
            "--hardcopy=" + model_name + "_projection_uncertainty.svg",
        ], cwd=dir
    )
    subprocess.run(
        [
            "mrcal-show-valid-intrinsics-region",
            "/tmp/camera-0.cameramodel",
            "--hardcopy=" + model_name + "_valid_intrinsics_region.svg",
        ], cwd=dir
    )
    subprocess.run(
        [
            "mrcal-show-distortion-off-pinhole",
            "/tmp/camera-0.cameramodel",
            "--hardcopy=" + model_name + "_distortion.svg",
        ], cwd=dir
    )
    subprocess.run(
        [
            "mrcal-show-residuals",
            "/tmp/camera-0.cameramodel",
            "--vectorfield",
            "--hardcopy=" + model_name + "_residuals.svg",
        ], cwd=dir
    )


def calibrate_cameras(image_dir: str, object_spacing: float = 0.012, gridn: int = 13):
    name = str(uuid.uuid4())
    logger.info("Starting calibration: " + name)
    try:
        with open("/tmp/corners_" + name + ".vnl", "w") as corners_cache:
            subprocess.run(
                [
                    "mrgingham",
                    "--jobs $(nproc)",
                    "--gridn=" + str(gridn),
                    image_dir + "/'*.png'",
                ], stdout=corners_cache, check=True
            )
        logger.info("Computed corners cache")
    except subprocess.CalledProcessError:
        logger.error("Failed to compute corners cache")
        return
    try:
        subprocess.run(
            [
                "mrcal-calibrate-cameras",
                "--corners-cache=" + "/tmp/corners_" + name + ".vnl",
                "--lensmodel=LENSMODEL_OPENCV8",
                "--focal=900",
                "--object-spacing=" + str(object_spacing),
                "--object-width-n=" + str(gridn),
            ],
            check=True,
            cwd = "/tmp"
        )
        logger.info("Calibration complete")
    except subprocess.CalledProcessError:
        logger.error("Calibration failed")
        return
    logger.info("Generating graphs")
    generate_calibration_images("test", os.path.join(exec_dir, "calibration"))
    logger.info("Calibration complete")
