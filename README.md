<div>
  <h1 align="center">PeninsulaPerception</h1>
  <p align="center">
    Vision system for FRC
  </p>
</div>

## Capabilities

- Detection of Apriltags
- Tag pose estimation
- Logging and Live preview using Foxglove
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
pip install -r requirements_dev.txt
```

**Notes**

- If using gstreamer capture, you should not install `opencv-contrib-python` with pip. Instead, you need to compile
  opencv from source. Instructions are here: https://eninsula.pages.dev/docs/vision/compile-opencv

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

### Configuration Fields

`device_id`

- Type: `string`
- Description: Identifier for the device.

`map`

- Type: `string`
- Description: Path to the field layout file. It should contain the location of every apriltag on the field.

`server_ip`

- Type: `string`
- Description: IP address of the server NT4 instance.

`test_video`

- Type: `string`
- Description: Path to a test video file.

`camera`

- Type: `object`
    - `calibration`: Calibration file for the camera.
    - `pipeline`: GStreamer pipeline string for video capture (Only valid if `"capture": "gstreamer"`).
    - `fps`: Frames per second for the camera capture. This is used for latency compensation

`aruco`

- `decimate`: Image decimation factor.
- `aruco3`: Use ArUco 3.x version boolean flag.
- `corner_refinement`: Method used for corner refinement (`"subpix"`, `"none"`).
- `refinement_window`: Window size for corner refinement.

`apriltag3`

- `border`: Border size of the tag.
- `threads`: Number of threads to use for detection.
- `quad_decimate`: Image decimation factor.
- `quad_blur`: Blur applied to image before detection.
- `refine_edges`: Refine tag edges boolean flag.
- `refine_decode`: Refine tag decode boolean flag.
- `refine_pose`: Refine tag pose boolean flag.
- `debug`: Enable debug mode boolean flag.
- `quad_contours`: Use contours for quad detection boolean flag.

`preview`

- `enabled`: Enable foxglove logging.
- `show_fps`: Display FPS in the video stream.
- `stream_quality`: Stream quality (0-100).
- `log_quality`: Logging quality (0-100).
- `max_stream_res`: Maximum resolution for the stream `[width, height]`.

`use_networktables`

- Type: `boolean`
- Description: Use NetworkTables for sending data.

`capture`

- Type: `string`
- Description: Capture method (`"opencv"`, `"gstreamer"`).

`detector`

- Type: `string`
- Description: Type of marker detector to use (`"apriltag"`, `"aruco"`, `"wpilib"`).

`solvepnp_method`

- Type: `string`
- Description: Method used for solvePnP operations (`"singletag"`, `"multitag"`, `"ransac"`).

## NetworkTables Output

All NetworkTables outputs will be under /Perception/`device_id`

- fps: The current processing fps
- observations0, observations1: Field oriented poses
- errors: The ambiguity present in each of the poses
