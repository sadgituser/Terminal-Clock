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
    Entry,
    Frame,
    Label,
    Listbox,
    PhotoImage,
    Radiobutton,
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

window.geometry("800x480")
window.configure(bg="#000000")
center_window(window, 800, 480)


canvas = Canvas(
    window,
    bg="#000000",
    height=480,
    width=800,
    bd=0,
    highlightthickness=0,
    relief="ridge"
)

canvas.place(x=0, y=0)
canvas.create_rectangle(
    0.0,
    0.0,
    800.0,
    50.0,
    fill="#FFFFFF",
    outline="")

canvas.create_text(
    214.0,
    0.0,
    anchor="nw",
    text="Terminal Clock",
    fill="#00FF00",
    font=("IBM Plex Mono", 40 * -1, "bold", "roman")
)
window.resizable(False, False)

if __name__ == "__main__":
    window.mainloop()
