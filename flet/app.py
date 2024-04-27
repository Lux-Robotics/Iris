import flet as ft
import fletify
from dropdown import *


def main(page: ft.Page):
    page.theme = ft.Theme(use_material3=True)
    appbar = ft.AppBar(title=ft.Text("PeninsulaPerception"), elevation=1)

    pipeline_subdiv = ft.Text("Pipeline Settings", size=24)

    detector_dropdown = DropdownWithLabel(
        "Detector", Dropdown(["Apriltag3", "Aruco"], "Aruco")
    )
    tag_family = DropdownWithLabel(
        "AprilTag Family", Dropdown(["16h5", "36h11"], "36h11")
    )
    solvepnp_dropdown = DropdownWithLabel(
        "Pose Estimation Algorithm",
        Dropdown(["singletag", "multitag", "ransac"], "ransac"),
    )
    stream_res = DropdownWithLabel(
        "Stream Resolution", Dropdown(["1920x1200", "960x600"], "960x600")
    )

    camera_subdiv = ft.Text("Camera Settings", size=24)

    exposure_text = ft.Text("Exposure")
    exposure_slider = ft.Slider(label="Exposure", expand=True)

    brightness_text = ft.Text("Brightness")
    brightness_slider = ft.Slider(label="Exposure", expand=True)

    gain_text = ft.Text("Sensor Gain")
    gain_slider = ft.Slider(label="Exposure", expand=True)

    page.add(
        appbar,
        ft.Column(
            controls=[
                camera_subdiv,
                ft.Row([exposure_text, exposure_slider]),
                ft.Row([brightness_text, brightness_slider]),
                ft.Row([gain_text, gain_slider]),
            ],
            width=300,
        ),
        ft.Column(
            controls=[
                pipeline_subdiv,
                tag_family,
                detector_dropdown,
                solvepnp_dropdown,
                stream_res,
            ],
            width=400,
        ),
    )


ft.app(target=main, view=ft.AppView.WEB_BROWSER)
