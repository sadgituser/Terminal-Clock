import ctypes
import datetime
from pathlib import Path
import sys
from tkinter import Canvas, Label, PhotoImage, Tk, ttk

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


def load_photo_image(path: str):
    try:
        image = PhotoImage(file=str(path))
    except Exception:
        if Image is None or ImageTk is None:
            return None
        try:
            image = ImageTk.PhotoImage(Image.open(path))
        except Exception:
            return None
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


class ImageButton(Label):
    def __init__(self, master=None, command=None, **kwargs):
        super().__init__(master, **kwargs)
        self._command = command
        self.configure(cursor="hand2")
        self.bind("<Button-1>", self._invoke)

    def _invoke(self, event):
        if self._command is not None:
            self._command()


class TerminalClockApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Terminal Clock")
        self.root.geometry("800x480")
        self.root.configure(bg="#000000")
        self.root.resizable(False, False)
        center_window(self.root, 800, 480)

        # Main Canvas Setup
        self.canvas = Canvas(
            self.root,
            bg="#000000",
            height=480,
            width=800,
            bd=0,
            highlightthickness=0,
            relief="ridge"
        )
        self.canvas.place(x=0, y=0)

        # --- 1. Permanent UI (Header) ---
        self.canvas.create_rectangle(0.0, 0.0, 800.0, 50.0, fill="#171617", outline="")
        self.canvas.create_text(
            214.0,
            0.0,
            anchor="nw",
            text="Terminal Clock",
            fill="#00FF00",
            font=("IBM Plex Mono", -40, "bold")
        )

        header_img = load_photo_image(relative_to_assets("element_1.png"))
        if header_img:
            self.canvas.create_image(284.0, 73.0, image=header_img)

        # --- 2. Real-Time Persistent Clock Element ---
        self.clock_id = self.canvas.create_text(
            0.0,
            65.0,
            anchor="nw",
            text="",
            fill="#00FF00",
            font=("IBM Plex Mono", -16, "bold")
        )

        # --- 3. Dynamic UI State ---
        self.terminal_lines = [f"Terminal Line {i}" for i in range(1, 14)]

        # --- 4. Setup Controls & Start Loops ---
        self._setup_buttons()
        self.update_clock()
        self.refresh_window()

    # --- Clock Update System ---
    def update_clock(self):
        """Updates the clock text string every second without redrawing the window."""
        now_str = datetime.datetime.now().strftime("%H:%M:%S")
        self.canvas.itemconfig(
            self.clock_id,
            text=f"   Terminal Clock OS: Time {now_str}"
        )
        self.root.after(1000, self.update_clock)

    # --- Screen Refresh System ---
    def refresh_window(self):
        """Wipes only dynamic canvas items and redraws current terminal state."""
        self.canvas.delete("dynamic_ui")

        y_start = 99.0
        line_spacing = 25.0

        for i, line in enumerate(self.terminal_lines):
            self.canvas.create_text(
                0.0,
                y_start + (i * line_spacing),
                anchor="nw",
                text=f"   > {line}",
                fill="#00FF00",
                font=("IBM Plex Mono", -16, "bold"),
                tags="dynamic_ui"  # Tagged for selective clearing
            )

    def add_terminal_line(self, text):
        """Appends a new line, keeps output capped to 13 lines, and triggers a window refresh."""
        self.terminal_lines.append(text)
        if len(self.terminal_lines) > 13:
            self.terminal_lines.pop(0)
        self.refresh_window()

    def _setup_buttons(self):
        x_coords = [25.0, 225.0, 425.0, 625.0]
        for idx, x_pos in enumerate(x_coords, start=1):
            btn_img = load_photo_image(relative_to_assets(f"button_{idx}.png"))

            if btn_img:
                btn = ImageButton(
                    self.root,
                    image=btn_img,
                    borderwidth=0,
                    highlightthickness=0,
                    command=lambda b=idx: self.add_terminal_line(f"Button {b} clicked!"),
                    relief="flat"
                )
            else:
                # Fallback text buttons if image assets are missing
                btn = Label(
                    self.root,
                    text=f"Button {idx}",
                    bg="#171617",
                    fg="#00FF00",
                    font=("IBM Plex Mono", -12, "bold"),
                    cursor="hand2"
                )
                btn.bind("<Button-1>", lambda e, b=idx: self.add_terminal_line(f"Button {b} clicked!"))

            btn.place(x=x_pos, y=435.0, width=150.0, height=30.0)


if __name__ == "__main__":
    enable_dpi_awareness()
    root = Tk()
    app = TerminalClockApp(root)
    root.mainloop()

