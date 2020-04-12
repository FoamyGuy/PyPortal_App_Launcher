"""
The basis for this was originally created for the oshwabadge2020:
https://github.com/oshwabadge2020/apps/tree/master/app-loader

Adapted for PyPortal and Touchscreen by Foamyguy
"""
import os
import board

import adafruit_imageload
import time
from time import sleep
import terminalio
from adafruit_display_text import label
from adafruit_button import Button
import adafruit_touchscreen
import displayio

COLOR = 0xFFFFFF
FONT = terminalio.FONT
TOP_OFFSET = 3
MARGIN = 3
APP_DIR = "/apps"
MENU_START = 10+TOP_OFFSET+MARGIN

CURSOR_FILENAME = "8px_cursors.bmp"

# --| Button Config |-------------------------------------------------
BUTTON_X = 3
BUTTON_Y = 320 - 40 - 4
BUTTON_WIDTH = 240//3 - 4
BUTTON_HEIGHT = 40
BUTTON_STYLE = Button.ROUNDRECT
BUTTON_FILL_COLOR = 0x880088
BUTTON_OUTLINE_COLOR = 0xFF00FF
BUTTON_LABEL = "UP"
BUTTON_LABEL_COLOR = 0xFFFFFF
# --| Button Config |-------------------------------------------------

# Setup touchscreen (PyPortal)
ts = adafruit_touchscreen.Touchscreen(
        board.TOUCH_YD,
        board.TOUCH_YU,
        board.TOUCH_XR,
        board.TOUCH_XL,
        calibration=((5200, 59000), (5800, 57000)),
        size=(240, 320),
    )


class Loader:
    def __init__(self):

        self.display = board.DISPLAY
        self.display.brightness = 0.1
        self.cursor_index = 0
        self.init_cursor()

        self.files_available = self.check_for_apps()
        self.file_count = len(self.files_available)

        self.init_menu()
        self.display.rotation = 270
        self.display.show(self.screen_group)

    def init_cursor(self):
        self.cursor_group = displayio.Group()
        cursor_bmp, cursor_pal = adafruit_imageload.load(
            CURSOR_FILENAME,
            bitmap=displayio.Bitmap,
            palette=displayio.Palette
        )
        self.cursor = displayio.TileGrid(
            cursor_bmp,
            pixel_shader=cursor_pal,
            width=1,
            height=1,
            tile_width=8,
            tile_height=8
        )
        self.cursor[0] = 0
        self.cursor.x = 0
        self.cursor.y = MENU_START+(self.cursor_index*8)

    def init_menu(self):
        self.screen_group = displayio.Group(max_size=6)

        self.program_menu = displayio.Group(max_size=20, scale=2)

        loader_banner = label.Label(FONT, text="Choose to Run", color=0xFF00FF)
        loader_banner.x = 10
        loader_banner.y = TOP_OFFSET
        self.program_menu.append(loader_banner)
        for list_index, program_name in enumerate(self.files_available):
            menu_item_str = "%s"%'{:>5}'.format(program_name)

            menu_item = label.Label(FONT, text=menu_item_str, color=COLOR)
            menu_item.x = 10
            menu_item.y = MENU_START+(list_index*10)
            self.program_menu.append(menu_item)

        print("making up button")
        # Make the button
        self.up_button = Button(
            x=BUTTON_X,
            y=BUTTON_Y,
            width=BUTTON_WIDTH,
            height=BUTTON_HEIGHT,
            style=BUTTON_STYLE,
            fill_color=BUTTON_FILL_COLOR,
            outline_color=BUTTON_OUTLINE_COLOR,
            label=BUTTON_LABEL,
            label_font=terminalio.FONT,
            label_color=BUTTON_LABEL_COLOR,
        )

        self.down_button = Button(
            x=BUTTON_X+BUTTON_WIDTH+4,
            y=BUTTON_Y,
            width=BUTTON_WIDTH,
            height=BUTTON_HEIGHT,
            style=BUTTON_STYLE,
            fill_color=BUTTON_FILL_COLOR,
            outline_color=BUTTON_OUTLINE_COLOR,
            label="DOWN",
            label_font=terminalio.FONT,
            label_color=BUTTON_LABEL_COLOR,
        )

        self.run_button = Button(
            x=BUTTON_X+BUTTON_WIDTH*2+4+4,
            y=BUTTON_Y,
            width=BUTTON_WIDTH,
            height=BUTTON_HEIGHT,
            style=BUTTON_STYLE,
            fill_color=BUTTON_FILL_COLOR,
            outline_color=BUTTON_OUTLINE_COLOR,
            label="RUN",
            label_font=terminalio.FONT,
            label_color=BUTTON_LABEL_COLOR,
        )

        self.program_menu.append(self.cursor)

        self.screen_group.append(self.program_menu)

        self.screen_group.append(self.up_button.group)
        self.screen_group.append(self.down_button.group)
        self.screen_group.append(self.run_button.group)

    def run_file(self, filename):
        module_name = APP_DIR+"/"+filename.strip(".py")
        mod = __import__(module_name)
        self.display.show(None)
        mod.main()

        ok = False
        while not ok:
            if mod.running:
                print("mod stopped")
                self.display.show(self.screen_group)
                break

    def check_for_apps(self, appdir=APP_DIR):
        return os.listdir(appdir)

    #def print_list(display, programs, cur_index):


    def run(self):
        last_update =  time.monotonic()
        i = 0
        current_time = time.monotonic()
        prev_btns = {"up": False, "down": False, "run": False}
        while True:
            current_time =  time.monotonic()
            if current_time - last_update > 0.2:
                last_update = current_time
                i +=1
                self.cursor[0] = i%3

            self.cursor.y = MENU_START+(self.cursor_index*10)-2

            p = ts.touch_point
            if p:
                self.was_touched = True;
                if self.up_button.contains(p):
                    self.up_button.selected = True
                else:
                    self.up_button.selected = False

                if self.down_button.contains(p):
                    self.down_button.selected = True
                else:
                    self.down_button.selected = False

                if self.run_button.contains(p):
                    self.run_button.selected = True
                else:
                    self.run_button.selected = False
            else:
                self.was_touched = False
                self.run_button.selected = False
                self.up_button.selected = False
                self.down_button.selected = False


            buttons = {
                "up": self.up_button.selected,
                "down": self.down_button.selected,
                "run": self.run_button.selected
            }

            if buttons["up"] and not prev_btns["up"]:
                if self.cursor_index > 0:
                    self.cursor_index -= 1
            if buttons["down"] and not prev_btns["down"]:
                if self.cursor_index < self.file_count - 1:
                    self.cursor_index += 1

            if buttons["run"] and not prev_btns["run"]:
                self.run_file(self.files_available[self.cursor_index])

            prev_btns = buttons

if __name__ == "__main__":
    loader = Loader()
    loader.run()