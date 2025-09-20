from contextlib import suppress
from datetime import datetime, timezone
import os
from pathlib import Path
from typing import Any, Final

import pygame as pg
from pygame import Event
import pygame_gui as pg_gui
from pygame_gui.core.utility import create_resource_path
from pygame_gui.elements import UIButton, UIDropDownMenu
from pygame_gui.windows import UIFileDialog
from pynput import mouse
from screeninfo import get_monitors

LINE_COLOR: Final = (64, 224, 208)
WHITE: Final = (255, 255, 255)
YELLOW: Final = (255, 255, 0)
BLACK: Final = (0, 0, 0)


class CustomUIFileDialog(UIFileDialog):
    """Custom file dialog to filter and show only directories."""

    def __init__(self, *args: Any, **kwargs: Any) -> None:
        super().__init__(*args, **kwargs)
        self.current_file_list: list[tuple[str, str]] = []

    def update_current_file_list(self) -> None:
        super().update_current_file_list()
        self.current_file_list = [
            (name, item_type) for name, item_type in self.current_file_list if item_type == "#directory_list_item"
        ]


class Karbon:
    def __init__(self) -> None:
        pg.init()
        pg.display.set_caption("Karbon")

        # Get list of monitors
        self.monitors = get_monitors()
        self.monitor_names = [f"Monitor {i}: {m.width} x {m.height}" for i, m in enumerate(self.monitors, start=1)]
        self.current_monitor_index = 0
        # Set up window on the current monitor
        self.current_monitor = self.monitors[self.current_monitor_index]
        self.window_width, self.window_height = self.current_monitor.width, self.current_monitor.height
        self.window_surface = pg.display.set_mode((self.window_width, self.window_height), pg.RESIZABLE)
        # Initialize UI manager and drawing surface
        self.ui_manager = pg_gui.UIManager((self.window_width, self.window_height))
        self.bg = pg.Surface((self.window_width, self.window_height))
        self.bg.fill(BLACK)
        self.clock = pg.time.Clock()

        # Initialize buttons with their properties
        self.clear_btn = UIButton(
            relative_rect=pg.Rect(-220, -140, 140, 30),
            text="Clear",
            manager=self.ui_manager,
            anchors={"left": "right", "right": "right", "top": "bottom", "bottom": "bottom"},
        )
        self.snapshot_btn = UIButton(
            relative_rect=pg.Rect(-220, -190, 140, 30),
            text="Snapshot",
            manager=self.ui_manager,
            anchors={"left": "right", "right": "right", "top": "bottom", "bottom": "bottom"},
        )
        self.save_btn = UIButton(
            relative_rect=pg.Rect(-220, -240, 140, 30),
            text="Save as Image",
            manager=self.ui_manager,
            anchors={"left": "right", "right": "right", "top": "bottom", "bottom": "bottom"},
        )
        self.monitor_dropdown = UIDropDownMenu(
            options_list=self.monitor_names,
            starting_option=self.monitor_names[self.current_monitor_index],
            relative_rect=pg.Rect(-220, -290, 200, 30),
            manager=self.ui_manager,
            anchors={"left": "right", "right": "right", "top": "bottom", "bottom": "bottom"},
        )

        # Start mouse listener
        self.mouse_listener = mouse.Listener(on_move=self.on_move, on_click=self.on_click)
        self.mouse_listener.start()

    @staticmethod
    def get_current_datetime() -> str:
        return datetime.now(tz=timezone.utc).strftime("%Y%m%d_%H%M%S")

    @staticmethod
    def create_snapshot_folder() -> Path:
        directory_path = Path.home() / ".karbon_snapshots"
        if not directory_path.exists():
            directory_path.mkdir(parents=True, exist_ok=True)
        return directory_path

    def handle_button_press(
        self,
        event: Event,
        f_dialog: CustomUIFileDialog | None,
        snapshot_folder_path: Path,
    ) -> CustomUIFileDialog | None:
        # Clear the screen
        if event.ui_element == self.clear_btn:
            self.bg.fill(BLACK)
        # Take a snapshot
        elif event.ui_element == self.snapshot_btn:
            pg.image.save(self.bg, f"{snapshot_folder_path}/snapshot_{self.get_current_datetime()}.png")
        # Show the file save dialog
        elif event.ui_element == self.save_btn:
            f_dialog = CustomUIFileDialog(
                pg.Rect(160, 50, 440, 500),
                self.ui_manager,
                window_title="Save as Image",
                initial_file_path=".",
                allow_picking_directories=True,
            )
            self.save_btn.disable()
        elif f_dialog and event.ui_element == f_dialog.parent_directory_button:
            f_dialog.current_file_path = Path(f_dialog.current_directory_path)
        return f_dialog

    def handle_monitor_change(self, event: Event) -> None:
        # Update current monitor and recreate window with new dimensions
        self.current_monitor_index = self.monitor_names.index(event.text)
        self.current_monitor = self.monitors[self.current_monitor_index]
        # Note: SDL_VIDEO_WINDOW_POS is set but may not work in all pygame versions
        os.environ["SDL_VIDEO_WINDOW_POS"] = f"{self.current_monitor.x},{self.current_monitor.y}"
        self.window_width, self.window_height = self.current_monitor.width, self.current_monitor.height
        self.window_surface = pg.display.set_mode((self.window_width, self.window_height), pg.RESIZABLE)

        # Recreate UI manager and drawing surface for new monitor size
        self.ui_manager = pg_gui.UIManager((self.window_width, self.window_height))
        self.bg = pg.Surface((self.window_width, self.window_height))
        self.bg.fill(BLACK)

        # Recreate all UI elements for the new window size
        self.clear_btn = UIButton(
            relative_rect=pg.Rect(-220, -140, 140, 30),
            text="Clear",
            manager=self.ui_manager,
            anchors={"left": "right", "right": "right", "top": "bottom", "bottom": "bottom"},
        )
        self.snapshot_btn = UIButton(
            relative_rect=pg.Rect(-220, -190, 140, 30),
            text="Snapshot",
            manager=self.ui_manager,
            anchors={"left": "right", "right": "right", "top": "bottom", "bottom": "bottom"},
        )
        self.save_btn = UIButton(
            relative_rect=pg.Rect(-220, -240, 140, 30),
            text="Save as Image",
            manager=self.ui_manager,
            anchors={"left": "right", "right": "right", "top": "bottom", "bottom": "bottom"},
        )
        self.monitor_dropdown = UIDropDownMenu(
            options_list=self.monitor_names,
            starting_option=self.monitor_names[self.current_monitor_index],
            relative_rect=pg.Rect(-220, -290, 200, 30),
            manager=self.ui_manager,
            anchors={"left": "right", "right": "right", "top": "bottom", "bottom": "bottom"},
        )

    def handle_file_dialog_events(
        self,
        event: Event,
        img_path: str,
        f_dialog: CustomUIFileDialog | None,
    ) -> tuple[str, CustomUIFileDialog | None]:
        if event.type == pg_gui.UI_FILE_DIALOG_PATH_PICKED:
            with suppress(pg.error):
                img_path = create_resource_path(event.text)
        # Handle file dialog close event
        elif event.type == pg_gui.UI_WINDOW_CLOSE and event.ui_element == f_dialog:
            self.save_btn.enable()
            f_dialog = None
            if img_path:
                pg.image.save(self.bg, f"{img_path}/screenshot_{self.get_current_datetime()}.png")
                img_path = ""
        return img_path, f_dialog

    def run(self) -> None:
        img_path = ""
        f_dialog = None
        is_running = True
        snapshot_folder_path = self.create_snapshot_folder()

        while is_running:
            time_delta = self.clock.tick(60) / 1000.0
            for event in pg.event.get():
                if event.type == pg.QUIT:
                    is_running = False
                elif event.type == pg_gui.UI_BUTTON_PRESSED:
                    f_dialog = self.handle_button_press(event, f_dialog, snapshot_folder_path)
                elif event.type == pg_gui.UI_DROP_DOWN_MENU_CHANGED and event.ui_element == self.monitor_dropdown:
                    self.handle_monitor_change(event)
                elif event.type in (pg_gui.UI_FILE_DIALOG_PATH_PICKED, pg_gui.UI_WINDOW_CLOSE):
                    img_path, f_dialog = self.handle_file_dialog_events(event, img_path, f_dialog)
                # Process the event with the UI manager
                self.ui_manager.process_events(event)

            self.ui_manager.update(time_delta)
            self.window_surface.blit(self.bg, (0, 0))
            self.ui_manager.draw_ui(self.window_surface)
            pg.display.update()

        self.mouse_listener.stop()

    def on_click(self, x: int, y: int, button: mouse.Button, _pressed: bool) -> None:
        adjusted_x, adjusted_y = x - self.current_monitor.x, y - self.current_monitor.y
        # Check if the adjusted coordinates are within the bounds of the monitor
        if 0 <= adjusted_x < self.window_width and 0 <= adjusted_y < self.window_height:
            if button == mouse.Button.left:
                pg.draw.circle(self.bg, YELLOW, (adjusted_x, adjusted_y), 4)
            elif button == mouse.Button.right:
                pg.draw.circle(self.bg, (128, 0, 128), (adjusted_x, adjusted_y), 6)

    def on_move(self, x: int, y: int) -> None:
        adjusted_x, adjusted_y = x - self.current_monitor.x, y - self.current_monitor.y
        # Check if the adjusted coordinates are within the bounds of the monitor
        if 0 <= adjusted_x < self.window_width and 0 <= adjusted_y < self.window_height:
            pg.draw.line(self.bg, LINE_COLOR, (adjusted_x, adjusted_y), (adjusted_x, adjusted_y), 1)
