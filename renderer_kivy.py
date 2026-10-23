"""
Kivy-based Mobile Terminal Renderer for Aurum Trust Bank

Features:
- Pure Kivy mobile layout with touch scrolling (ScrollView).
- Dark terminal aesthetics with monospaced font and box-drawing support.
- Adaptive Mobile Box Formatter:
  Automatically condenses wide desktop-sized ASCII tables (63+ chars wide like
  the 2-column menu) into clean single-column mobile-friendly cards that fit on
  any phone screen without wrapping or tearing!
- Horizontal Pan Support + Auto font scaling so nothing gets truncated.
- Full Touch QWERTY Keyboard:
  - Letters (a-z / A-Z) with dynamic SHIFT toggle (capitalization).
  - Numbers row (1-0).
  - Special characters & symbols toggle (?123 / ABC) for punctuation (@, #, $, %, etc.).
  - Spacebar, Backspace (DEL), and ENTER.
- Full stdio redirection (print / input) running the bank logic in a background thread.
- Matplotlib in-app popup modal preventing macOS FigureManager threading crashes.
"""

import sys
import os
import io
import re
import threading
import queue

os.environ["KIVY_NO_ARGS"] = "1"

try:
    from kivy.config import Config
    Config.set("graphics", "width", "420")
    Config.set("graphics", "height", "780")
    Config.set("graphics", "resizable", "1")

    from kivy.app import App
    from kivy.clock import Clock
    from kivy.uix.boxlayout import BoxLayout
    from kivy.uix.scrollview import ScrollView
    from kivy.uix.label import Label
    from kivy.uix.button import Button
    from kivy.uix.popup import Popup
    from kivy.uix.image import Image
    from kivy.core.image import Image as CoreImage
    from kivy.core.text import LabelBase
    from kivy.graphics import Color, Rectangle
except ImportError as e:
    print(f"Error: Kivy is not installed. Run `pip install kivy` to use this renderer.\nDetails: {e}")
    sys.exit(1)


# Register cross-platform monospace font in Kivy
MONO_FONT_CANDIDATES = [
    "/System/Library/Fonts/Supplemental/Courier New.ttf",
    "/System/Library/Fonts/Monaco.ttf",
    "/System/Library/Fonts/SFNSMono.ttf",
    "/Library/Fonts/Courier New.ttf",
    "/usr/share/fonts/truetype/dejavu/DejaVuSansMono.ttf",
    "C:\\Windows\\Fonts\\consola.ttf",
    "C:\\Windows\\Fonts\\cour.ttf",
]

MONO_FONT_NAME = None
for path in MONO_FONT_CANDIDATES:
    if os.path.exists(path):
        try:
            LabelBase.register(name="TerminalMono", fn_regular=path)
            MONO_FONT_NAME = "TerminalMono"
            break
        except Exception:
            continue


