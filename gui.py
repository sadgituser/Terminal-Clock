from pathlib import Path
import ctypes
import sys

# from tkinter import *
# Explicit imports to satisfy Flake8
from tkinter import (
    BooleanVar,
    Button,
    Canvas,
    Checkbutton,
    Frame,
    Label,
    Listbox,
    PhotoImage,
    StringVar,
    Text,
    Tk,
    ttk,
)

try:
    from PIL import Image, ImageTk
except ImportError:
    Image = None
    ImageTk = None


OUTPUT_PATH = Path(__file__).parent
ASSETS_PATH = OUTPUT_PATH / Path(r"assets\frame0")
THEME = ""
IMAGE_REFS = []


def relative_to_assets(path: str) -> Path:
    return ASSETS_PATH / Path(path)


def set_assets_path(path: str):
    global ASSETS_PATH
    ASSETS_PATH = OUTPUT_PATH / Path(path)


def load_photo_image(path: str):
    try:
        image = PhotoImage(file=path)
    except Exception:
        if Image is None or ImageTk is None:
            raise
        image = ImageTk.PhotoImage(Image.open(path))
    IMAGE_REFS.append(image)
    return image


def enable_dpi_awareness():
    if sys.platform != "win32":
        return
    try:
        ctypes.windll.shcore.SetProcessDpiAwareness(1)
    except Exception:
        try:
            ctypes.windll.user32.SetProcessDPIAware()
        except Exception:
            pass


def center_window(window, width, height):
    window.update_idletasks()
    x = int((window.winfo_screenwidth() - width) / 2)
    y = int((window.winfo_screenheight() - height) / 2)
    window.geometry(f"{width}x{height}+{x}+{y}")


def create_rounded_rectangle(canvas, x1, y1, x2, y2, radius, **kwargs):
    radius = max(0, min(radius, abs(x2 - x1) / 2, abs(y2 - y1) / 2))
    if radius == 0:
        return canvas.create_rectangle(x1, y1, x2, y2, **kwargs)
    points = [
        x1 + radius, y1,
        x2 - radius, y1,
        x2, y1,
        x2, y1 + radius,
        x2, y2 - radius,
        x2, y2,
        x2 - radius, y2,
        x1 + radius, y2,
        x1, y2,
        x1, y2 - radius,
        x1, y1 + radius,
        x1, y1,
    ]
    return canvas.create_polygon(points, smooth=True, **kwargs)


class ImageButton(Label):
    def __init__(self, master=None, command=None, **kwargs):
        super().__init__(master, **kwargs)
        self._command = command
        self.configure(cursor="hand2")
        self.bind("<Button-1>", self._invoke)

    def _invoke(self, event):
        if self._command is not None:
            self._command()

    def configure(self, cnf=None, **kwargs):
        if cnf and "command" in cnf:
            cnf = dict(cnf)
            self._command = cnf.pop("command")
        if "command" in kwargs:
            self._command = kwargs.pop("command")
        return super().configure(cnf, **kwargs)

    config = configure


def apply_theme(window):
    if not THEME:
        return
    try:
        ttk.Style(window).theme_use(THEME)
    except Exception:
        pass


enable_dpi_awareness()

window = Tk()
apply_theme(window)

#Window Geometry easy changer
windowheight = 480
windowwidth = 800


window.geometry(f"{windowwidth}x{windowheight}")
window.configure(bg="#000000")
center_window(window, windowwidth, windowheight)


#Main canvas that is black in color and is the window (windowwidth x windowheight in px)
canvas = Canvas(
    window,
    bg="#000000",
    height=windowheight,
    width=windowwidth,
    bd=0,
    highlightthickness=0,
    relief="ridge"
)


#Rectangle that is at the top of the window that is dark gray in color (is behind the 'Terminal Clock' text)
canvas.place(x=0, y=0)
canvas.create_rectangle(
    0.0,
    0.0,
    windowwidth,
    50.0,
    fill="#171617",
    outline="")


#'Terminal Clock' text in green shown at the top of the window (on top of the dark gray rectangle)
canvas.create_text(
    windowwidth / 2,
    0.0,
    anchor="n",
    text="Terminal Clock",
    fill="#00FF00",
    font=("IBM Plex Mono", 40 * -1, "bold", "roman")
)
window.resizable(False, False)

if __name__ == "__main__":
    window.mainloop()


#Still to add:
#Buttons for alarm setting, stopwatch, timer, and settings etc.
#Functions to convert the physical button input to interact with the GUI (like pressing the button to set an alarm, or start the stopwatch etc.)
#Functions to set the alarm, start the stopwatch, and start the timer etc.
#Functions for the rotary encoder to scroll through the options in the GUI and select them.
#Appearing and disappearing text on the CLI style 'terminal'
#Fun messages on the terminal
#Functionality to play sounds on the speaker when the alarm goes off, or when the timer goes off, or when the stopwatch is started/stopped etc.
#Functionality for the stopwatch, timer, and alarm to work in the background while the GUI is running.
#Functionality for menu switching between the main menu, alarm menu, stopwatch menu, timer menu, and settings menu etc.
#Functionality to save the alarm, stopwatch, and timer settings to a file so that they can be loaded when the program is restarted.
#Functionality to load the alarm, stopwatch, and timer settings from a file when the program is started.
#Functionality to set the time and date on the clock (settings menu) and save it to a file so that it can be loaded when the program is restarted.
#Functionality to ensure that the script restarts automatically when the Raspberry Pi is powered on (settings menu)
#Other ideas...
