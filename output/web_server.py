import subprocess

import uvicorn
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel

from util.state import exec_dir, settings, platform, Platform, device_id
from fastapi.staticfiles import StaticFiles
import os


class HostnameConfig(BaseModel):
    hostname: str


class IPConfig(BaseModel):
    dhcp: bool
    ipv4: str
    gateway: str


app = FastAPI()
# api_router = APIRouter()


@app.post("/api/hostname")
def update_hostname(new_hostname: HostnameConfig):
    if platform == Platform.IRIS:
        try:
            subprocess.run(
                ["hostnamectl", "set-hostname", new_hostname.hostname], check=True
            )
        except subprocess.CalledProcessError:
            raise HTTPException(status_code=500, detail="Failed to set hostname")
    else:
        raise HTTPException(
            status_code=403, detail="Hostname cannot be set in a dev environment"
        )
    return {"status": "ok"}


@app.get("/api/hostname", response_model=HostnameConfig)
def get_hostname():
    return {"hostname": device_id}


@app.post("/api/ip-config")
def update_ip_config(new_ip_config: IPConfig):
    if platform == Platform.IRIS:
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
            raise HTTPException(status_code=500, detail="Failed to set hostname")
    else:
        raise HTTPException(
            status_code=403, detail="Hostname cannot be set in a dev environment"
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


app.mount(
    "/",
    StaticFiles(directory=os.path.join(exec_dir, "iris-web", "dist"), html=True),
    name="static",
)
# app.include_router(api_router, prefix="/api")


def start():
    port = 80
    if platform != Platform.IRIS:
        port = settings.dev_server_port
    uvicorn.run(app, host="0.0.0.0", port=port, log_level="info")
