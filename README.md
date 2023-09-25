<div>
  <h1 align="center">PeninsulaPerception</h1>
  <p align="center">
    Vision system for FRC
  </p>
</div>

## Capabilities

- Detection of Apriltags
- Tag pose estimation
- Live preview for detections
- Modular structure to allow for swapping pipeline components
- Highly configurable
- Benchmark mode for evaluating performance

## Benchmarks

Tested on 9/1/2023, commit 87121d18ca9cb0b0bc072eeaff76ab7e99f4b762

| Detection Method               | Input Resolution | Apple M1 | Orange Pi 5 |
|--------------------------------|------------------|----------|-------------|
| Aruco + solvepnp_singletag     | 1600x1200        | 122fps   | 47fps       |
| Apriltag3 + solvepnp_singletag | 1600x1200        | 96fps    | 35fps       |

## Getting Started

### Prerequisites

- Python version 3.10 or newer
- Clang and cmake installed
- USB camera

### Install libraries

```shell
pip install -r requirements.txt
```

**Notes**

- If using gstreamer capture, you should not install `opencv-contrib-python` with pip. Instead, you need to compile
  opencv from source.
  Instructions are here: https://preview.peninsula.pages.dev/docs/vision/compile-opencv

- `robotpy` does not provide prebuilt binaries for linux arm and installing with pip will result in an error.
  Install with this command instead:

```shell
CI=1 pip3 install --upgrade --find-links=https://tortall.net/~robotpy/wheels/2023/raspbian robotpy
``` 

### Starting the program

```shell
python3 main.py
```

**Manually select mode:**

```shell
python3 main.py --mode 0
```

**Modes:**

`0`: Normal operation (default)

`1`: Run using test video

`2`: Benchmark Mode

## Configuration

PeninsulaPerception is configured using `config.json` in the project's root directory.

### Parameters Overview

- device_id: The identifier for the camera. This will also be the name under which detection results will be sent over
  in NetworkTables
- calibration: Path to the calibration file. Reference the existing calibrations for formatting
- map: Path to the json file containing the locations of all the apriltags.
- test_video: Path to the test video for operational modes 1 and 2
- aruco: Settings for the aruco detector
- apriltag3: Settings for the apriltag3 detector
- preview: Settings for the web preview
    - enabled: Whether the preview is enabled
    - show_fps: Whether a fps counter is overlayed onto the preview stream
    - show_transform: Whether to overlay the tvec of the apriltag onto the stream. **Currently Deprecated**
    - stream_quality: The jpeg compression quality of each frame. Lower means more compression and less bandwidth
    - max_stream_res: The maximum streaming resolution. If the image is larger than this resolution, it will be scaled
      down by integer increments until it is under the maximum resolution
    - stream_port: The port that the stream is served under
- use_networktables: Toggle for NetworkTables support
- capture: Capture method `WIP`
- detector: The detector to use. Valid options are `aruco` and `apriltag3`
- solvepnp_method: The solvepnp method to use. Valid options are `singletag` and `multitag`

## NetworkTables Output

All NetworkTables outputs will be under /Perception/`device_id`

- fps: The current processing fps
- observations0, observations1: Field oriented poses
- errors: The ambiguity present in each of the poses