def format_for_mobile_screen(text, max_cols=38):
    """
    Transforms wide desktop ASCII tables into sleek, mobile-friendly cards.
    Detects two-column menu tables (+----+----+ and | col1 | col2 |) and converts
    them into clean single-column cards that never wrap or break borders.
    """
    lines = text.split("\n")
    formatted_lines = []

    for line in lines:
        # Check if line is a 2-column menu border: e.g. +----------------------------+--------------------------------+
        if line.startswith("+--") and "+" in line[1:-1] and line.endswith("+"):
            formatted_lines.append("+" + "-" * (max_cols - 2) + "+")
            continue

        # Check if line is a wide single border: e.g. +-------------------------------------------------------------+
        if line.startswith("+--") and line.endswith("+") and len(line) > max_cols:
            formatted_lines.append("+" + "-" * (max_cols - 2) + "+")
            continue

        # Check if line is a wide title: e.g. ======================AURUM TRUST BANK==============================
        if "====" in line and len(line) > max_cols:
            title = line.strip("= ")
            rem = max(0, max_cols - len(title) - 2)
            left = rem // 2
            right = rem - left
            formatted_lines.append("=" * left + " " + title + " " + "=" * right)
            continue

        # Check if line is a 2-column menu row: e.g. | 1) Deposit                 | 2)  Withdrawal                 |
        if line.startswith("|") and line.count("|") >= 3 and line.endswith("|"):
            parts = [p.strip() for p in line.split("|")[1:-1] if p.strip()]
            for item in parts:
                content = f" {item}"
                padded = content.ljust(max_cols - 2)[: max_cols - 2]
                formatted_lines.append(f"|{padded}|")
            continue

        # Check if line is a wide single-column row: e.g. | What would you like to perform today:                       |
        if line.startswith("|") and line.endswith("|") and len(line) > max_cols:
            inner = line[1:-1].strip()
            # If inner text fits in one mobile line
            if len(inner) <= max_cols - 4:
                formatted_lines.append(f"| {inner.ljust(max_cols - 4)} |")
            else:
                # Wrap long inner text cleanly within the box
                words = inner.split(" ")
                curr = ""
                for w in words:
                    if len(curr) + len(w) + 1 <= max_cols - 4:
                        curr = f"{curr} {w}".strip()
                    else:
                        formatted_lines.append(f"| {curr.ljust(max_cols - 4)} |")
                        curr = w
                if curr:
                    formatted_lines.append(f"| {curr.ljust(max_cols - 4)} |")
            continue

        formatted_lines.append(line)

    return "\n".join(formatted_lines)


class StdioRedirector:
    def __init__(self, app):
        self.app = app
        self.orig_stdout = sys.stdout
        self.orig_stderr = sys.stderr

    def write(self, s):
        if s:
            self.app.queue_output(s)
            self.orig_stdout.write(s)

    def flush(self):
        self.orig_stdout.flush()


def patch_matplotlib_for_kivy(app):
    """
    Mobile Fix for Matplotlib:
    1. Sets headless 'Agg' backend so it never tries to spawn an unsupported desktop window.
    2. Tunes figure style, fonts, and DPI for crisp high-density phone screens.
    3. Blocks the worker thread while showing the popup so the script doesn't race ahead.
    """
    try:
        import matplotlib
        matplotlib.use("Agg")  # CRITICAL: Headless backend prevents desktop window crash on mobile
        import matplotlib.pyplot as plt

        # Tune chart aesthetics for mobile phone screens
        plt.rcParams.update({
            "figure.figsize": (5, 4.5),
            "figure.dpi": 150,
            "font.size": 11,
            "axes.labelsize": 11,
            "axes.titlesize": 12,
            "xtick.labelsize": 10,
            "ytick.labelsize": 10,
            "lines.linewidth": 2,
        })

        def custom_show(*args, **kwargs):
            fig = plt.gcf()
            buf = io.BytesIO()
            fig.savefig(buf, format="png", bbox_inches="tight", dpi=160, facecolor="#ffffff")
            buf.seek(0)
            plt.close(fig)
            # Display popup in Kivy and pause thread until user taps 'Close'
            app.show_plot_blocking(buf.getvalue())

        plt.show = custom_show
    except ImportError:
        pass


