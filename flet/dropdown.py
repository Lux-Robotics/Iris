import flet as ft


class Dropdown(ft.Dropdown):
    def __init__(self, options, default_value: str = ""):
        super().__init__(
            value=default_value,
            text_size=14,
            options=[ft.dropdown.Option(o) for o in options],
            border_width=1,
            content_padding=ft.padding.symmetric(0, 15),
            border_radius=15,
            expand=True,
        )


class DropdownWithLabel(ft.Row):
    def __init__(self, label: str, dropdown: Dropdown):
        self.label = ft.Text(label)
        self.label.width = 200
        self.dropdown = dropdown
        super().__init__(controls=[self.label, dropdown])
