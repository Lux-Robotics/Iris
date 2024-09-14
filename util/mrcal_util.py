import subprocess


def generate_calibration_images(model_name: str):
    subprocess.run(
        [
            "mrcal-show-projection-uncertainty",
            "/tmp/camera-0.cameramodel",
            "--hardcopy=" + model_name + "_projection_uncertainty.svg",
        ]
    )
    subprocess.run(
        [
            "mrcal-show-valid-intrinsics-region",
            "/tmp/camera-0.cameramodel",
            "--hardcopy=" + model_name + "_valid_intrinsics_region.svg",
        ]
    )
    subprocess.run(
        [
            "mrcal-show-distortion-off-pinhole",
            "/tmp/camera-0.cameramodel",
            "--hardcopy=" + model_name + "_distortion.svg",
        ]
    )
    subprocess.run(
        [
            "mrcal-show-residuals",
            "/tmp/camera-0.cameramodel",
            "--vectorfield",
            "--hardcopy=" + model_name + "_residuals.svg",
        ]
    )


def calibrate_cameras():
    pass