class QwertyKeyboard(BoxLayout):
    """Full mobile QWERTY keyboard with numbers, alphabet, shift, symbols, space, del, enter."""
    def __init__(self, on_key_callback, **kwargs):
        super().__init__(orientation="vertical", **kwargs)
        self.size_hint_y = None
        self.height = 240
        self.spacing = 4
        self.padding = [4, 6, 4, 6]
        self.on_key_callback = on_key_callback

        self.is_shift = False
        self.is_symbols = False

        with self.canvas.before:
            Color(0.09, 0.11, 0.16, 1)
            self.bg_rect = Rectangle(size=self.size, pos=self.pos)
        self.bind(size=self._update_bg, pos=self._update_bg)

        self.rebuild_keys()

    def _update_bg(self, *args):
        self.bg_rect.pos = self.pos
        self.bg_rect.size = self.size

    def toggle_shift(self):
        self.is_shift = not self.is_shift
        self.rebuild_keys()

    def toggle_symbols(self):
        self.is_symbols = not self.is_symbols
        self.rebuild_keys()

    def rebuild_keys(self):
        self.clear_widgets()

        if self.is_symbols:
            rows = [
                ["1", "2", "3", "4", "5", "6", "7", "8", "9", "0"],
                ["@", "#", "$", "%", "&", "-", "+", "(", ")", "/"],
                ["*", "\"", "'", ":", ";", "!", "?", "_", "=", "\\"],
                ["ABC", "<", ">", ",", "SPACE", ".", "DEL", "ENTER"]
            ]
        else:
            nums = ["1", "2", "3", "4", "5", "6", "7", "8", "9", "0"]
            r1 = ["Q", "W", "E", "R", "T", "Y", "U", "I", "O", "P"]
            r2 = ["A", "S", "D", "F", "G", "H", "J", "K", "L"]
            r3 = ["SHIFT", "Z", "X", "C", "V", "B", "N", "M", "DEL"]
            r4 = ["?123", ",", "SPACE", ".", "ENTER"]

            if not self.is_shift:
                r1 = [c.lower() for c in r1]
                r2 = [c.lower() for c in r2]
                r3 = ["SHIFT"] + [c.lower() for c in r3[1:-1]] + ["DEL"]

            rows = [nums, r1, r2, r3, r4]

        for row in rows:
            row_box = BoxLayout(orientation="horizontal", spacing=3, size_hint_y=1)
            for k in row:
                btn = self._create_button(k)
                row_box.add_widget(btn)
            self.add_widget(row_box)

    def _create_button(self, label):
        btn_kwargs = {
            "text": label,
            "font_size": "15sp",
            "background_normal": "",
            "color": (0.95, 0.95, 0.98, 1),
        }
        if MONO_FONT_NAME:
            btn_kwargs["font_name"] = MONO_FONT_NAME

        if label == "SPACE":
            btn_kwargs["size_hint_x"] = 3.5
            btn_kwargs["background_color"] = (0.20, 0.23, 0.32, 1)
        elif label == "ENTER":
            btn_kwargs["size_hint_x"] = 2.0
            btn_kwargs["background_color"] = (0.12, 0.35, 0.24, 1)
            btn_kwargs["color"] = (0.35, 0.95, 0.60, 1)
        elif label == "DEL":
            btn_kwargs["size_hint_x"] = 1.6
            btn_kwargs["background_color"] = (0.32, 0.16, 0.22, 1)
            btn_kwargs["color"] = (1.0, 0.65, 0.65, 1)
        elif label == "SHIFT":
            btn_kwargs["size_hint_x"] = 1.6
            shift_active = self.is_shift
            btn_kwargs["background_color"] = (0.28, 0.34, 0.50, 1) if shift_active else (0.16, 0.19, 0.27, 1)
            btn_kwargs["text"] = "▲" if shift_active else "⇧"
        elif label in ("?123", "ABC"):
            btn_kwargs["size_hint_x"] = 1.6
            btn_kwargs["background_color"] = (0.20, 0.24, 0.34, 1)
        else:
            btn_kwargs["size_hint_x"] = 1.0
            btn_kwargs["background_color"] = (0.16, 0.19, 0.27, 1)

        btn = Button(**btn_kwargs)
        btn.bind(on_release=lambda instance, code=label: self._on_btn_click(code))
        return btn

    def _on_btn_click(self, code):
        if code == "SHIFT":
            self.toggle_shift()
        elif code in ("?123", "ABC"):
            self.toggle_symbols()
        elif code == "SPACE":
            self.on_key_callback(" ")
        elif code == "DEL":
            self.on_key_callback("BACKSPACE")
        elif code == "ENTER":
            self.on_key_callback("ENTER")
        else:
            self.on_key_callback(code)


