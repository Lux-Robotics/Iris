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

## Benchmarks
| Hardware    | Apple M1 | OrangePi 5 |
|-------------|----------|------------|
| 1600 x 1200 | 50fps    | N/A        |

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