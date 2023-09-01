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
- Benchmark script for evaluating performance - `coming soon`

## Benchmarks

Tested on 9/1/2023, commit 87121d18ca9cb0b0bc072eeaff76ab7e99f4b762

| Detection Method               | Input Resolution | Apple M1 | Orange Pi 5 |
|--------------------------------|------------------|----------|-------------|
| Aruco + solvepnp_singletag     | 1600x1200        | 122fps   | 47fps       |
| Apriltag3 + solvepnp_singletag | 1600x1200        | 96fps    | 35fps       |

## Getting Started

### Prerequisites
- Python version 3.10 or newer
- USB camera

### Install libraries
```shell
pip install -r requirements.txt
```

### Starting the program
```shell
python3 main.py
```

## Configuration
PeninsulaPerception is configured using `config.json` in the project's root directory. 