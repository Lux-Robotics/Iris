import os
import subprocess

import uvicorn
from fastapi import FastAPI, HTTPException
from fastapi.responses import StreamingResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel

import util.snapshot_manager
from util import state
from util.calibration_util import calibrate_cameras
from util.state import Platform, current_platform, device_id, exec_dir, settings


class IPConfig(BaseModel):
    dhcp: bool
    ipv4: str
    gateway: str


app = FastAPI()

os.makedirs(state.snapshots_dir, exist_ok=True)


@app.post("/api/hostname")
def update_hostname(new_hostname: str):
    if current_platform == Platform.IRIS:
        try:
            subprocess.run(
                ["hostnamectl", "set-hostname", new_hostname.hostname], check=True
            )
        except subprocess.CalledProcessError:
            raise HTTPException(status_code=500, detail="Failed to set hostname")
    elif current_platform == Platform.TEST:
        try:
            subprocess.run(
                ["hostnamectl", "hostname", new_hostname.hostname], check=True
            )
        except subprocess.CalledProcessError:
            raise HTTPException(status_code=500, detail="Failed to set hostname")
    else:
        raise HTTPException(
            status_code=403, detail="Hostname cannot be set in a dev environment"
        )
    return {"status": "ok"}


@app.get("/api/hostname", response_model=str)
def get_hostname():
    return {"hostname": device_id}


@app.post("/api/ip-config")
def update_ip_config(new_ip_config: IPConfig):
    if current_platform == Platform.IRIS:
        try:
            connection_name = "eth0"
            subprocess.run(
                [
                    "nmcli",
                    "con",
                    "modify",
                    connection_name,
                    "ipv4.method",
                    "auto" if new_ip_config.dhcp else "manual",
                ],
                check=True,
            )
            if not new_ip_config.dhcp:
                subprocess.run(
                    [
                        "nmcli",
                        "con",
                        "modify",
                        connection_name,
                        "ipv4.address",
                        new_ip_config.ipv4,
                    ],
                    check=True,
                )
                subprocess.run(
                    [
                        "nmcli",
                        "con",
                        "modify",
                        connection_name,
                        "ipv4.gateway",
                        new_ip_config.gateway,
                    ],
                    check=True,
                )
        except subprocess.CalledProcessError:
            raise HTTPException(
                status_code=500, detail="Failed to set ip configuration"
            )
    else:
        raise HTTPException(
            status_code=403, detail="IP cannot be set in a dev environment"
        )
    return {"status": "ok"}


@app.get("/api/ip-config", response_model=IPConfig)
def get_ip_config():
    try:
        connection_name = "eth0"
        result = subprocess.run(
            [
                "nmcli",
                "-g",
                "ipv4.method,ipv4.address,ipv4.gateway",
                "con",
                "show",
                connection_name,
            ],
            text=True,
            capture_output=True,
            check=True,
        )

        details = result.stdout.strip().splitlines()
        connection_info = {}

        for detail in details:
            key, value = detail.split(":", 1)
            connection_info[key] = value.strip()

        # Determine DHCP setting and extract relevant information
        dhcp = connection_info["ipv4.method"] == "auto"
        ipv4 = connection_info.get("ipv4.address", "Not set")
        gateway = connection_info.get("ipv4.gateway", "Not set")
        return {
            "dhcp": dhcp,
            "ipv4": ipv4,
            "gateway": gateway,
        }
    except Exception:
        raise HTTPException(status_code=500, detail="Failed to get IP configuration")


@app.post("/api/take-snapshot")
def take_snapshot():
    util.snapshot_manager.take_snapshot()
    return {"status": "ok"}


@app.post("/api/delete-snapshots")
def delete_snapshots():
    util.snapshot_manager.clear_snapshots()
    return {"status": "ok"}


@app.get("/api/calibrate")
async def calibrate():
    return StreamingResponse(
        calibrate_cameras(state.snapshots_dir), media_type="text/event-stream"
    )


@app.post("/api/swap-calibrations")
def swap_calibrations():
    current = os.path.join(state.config_dir, "calibration", "current")
    staged = os.path.join(state.config_dir, "calibration", "staged")

    if not os.path.islink(current) or not os.path.islink(staged):
        raise HTTPException(status_code=500, detail="Swap failed")

    target1 = os.readlink(current)
    target2 = os.readlink(staged)

    os.unlink(current)
    os.unlink(staged)

    os.symlink(target2, current)
    os.symlink(target1, staged)

    state.reload_calibration()
    return {"status": "ok"}


@app.get("/api/get-calibrations")
def get_calibrations():
    try:
        staged = state.load_calibration(state.settings, "staged")
    except Exception:
        staged = None

    return {"current": settings.calibration, "staged": staged}


app.mount("/snapshots", StaticFiles(directory=state.snapshots_dir), name="snapshots")

app.mount(
    "/calibrations",
    StaticFiles(directory=os.path.join(state.config_dir, "calibration")),
    name="calibrations",
)

app.mount(
    "/",
    StaticFiles(directory=os.path.join(exec_dir, "iris-web", "dist"), html=True),
    name="static",
)


def start():
    port = 80
    if current_platform == Platform.DEV:
        port = settings.dev_server_port
    uvicorn.run(app, host="0.0.0.0", port=port, log_level="info")
