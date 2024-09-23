import os
from contextlib import suppress
from datetime import datetime
from pathlib import Path
from typing import Final

import pygame as pg
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

    def __init__(self, *args, **kwargs) -> None:
        super().__init__(*args, **kwargs)
        self.current_file_list: list[tuple[str, str]] = []

    def update_current_file_list(self) -> None:
        super().update_current_file_list()
        self.current_file_list = [
            (name, item_type) for name, item_type in self.current_file_list if item_type == "#directory_list_item"
        ]


class Karbon:
    def __init__(self) -> None:
        # Initialize pygame and set up the window
        pg.init()
        pg.display.set_caption("Karbon")

        # Get list of monitors
        self.monitors = get_monitors()
        self.monitor_names = [f"Monitor {i + 1}: {m.width}x{m.height}" for i, m in enumerate(self.monitors)]

        # Create initial window on primary monitor
        self.current_monitor_index = 0
        self.set_window_on_monitor(self.current_monitor_index)

        self.ui_manager = pg_gui.UIManager((self.window_width, self.window_height))

        self.bg = pg.Surface((self.window_width, self.window_height))
        self.bg.fill(BLACK)
        self.clock = pg.time.Clock()

        # Initialize buttons with their properties
        self.clear_btn = UIButton(
            relative_rect=pg.Rect(-220, -140, 140, 30),
            text="Clear",
            manager=self.ui_manager,
            anchors={
                "left": "right",
                "right": "right",
                "top": "bottom",
                "bottom": "bottom",
            },
        )
        self.snapshot_btn = UIButton(
            relative_rect=pg.Rect(-220, -190, 140, 30),
            text="Snapshot",
            manager=self.ui_manager,
            anchors={
                "left": "right",
                "right": "right",
                "top": "bottom",
                "bottom": "bottom",
            },
        )
        self.save_btn = UIButton(
            relative_rect=pg.Rect(-220, -240, 140, 30),
            text="Save as Image",
            manager=self.ui_manager,
            anchors={
                "left": "right",
                "right": "right",
                "top": "bottom",
                "bottom": "bottom",
            },
        )
        self.monitor_dropdown = UIDropDownMenu(
            options_list=self.monitor_names,
            starting_option=self.monitor_names[self.current_monitor_index],
            relative_rect=pg.Rect(-220, -290, 200, 30),
            manager=self.ui_manager,
            anchors={
                "left": "right",
                "right": "right",
                "top": "bottom",
                "bottom": "bottom",
            },
        )

        # Start mouse listener
        self.mouse_listener = mouse.Listener(on_move=self.on_move, on_click=self.on_click)
        self.mouse_listener.start()

    def set_window_on_monitor(self, monitor_index: int) -> None:
        monitor = self.monitors[monitor_index]
        os.environ["SDL_VIDEO_WINDOW_POS"] = f"{monitor.x},{monitor.y}"
        self.window_width, self.window_height = monitor.width, monitor.height
        self.window_surface = pg.display.set_mode((self.window_width, self.window_height), pg.RESIZABLE)

    @staticmethod
    def get_current_datetime() -> str:
        return datetime.now().strftime("%Y%m%d_%H%M%S")

    @staticmethod
    def create_snapshot_folder() -> Path:
        directory_path = Path.home() / ".karbon_snapshots"
        if not directory_path.exists():
            directory_path.mkdir(parents=True, exist_ok=True)
        return directory_path

    def run(self) -> None:
        img_path, f_dialog = None, None
        is_running = True
        snapshot_folder_path = self.create_snapshot_folder()

        while is_running:
            # Limit the frame rate to 60 FPS
            time_delta = self.clock.tick(60) / 1000.0
            for event in pg.event.get():
                if event.type == pg.QUIT:
                    is_running = False

                # Process UI events
                if event.type == pg_gui.UI_BUTTON_PRESSED:
                    # Handle button presses
                    if event.ui_element == self.clear_btn:
                        self.bg.fill(BLACK)
                    elif event.ui_element == self.snapshot_btn:
                        pg.image.save(
                            self.bg,
                            f"{snapshot_folder_path}/snapshot_{self.get_current_datetime()}.png",
                        )
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

                elif event.type == pg_gui.UI_DROP_DOWN_MENU_CHANGED:
                    if event.ui_element == self.monitor_dropdown:
                        selected_monitor_name = event.text
                        self.current_monitor_index = self.monitor_names.index(selected_monitor_name)
                        # Update window to new monitor
                        self.set_window_on_monitor(self.current_monitor_index)
                        # Recreate UI manager and background surface with new size
                        self.ui_manager = pg_gui.UIManager((self.window_width, self.window_height))
                        self.bg = pg.Surface((self.window_width, self.window_height))
                        self.bg.fill(BLACK)
                        # Re-add UI elements to the new UI manager
                        self.clear_btn = UIButton(
                            relative_rect=pg.Rect(-220, -140, 140, 30),
                            text="Clear",
                            manager=self.ui_manager,
                            anchors={
                                "left": "right",
                                "right": "right",
                                "top": "bottom",
                                "bottom": "bottom",
                            },
                        )
                        self.snapshot_btn = UIButton(
                            relative_rect=pg.Rect(-220, -190, 140, 30),
                            text="Snapshot",
                            manager=self.ui_manager,
                            anchors={
                                "left": "right",
                                "right": "right",
                                "top": "bottom",
                                "bottom": "bottom",
                            },
                        )
                        self.save_btn = UIButton(
                            relative_rect=pg.Rect(-220, -240, 140, 30),
                            text="Save as Image",
                            manager=self.ui_manager,
                            anchors={
                                "left": "right",
                                "right": "right",
                                "top": "bottom",
                                "bottom": "bottom",
                            },
                        )
                        self.monitor_dropdown = UIDropDownMenu(
                            options_list=self.monitor_names,
                            starting_option=self.monitor_names[self.current_monitor_index],
                            relative_rect=pg.Rect(-220, -290, 200, 30),
                            manager=self.ui_manager,
                            anchors={
                                "left": "right",
                                "right": "right",
                                "top": "bottom",
                                "bottom": "bottom",
                            },
                        )

                elif event.type == pg_gui.UI_FILE_DIALOG_PATH_PICKED:
                    with suppress(pg.error):
                        img_path = create_resource_path(event.text)

                elif event.type == pg_gui.UI_WINDOW_CLOSE:
                    if event.ui_element == f_dialog:
                        self.save_btn.enable()
                        f_dialog = None
                        if img_path:
                            pg.image.save(
                                self.bg,
                                f"{img_path}/screenshot_{self.get_current_datetime()}.png",
                            )
                            img_path = None

                # Process the event with the UI manager
                self.ui_manager.process_events(event)

            self.ui_manager.update(time_delta)
            self.window_surface.blit(self.bg, (0, 0))
            self.ui_manager.draw_ui(self.window_surface)
            pg.display.update()

        self.mouse_listener.stop()

    def on_click(self, x, y, button, pressed) -> None:
        # Adjust coordinates relative to the selected monitor
        monitor = self.monitors[self.current_monitor_index]
        adjusted_x = x - monitor.x
        adjusted_y = y - monitor.y

        if 0 <= adjusted_x < self.window_width and 0 <= adjusted_y < self.window_height:
            if button == mouse.Button.left:
                pg.draw.circle(self.bg, YELLOW, (adjusted_x, adjusted_y), 4)
            elif button == mouse.Button.right:
                pg.draw.circle(self.bg, (128, 0, 128), (adjusted_x, adjusted_y), 6)

    def on_move(self, x, y) -> None:
        # Get the current monitor
        monitor = self.monitors[self.current_monitor_index]
        # Adjust coordinates relative to the selected monitor
        adjusted_x = x - monitor.x
        adjusted_y = y - monitor.y

        # Check if the adjusted coordinates are within the bounds of the monitor
        if 0 <= adjusted_x < self.window_width and 0 <= adjusted_y < self.window_height:
            pg.draw.line(self.bg, LINE_COLOR, (adjusted_x, adjusted_y), (adjusted_x, adjusted_y), 1)
