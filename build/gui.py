import ctypes
import datetime
import os
from pathlib import Path
import random
import sys
from tkinter import Canvas, Tk

try:
    from PIL import Image, ImageTk
except ImportError:
    Image = None
    ImageTk = None

# Hardware GPIO Integration
try:
    from gpiozero import Button as GPIOButton, RotaryEncoder
    GPIO_AVAILABLE = True
except (ImportError, Exception):
    GPIO_AVAILABLE = False

PIN_ROTARY_A = 17
PIN_ROTARY_B = 27
PIN_ROTARY_SW = 22
PIN_BTN_1 = 23
PIN_BTN_2 = 24
PIN_BTN_3 = 25


class TerminalClockOS:
    def __init__(self, root):
        self.root = root
        self.root.title("Terminal Clock OS - Retro Edition")
        self.root.geometry("800x480")
        self.root.configure(bg="#000000")
        self.root.resizable(False, False)
        self._center_window(800, 480)

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

        # --- THEME & COLOR STATE ---
        self.themes = {
            "Matrix Green": {"fg": "#00FF00", "dim": "#005500", "bg_btn": "#171617"},
            "Amber CRT":    {"fg": "#FFB000", "dim": "#885500", "bg_btn": "#171617"},
            "Cyber Cyan":   {"fg": "#00FFFF", "dim": "#005555", "bg_btn": "#171617"},
            "Sith Red":     {"fg": "#FF0055", "dim": "#550011", "bg_btn": "#171617"},
        }
        self.theme_names = list(self.themes.keys())
        self.current_theme_idx = 0

        # --- APP STATE ---
        self.terminal_lines = []
        self.current_menu = "MAIN"
        self.selected_button_idx = 0

        # Alarm & Math Quiz
        self.alarm_time = "07:00"
        self.alarm_enabled = True
        self.in_alarm_state = False
        self.quiz_solution = None
        self.user_answer = 0

        # Self-Destruct Easter Egg
        self.self_destruct_count = 10
        self.self_destruct_job = None

        # Fun System Quotes & Personality
        self.quotes = [
            "I'm sorry, Dave. I can't snooze that alarm.",
            "Waking up uses 99% of your available processing power.",
            "Fun fact: Coffee is just battery acid for humans.",
            "Raspberry Pi Zero 2 W running at optimal speed.",
            "CRT phosphor warmth detected... cozy level 100%.",
            "Beep boop. Don't touch my rotary encoder.",
            "Error 404: Sleep not found."
        ]

        # --- MENUS ---
        self.menus = {
            "MAIN": [
                {"label": "ALARM", "action": self.open_alarm_menu},
                {"label": "GAMES", "action": self.open_games_menu},
                {"label": "PANIC!", "action": self.trigger_self_destruct},
                {"label": "SETTINGS", "action": self.open_settings_menu},
            ],
            "ALARM": [
                {"label": "TOGGLE ON/OFF", "action": self.action_toggle_alarm},
                {"label": "SET 07:00", "action": lambda: self._set_alarm("07:00")},
                {"label": "TEST QUIZ", "action": self.trigger_alarm_quiz},
                {"label": "< BACK", "action": self.open_main_menu},
            ],
            "GAMES": [
                {"label": "FORTUNE", "action": self.print_random_quote},
                {"label": "8-BALL", "action": self.ask_magic_8ball},
                {"label": "COIN FLIP", "action": self.flip_coin},
                {"label": "< BACK", "action": self.open_main_menu},
            ],
            "SETTINGS": [
                {"label": "THEME", "action": self.cycle_theme},
                {"label": "CLEAR LOGS", "action": self.clear_logs},
                {"label": "REBOOT", "action": lambda: self.add_terminal_line("System rebooting...")},
                {"label": "< BACK", "action": self.open_main_menu},
            ],
            "QUIZ": [
                {"label": "- 1", "action": lambda: self.adjust_quiz_answer(-1)},
                {"label": "+ 1", "action": lambda: self.adjust_quiz_answer(1)},
                {"label": "SUBMIT", "action": self.check_quiz_answer},
                {"label": "SNOOZE", "action": lambda: self.add_terminal_line("Solve the math problem to snooze!")},
            ]
        }

        # --- UI STATIC ELEMENTS ---
        self.canvas.create_rectangle(0.0, 0.0, 800.0, 50.0, fill="#171617", outline="")
        self.header_text_id = self.canvas.create_text(
            400.0, 25.0, anchor="center", text="Terminal Clock OS",
            fill=self._color("fg"), font=("IBM Plex Mono", -28, "bold")
        )

        self.clock_id = self.canvas.create_text(
            15.0, 65.0, anchor="nw", text="",
            fill=self._color("fg"), font=("IBM Plex Mono", -16, "bold")
        )

        # Draw Retro CRT Scanlines Effect across screen
        for y in range(0, 480, 4):
            self.canvas.create_line(0, y, 800, y, fill="#000000", stipple="gray50")

        # --- CONTROLS ---
        self.canvas.bind("<Button-1>", self._on_canvas_click)
        self.root.bind("<Left>", lambda e: self.navigate_buttons(-1))
        self.root.bind("<Right>", lambda e: self.navigate_buttons(1))
        self.root.bind("<Return>", lambda e: self.press_selected_button())
        self.root.bind("<space>", lambda e: self.press_selected_button())
        self.root.bind("<Escape>", lambda e: self.open_main_menu())

        self._setup_hardware_gpio()

        # Loops
        self.update_clock()
        self.refresh_window()
        self.add_terminal_line("System Boot Complete. Welcome, Operator.")

    def _color(self, key):
        theme_name = self.theme_names[self.current_theme_idx]
        return self.themes[theme_name][key]

    # --- CLOCK LOOP ---
    def update_clock(self):
        now = datetime.datetime.now()
        now_str = now.strftime("%H:%M:%S")

        # Alarm Check
        if self.alarm_enabled and now.strftime("%H:%M") == self.alarm_time and now.second == 0:
            if not self.in_alarm_state:
                self.trigger_alarm_quiz()

        self.canvas.itemconfig(
            self.clock_id,
            text=f"Terminal Clock OS: Time {now_str} | Theme: {self.theme_names[self.current_theme_idx]}"
        )
        self.root.after(1000, self.update_clock)

    # --- FUN FEATURES & EASTER EGGS ---
    def trigger_alarm_quiz(self):
        """Forces the user to solve a math problem with rotary encoder to turn off alarm."""
        self.in_alarm_state = True
        self.current_menu = "QUIZ"
        self.selected_button_idx = 2  # Default to SUBMIT
        num1 = random.randint(12, 45)
        num2 = random.randint(11, 35)
        self.quiz_solution = num1 + num2
        self.user_answer = random.randint(10, 80)

        self.add_terminal_line("======================================")
        self.add_terminal_line("!!! ALARM TRIGGERED - WAKE UP CALL !!!")
        self.add_terminal_line(f"Solve to disarm: What is {num1} + {num2}?")
        self.add_terminal_line(f"Your Answer: {self.user_answer}")
        self.add_terminal_line("======================================")

    def adjust_quiz_answer(self, delta):
        self.user_answer += delta
        self.add_terminal_line(f"Selected Answer: {self.user_answer}")

    def check_quiz_answer(self):
        if self.user_answer == self.quiz_solution:
            self.in_alarm_state = False
            self.add_terminal_line("CORRECT ANSWER! Alarm Disarmed. Good morning!")
            self.open_main_menu()
        else:
            self.add_terminal_line(f"WRONG! {self.user_answer} is incorrect. Try again!")

    def trigger_self_destruct(self):
        """Playful countdown sequence with flickering screen."""
        self.self_destruct_count = 5
        self._self_destruct_tick()

    def _self_destruct_tick(self):
        if self.self_destruct_count > 0:
            self.add_terminal_line(f"!!! WARNING: SELF-DESTRUCT IN {self.self_destruct_count} !!!")
            self.self_destruct_count -= 1
            # Flicker screen red
            self.canvas.configure(bg="#330000" if self.self_destruct_count % 2 == 0 else "#000000")
            self.root.after(800, self._self_destruct_tick)
        else:
            self.canvas.configure(bg="#000000")
            self.add_terminal_line("BOOM! ... Just kidding. Have a nice day!")

    def print_random_quote(self):
        self.add_terminal_line(f"AI Quote: \"{random.choice(self.quotes)}\"")

    def ask_magic_8ball(self):
        responses = ["Outlook good.", "Ask again later.", "Cannot predict now.", "Definitely YES.", "Very doubtful."]
        self.add_terminal_line(f"Magic 8-Ball says: {random.choice(responses)}")

    def flip_coin(self):
        result = "HEADS" if random.choice([True, False]) else "TAILS"
        self.add_terminal_line(f"Flipping coin... Result: > {result} <")

    def clear_logs(self):
        self.terminal_lines = []
        self.add_terminal_line("Terminal logs cleared.")

    def cycle_theme(self):
        self.current_theme_idx = (self.current_theme_idx + 1) % len(self.theme_names)
        self.canvas.itemconfig(self.header_text_id, fill=self._color("fg"))
        self.canvas.itemconfig(self.clock_id, fill=self._color("fg"))
        self.add_terminal_line(f"Theme switched to {self.theme_names[self.current_theme_idx]}")

    # --- REFRESH & DRAW ---
    def refresh_window(self):
        self.canvas.delete("dynamic_ui")
        fg = self._color("fg")
        dim = self._color("dim")
        bg_btn = self._color("bg_btn")

        # Terminal Lines
        y_start = 95.0
        for i, line in enumerate(self.terminal_lines):
            self.canvas.create_text(
                15.0, y_start + (i * 22.0), anchor="nw", text=f"> {line}",
                fill=fg, font=("IBM Plex Mono", -15, "bold"), tags="dynamic_ui"
            )

        # Buttons
        x_positions = [25.0, 225.0, 425.0, 625.0]
        current_buttons = self.menus[self.current_menu]

        for i, btn_info in enumerate(current_buttons):
            x = x_positions[i]
            y = 430.0
            width, height = 150.0, 35.0
            is_selected = (i == self.selected_button_idx)

            fill_color = dim if is_selected else bg_btn
            outline_color = fg if is_selected else dim
            text_color = "#FFFFFF" if is_selected else fg
            prefix = "> " if is_selected else ""

            self.canvas.create_rectangle(
                x, y, x + width, y + height,
                fill=fill_color, outline=outline_color,
                width=2 if is_selected else 1, tags="dynamic_ui"
            )

            self.canvas.create_text(
                x + (width / 2), y + (height / 2),
                text=f"{prefix}{btn_info['label']}", fill=text_color,
                font=("IBM Plex Mono", -12, "bold"), tags="dynamic_ui"
            )

    # --- NAVIGATION ---
    def navigate_buttons(self, direction):
        self.selected_button_idx = (self.selected_button_idx + direction) % 4
        self.refresh_window()

    def press_selected_button(self):
        current_buttons = self.menus[self.current_menu]
        current_buttons[self.selected_button_idx]["action"]()

    def _on_canvas_click(self, event):
        x_positions = [25.0, 225.0, 425.0, 625.0]
        for i, x in enumerate(x_positions):
            if x <= event.x <= x + 150.0 and 430.0 <= event.y <= 465.0:
                self.selected_button_idx = i
                self.refresh_window()
                self.press_selected_button()
                break

    def add_terminal_line(self, text):
        self.terminal_lines.append(text)
        if len(self.terminal_lines) > 14:
            self.terminal_lines.pop(0)
        self.refresh_window()

    def open_main_menu(self):
        self.current_menu = "MAIN"
        self.selected_button_idx = 0
        self.refresh_window()

    def open_alarm_menu(self):
        self.current_menu = "ALARM"
        self.selected_button_idx = 0
        self.refresh_window()

    def open_games_menu(self):
        self.current_menu = "GAMES"
        self.selected_button_idx = 0
        self.refresh_window()

    def open_settings_menu(self):
        self.current_menu = "SETTINGS"
        self.selected_button_idx = 0
        self.refresh_window()

    def action_toggle_alarm(self):
        self.alarm_enabled = not self.alarm_enabled
        state = "ENABLED" if self.alarm_enabled else "DISABLED"
        self.add_terminal_line(f"Alarm status: {state}")

    def _set_alarm(self, time_str):
        self.alarm_time = time_str
        self.add_terminal_line(f"Alarm set to {self.alarm_time}")

    def _center_window(self, width, height):
        self.root.update_idletasks()
        x = int((self.root.winfo_screenwidth() - width) / 2)
        y = int((self.root.winfo_screenheight() - height) / 2)
        self.root.geometry(f"{width}x{height}+{x}+{y}")

    def _setup_hardware_gpio(self):
        if not GPIO_AVAILABLE:
            return
        try:
            self.encoder = RotaryEncoder(PIN_ROTARY_A, PIN_ROTARY_B)
            self.encoder.when_rotated_clockwise = lambda: self.navigate_buttons(1)
            self.encoder.when_rotated_counter_clockwise = lambda: self.navigate_buttons(-1)

            self.encoder_btn = GPIOButton(PIN_ROTARY_SW, bounce_time=0.05)
            self.encoder_btn.when_pressed = self.press_selected_button

            self.btn1 = GPIOButton(PIN_BTN_1, bounce_time=0.05)
            self.btn1.when_pressed = lambda: self.navigate_buttons(-1)

            self.btn2 = GPIOButton(PIN_BTN_2, bounce_time=0.05)
            self.btn2.when_pressed = self.press_selected_button

            self.btn3 = GPIOButton(PIN_BTN_3, bounce_time=0.05)
            self.btn3.when_pressed = lambda: self.navigate_buttons(1)
        except Exception as e:
            print(f"GPIO Error: {e}")


if __name__ == "__main__":
    root = Tk()
    app = TerminalClockOS(root)
    root.mainloop()

