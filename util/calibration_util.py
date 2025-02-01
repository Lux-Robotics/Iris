import os
import shutil
import subprocess
import tempfile
import uuid

import util.state as state
from util.state import exec_dir, logger


def generate_calibration_images(dir: str):
    commands = [
        [
            "mrcal-show-projection-uncertainty",
            "camera-0.cameramodel",
            "--hardcopy=" + "projection_uncertainty.svg",
        ],
        [
            "mrcal-show-valid-intrinsics-region",
            "camera-0.cameramodel",
            "--hardcopy=" + "valid_intrinsics_region.svg",
        ],
        [
            "mrcal-show-distortion-off-pinhole",
            "camera-0.cameramodel",
            "--hardcopy=" + "distortion.svg",
        ],
        [
            "mrcal-show-residuals",
            "camera-0.cameramodel",
            "--vectorfield",
            "--hardcopy=" + "residuals.svg",
        ],
    ]

    # Run all commands in parallel
    processes = [subprocess.Popen(cmd, cwd=dir) for cmd in commands]

    for proc in processes:
        proc.wait()
        if proc.returncode != 0:
            raise subprocess.CalledProcessError(proc.returncode, proc.args)


async def calibrate_cameras(
    image_dir: str, object_spacing: float = 0.010, gridn: int = 17
):
    with tempfile.TemporaryDirectory() as dir_path:
        logger.info("Starting calibration")
        yield f'data: {{"progress": {0}}}\n\n'
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
        except Exception as e:
            logger.error("Failed to compute corners cache: " + str(e))
            yield f'data: {{"progress": {-1}}}\n\n'
            return
        yield f'data: {{"progress": {1}}}\n\n'
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
        except Exception as e:
            logger.error("Calibration failed: " + str(e))
            yield f'data: {{"progress": {-1}}}\n\n'
            return
        yield f'data: {{"progress": {2}}}\n\n'
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
        except Exception as e:
            logger.error("Conversion failed: " + str(e))
            yield f'data: {{"progress": {-1}}}\n\n'
            return
        yield f'data: {{"progress": {3}}}\n\n'
        logger.info("Generating graphs")
        try:
            generate_calibration_images(dir_path)
        except Exception as e:
            logger.error("Failed to generate graphs: " + str(e))
            yield f'data: {{"progress": {-1}}}\n\n'
            return
        yield f'data: {{"progress": {4}}}\n\n'

        try:
            # Generate uuid name and copy to save folder
            calibration_name = uuid.uuid4().hex
            logger.info("Saving calibration: " + calibration_name)
            dest = os.path.join(state.config_dir, "calibration", calibration_name)
            os.makedirs(dest)
            for item in os.listdir(dir_path):
                if item.endswith(".svg") or item.endswith(".toml"):
                    src_file = os.path.join(dir_path, item)
                    dest_file = os.path.join(dest, item)
                    shutil.copy2(src_file, dest_file)

            # Create symlink
            staged_path = os.path.join(state.config_dir, "calibration", "staged")
            if os.path.isdir(staged_path):
                shutil.rmtree(staged_path)
            elif os.path.islink(staged_path):
                os.remove(staged_path)
            os.symlink(dest, staged_path)
            logger.info(f"Successfully created symlink {staged_path} -> {dest}")
        except Exception as e:
            logger.error("Failed to save calibration: " + str(e))
            yield f'data: {{"progress": {-1}}}\n\n'
            return

        yield f'data: {{"progress": {5}}}\n\n'
        logger.info("Calibration complete")
