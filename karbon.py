from contextlib import suppress
from pathlib import Path

import pygame as pg
import pygame_gui as pg_gui
from pygame_gui.core.utility import create_resource_path
from pygame_gui.elements import UIButton
from pygame_gui.windows import UIFileDialog
from pynput import mouse

LINE_COLOR = (64, 224, 208)
WHITE = (255, 255, 255)
YELLOW = (255, 255, 0)
BLACK = (0, 0, 0)


class CustomUIFileDialog(UIFileDialog):
    def update_current_file_list(self):
        super().update_current_file_list()
        self.current_file_list = [
            i for i in self.current_file_list[::-1] if i[1] != "#file_list_item"
        ]


class Karbon:
    def __init__(self):
        pg.init()
        pg.display.set_caption("Karbon")
        screen = pg.display.Info()
        w, h = screen.current_w, screen.current_h
        self.window_surface = pg.display.set_mode((w, h), pg.RESIZABLE)
        self.ui_manager = pg_gui.UIManager((w, h))
        self.bg = pg.Surface((w, h))
        self.bg.fill(BLACK)
        self.clock = pg.time.Clock()
        self.clear_btn = UIButton(
            relative_rect=pg.Rect(-220, -80, 140, 30),
            text="Clear",
            manager=self.ui_manager,
            anchors={
                "left": "right",
                "right": "right",
                "top": "bottom",
                "bottom": "bottom",
            },
        )
        self.save_btn = UIButton(
            relative_rect=pg.Rect(-220, -140, 140, 30),
            text="Save as Image",
            manager=self.ui_manager,
            anchors={
                "left": "right",
                "right": "right",
                "top": "bottom",
                "bottom": "bottom",
            },
        )
        self.mouse_listener = mouse.Listener(
            on_move=self.on_move, on_click=self.on_click
        )
        self.mouse_listener.start()

    def run(self):
        img_path = None
        f_dialog = None
        is_running = True

        while is_running:
            time_delta = self.clock.tick(60) / 1000.0
            for event in pg.event.get():
                if event.type == pg.QUIT:
                    is_running = False
                if event.type == pg_gui.UI_BUTTON_PRESSED:
                    if event.ui_element == self.clear_btn:
                        self.bg.fill(BLACK)
                    if event.ui_element == self.save_btn:
                        f_dialog = CustomUIFileDialog(
                            pg.Rect(160, 50, 440, 500),
                            self.ui_manager,
                            window_title="Save as Image",
                            initial_file_path=".",
                            allow_picking_directories=True,
                        )
                        self.save_btn.disable()
                    if (
                        f_dialog
                        and event.ui_element == f_dialog.parent_directory_button
                    ):
                        f_dialog.current_file_path = Path(
                            f_dialog.current_directory_path
                        )
                if event.type == pg_gui.UI_FILE_DIALOG_PATH_PICKED:
                    with suppress(pg.error):
                        img_path = create_resource_path(event.text)
                if (
                    event.type == pg_gui.UI_WINDOW_CLOSE
                    and event.ui_element == f_dialog
                ):
                    self.save_btn.enable()
                    f_dialog = None
                    if img_path:
                        pg.image.save(self.bg, f"{img_path}/karbon-screenshot.jpg")
                        img_path = None

                self.ui_manager.process_events(event)

            self.ui_manager.update(time_delta)
            self.window_surface.blit(self.bg, (0, 0))
            self.ui_manager.draw_ui(self.window_surface)
            pg.display.update()

    def on_click(self, x, y, button, pressed):
        if button is button.left:
            pg.draw.circle(self.bg, YELLOW, (x, y), 4)
        elif button is button.right:
            pg.draw.circle(self.bg, (128, 0, 128), (x, y), 6)

    def on_move(self, x, y):
        pg.draw.line(self.bg, LINE_COLOR, (x, y), (x, y), 1)


def main():
    app = Karbon()
    app.run()


if __name__ == "__main__":
    main()