class KivyTerminalApp(App):
    def build(self):
        self.title = "Aurum Trust Bank (Kivy Mobile)"
        self.output_queue = queue.Queue()
        self.input_queue = queue.Queue()
        self.input_active = False
        self.input_buffer = ""
        self.text_content = ""

        # Main Root Layout
        root = BoxLayout(orientation="vertical")
        with root.canvas.before:
            Color(0.06, 0.07, 0.10, 1)  # Deep dark background
            self.root_bg = Rectangle(size=root.size, pos=root.pos)
        root.bind(size=self._update_root_bg, pos=self._update_root_bg)

        # Scrollable Terminal Area (Touch Scroll + Horizontal Scroll Support)
        self.scroll_view = ScrollView(size_hint=(1, 1), do_scroll_x=True, do_scroll_y=True)
        label_kwargs = {
            "text": "[color=888888]Starting Aurum Trust Bank...[/color]\n",
            "font_size": "11.5sp",  # Optimized for clean 38-char mobile column fit
            "markup": True,
            "size_hint":(None, None),
            "valign": "top",
            "halign": "left",
            "color": (0.88, 0.90, 0.95, 1),
        }
        if MONO_FONT_NAME:
            label_kwargs["font_name"] = MONO_FONT_NAME

        self.terminal_label = Label(**label_kwargs)
        # Dynamic label width and height matching texture content
        self.terminal_label.bind(texture_size=self._on_label_resize)

        self.scroll_view.add_widget(self.terminal_label)
        root.add_widget(self.scroll_view)

        # Active typing preview bar
        self.input_bar = BoxLayout(size_hint_y=None, height=36, padding=[10, 4, 10, 4])
        with self.input_bar.canvas.before:
            Color(0.12, 0.14, 0.20, 1)
            self.input_bar_bg = Rectangle(size=self.input_bar.size, pos=self.input_bar.pos)
        self.input_bar.bind(size=self._update_input_bar_bg, pos=self._update_input_bar_bg)

        preview_kwargs = {
            "text": "[color=ebaf2d]Input:[/color] _",
            "font_size": "14sp",
            "markup": True,
            "halign": "left",
            "valign": "middle",
            "size_hint_x": 1,
        }
        if MONO_FONT_NAME:
            preview_kwargs["font_name"] = MONO_FONT_NAME

        self.input_preview_label = Label(**preview_kwargs)
        self.input_preview_label.bind(size=lambda s, sz: s.setter("text_size")(s, (sz[0], sz[1])))
        self.input_bar.add_widget(self.input_preview_label)
        root.add_widget(self.input_bar)

        # Full QWERTY Keyboard
        self.keyboard = QwertyKeyboard(on_key_callback=self.handle_keypad_press)
        root.add_widget(self.keyboard)

        # Schedule output flush (every 1/30s)
        Clock.schedule_interval(self.flush_output, 1.0 / 30.0)

        # Start bank logic in background thread
        self.worker = threading.Thread(target=self.run_worker, daemon=True)
        self.worker.start()

        return root

    def _on_label_resize(self, instance, size):
        instance.width = max(size[0] + 24, self.scroll_view.width)
        instance.height = max(size[1] + 20, self.scroll_view.height)

    def _update_root_bg(self, instance, *args):
        self.root_bg.pos = instance.pos
        self.root_bg.size = instance.size

    def _update_input_bar_bg(self, instance, *args):
        self.input_bar_bg.pos = instance.pos
        self.input_bar_bg.size = instance.size

    def queue_output(self, text):
        self.output_queue.put(text)

    def show_plot_blocking(self, png_bytes):
        """Displays popup on main thread and blocks worker thread until user taps 'Close Graph'."""
        dismiss_ev = threading.Event()
        Clock.schedule_once(lambda dt: self._open_plot_popup(png_bytes, dismiss_ev), 0)
        dismiss_ev.wait()

    def _open_plot_popup(self, png_bytes, dismiss_ev):
        data = io.BytesIO(png_bytes)
        core_img = CoreImage(data, ext="png")
        img_widget = Image(texture=core_img.texture)

        popup_layout = BoxLayout(orientation="vertical", padding=10, spacing=8)
        popup_layout.add_widget(img_widget)
        close_btn = Button(
            text="Close Graph",
            size_hint_y=None,
            height=46,
            background_normal="",
            background_color=(0.85, 0.3, 0.3, 1),
            font_size="16sp",
        )
        popup = Popup(
            title="Account Analytics Graph",
            content=popup_layout,
            size_hint=(0.95, 0.85),
            auto_dismiss=True,
        )
        def on_dismiss(*args):
            popup.dismiss()
            dismiss_ev.set()

        close_btn.bind(on_release=on_dismiss)
        popup.bind(on_dismiss=lambda *args: dismiss_ev.set())
        popup_layout.add_widget(close_btn)
        popup.open()

    def readline(self, prompt=""):
        if prompt:
            self.queue_output(prompt)

        self.input_active = True
        self.input_buffer = ""
        Clock.schedule_once(lambda dt: self._update_input_display(), 0)

        line = self.input_queue.get()
        self.input_active = False
        Clock.schedule_once(lambda dt: self._update_input_display(), 0)
        return line

    def handle_keypad_press(self, key_code):
        if not self.input_active:
            return

        if key_code == "ENTER":
            submitted = self.input_buffer + "\n"
            self.queue_output(self.input_buffer + "\n")
            self.input_buffer = ""
            self._update_input_display()
            self.input_queue.put(submitted)
        elif key_code == "BACKSPACE":
            if self.input_buffer:
                self.input_buffer = self.input_buffer[:-1]
                self._update_input_display()
        else:
            self.input_buffer += key_code
            self._update_input_display()

    def _update_input_display(self):
        if self.input_active:
            self.input_preview_label.text = f"[color=ebaf2d]Input:[/color] {self.input_buffer}[color=ebaf2d]_[/color]"
        else:
            self.input_preview_label.text = "[color=667799]System Processing...[/color]"

    def flush_output(self, dt):
        has_new = False
        while not self.output_queue.empty():
            try:
                chunk = self.output_queue.get_nowait()
                self.text_content += chunk
                has_new = True
            except queue.Empty:
                break

        if has_new:
            # 1. Format wide ASCII boxes into responsive single-column mobile cards
            formatted = format_for_mobile_screen(self.text_content, max_cols=38)

            # 2. Escape Kivy markup special characters
            clean = (
                formatted.replace("&", "&amp;")
                .replace("[", "[[")
                .replace("]", "]]")
            )
            self.terminal_label.text = clean
            self.scroll_view.scroll_y = 0

    def run_worker(self):
        redirector = StdioRedirector(self)
        sys.stdout = redirector
        sys.stderr = redirector
        sys.stdin = redirector

        patch_matplotlib_for_kivy(self)

        import builtins
        def custom_input(prompt=""):
            return self.readline(prompt).rstrip("\r\n")
        builtins.input = custom_input

        try:
            target_file = os.path.join(os.path.dirname(__file__), "ATB EXPERIMENTAL.py")
            if os.path.exists(target_file):
                with open(target_file, "r", encoding="utf-8") as f:
                    code = f.read()
                script_globals = {
                    "__name__": "__main__",
                    "__file__": target_file,
                    "input": custom_input,
                }
                exec(compile(code, target_file, "exec"), script_globals)
            else:
                self.queue_output(f"\nError: Could not find '{target_file}'\n")
        except Exception as e:
            import traceback
            self.queue_output(f"\n{traceback.format_exc()}\n")


if __name__ == "__main__":
    KivyTerminalApp().run()
