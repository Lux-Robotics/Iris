import os
import shutil
import subprocess

from util.state import logger, exec_dir
import util.state as state


def generate_calibration_images(dir: str):
    subprocess.run(
        [
            "mrcal-show-projection-uncertainty",
            "camera-0.cameramodel",
            "--hardcopy=" + "projection_uncertainty.svg",
        ],
        cwd=dir,
    )
    subprocess.run(
        [
            "mrcal-show-valid-intrinsics-region",
            "camera-0.cameramodel",
            "--hardcopy=" + "valid_intrinsics_region.svg",
        ],
        cwd=dir,
    )
    subprocess.run(
        [
            "mrcal-show-distortion-off-pinhole",
            "camera-0.cameramodel",
            "--hardcopy=" + "distortion.svg",
        ],
        cwd=dir,
    )
    subprocess.run(
        [
            "mrcal-show-residuals",
            "camera-0.cameramodel",
            "--vectorfield",
            "--hardcopy=" + "residuals.svg",
        ],
        cwd=dir,
    )


def calibrate_cameras(image_dir: str, object_spacing: float = 0.012, gridn: int = 14):
    logger.info("Creating calibration directory")
    try:
        dir_path = "/tmp/calibration"
        if os.path.exists(dir_path):
            shutil.rmtree(dir_path)
        os.makedirs(dir_path)
    except Exception:
        logger.error("Creating calibration directory failed")
        return False

    logger.info("Starting calibration")
    try:
        with open(dir_path + "/corners.vnl", "w") as corners_cache:
            subprocess.run(
                [
                    "mrgingham",
                    "--jobs=8",
                    "--gridn=" + str(gridn),
                    image_dir + "/*.png",
                ],
                stdout=corners_cache,
                check=True,
            )
        logger.info("Computed corners cache")
    except subprocess.CalledProcessError:
        logger.error("Failed to compute corners cache")
        return False
    state.calibration_progress = 1
    try:
        subprocess.run(
            [
                "mrcal-calibrate-cameras",
                "--corners-cache=corners.vnl",
                "--lensmodel=LENSMODEL_OPENCV8",
                "--focal=900",
                "--object-spacing=" + str(object_spacing),
                "--object-width-n=" + str(gridn),
                image_dir + "/*.png",
            ],
            check=True,
            cwd=dir_path,
        )
        logger.info("Calibration complete")
    except subprocess.CalledProcessError:
        logger.error("Calibration failed")
        return False
    state.calibration_progress = 2
    logger.info("Converting calibration")
    try:
        subprocess.run(
            [
                os.path.join(exec_dir, "scripts", "convert_mrcal_calibs"),
                "camera-0.cameramodel",
                "calibration.toml",
            ],
            check=True,
            cwd=dir_path,
        )
    except subprocess.CalledProcessError:
        logger.error("Conversion failed")
        return False
    state.calibration_progress = 3
    logger.info("Generating graphs")
    try:
        generate_calibration_images(dir_path)
    except Exception:
        logger.error("Failed to generate graphs")
        return False
    logger.info("Calibration complete")
    state.calibration_progress = 4
    return True
