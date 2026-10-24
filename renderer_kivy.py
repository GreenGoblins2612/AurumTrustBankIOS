"""
Aurum Trust Bank - Kivy terminal renderer for Android and iOS.

- Preserves the bank program's original terminal output.
- Does not convert or resize ASCII tables.
- Uses horizontal and vertical touch scrolling.
- Uses the platform's native on-screen keyboard via TextInput.
- Runs bank logic in a worker thread and supports Matplotlib popups.
"""

import sys
import os
import io
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
    from kivy.core.window import Window
    from kivy.core.text import LabelBase
    from kivy.graphics import Color, Rectangle
    from kivy.uix.boxlayout import BoxLayout
    from kivy.uix.scrollview import ScrollView
    from kivy.uix.label import Label
    from kivy.uix.textinput import TextInput
    from kivy.uix.button import Button
    from kivy.uix.popup import Popup
    from kivy.uix.image import Image
    from kivy.core.image import Image as CoreImage
except ImportError as exc:
    print(f"Kivy is not installed: {exc}")
    sys.exit(1)


# Use a monospace font if one is available in the packaged app.
# On iOS/Android, include a .ttf in the app and add its path here
# for guaranteed monospace rendering across devices.
MONO_FONT_CANDIDATES = [
    os.path.join(os.path.dirname(os.path.abspath(__file__)), "DejaVuSansMono.ttf"),
    "/system/fonts/RobotoMono-Regular.ttf",
    "/system/fonts/DroidSansMono.ttf",
    "/System/Library/Fonts/Supplemental/Courier New.ttf",
    "/System/Library/Fonts/Monaco.ttf",
    "/usr/share/fonts/truetype/dejavu/DejaVuSansMono.ttf",
    "C:\\Windows\\Fonts\\consola.ttf",
    "C:\\Windows\\Fonts\\cour.ttf",
]

MONO_FONT_NAME = "Roboto"
for font_path in MONO_FONT_CANDIDATES:
    if os.path.isfile(font_path):
        try:
            LabelBase.register(name="TerminalMono", fn_regular=font_path)
            MONO_FONT_NAME = "TerminalMono"
            break
        except Exception:
            continue


class StdioRedirector:
    def __init__(self, app):
        self.app = app
        self.orig_stdout = sys.stdout
        self.orig_stderr = sys.stderr

    def write(self, value):
        if value:
            self.app.queue_output(value)
            try:
                self.orig_stdout.write(value)
            except Exception:
                pass

    def flush(self):
        try:
            self.orig_stdout.flush()
        except Exception:
            pass

    def readline(self, *args, **kwargs):
        return self.app.readline()


def patch_matplotlib_for_kivy(app):
    """Render Matplotlib figures to PNG and show them in a Kivy popup."""
    try:
        os.environ.setdefault(
            "MPLCONFIGDIR",
            os.path.join(os.path.dirname(os.path.abspath(__file__)), "matplotlib_cache")
        )
        import matplotlib
        matplotlib.use("Agg")
        import matplotlib.pyplot as plt

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
            buffer = io.BytesIO()
            fig.savefig(
                buffer,
                format="png",
                bbox_inches="tight",
                dpi=160,
                facecolor="#ffffff"
            )
            image_bytes = buffer.getvalue()
            plt.close(fig)
            app.show_plot_blocking(image_bytes)

        plt.show = custom_show
    except ImportError:
        pass


class KivyTerminalApp(App):
    def build(self):
        self.title = "Aurum Trust Bank"
        self.output_queue = queue.Queue()
        self.input_queue = queue.Queue()
        self.input_active = False
        self.text_content = ""
        self._input_lock = threading.Lock()

        # Kivy uses the native iOS/Android soft keyboard for TextInput.
        # On iOS the OS manages keyboard placement; on Android this helps
        # move the target into view when the keyboard appears.
        try:
            Window.softinput_mode = "below_target"
        except Exception:
            pass

        root = BoxLayout(orientation="vertical")
        with root.canvas.before:
            Color(0.06, 0.07, 0.10, 1)
            self.root_bg = Rectangle(size=root.size, pos=root.pos)
        root.bind(size=self._update_root_bg, pos=self._update_root_bg)

        self.scroll_view = ScrollView(
            size_hint=(1, 1),
            do_scroll_x=True,
            do_scroll_y=True,
            bar_width="4dp",
            scroll_type=["bars", "content"],
        )

        self.terminal_label = Label(
            text="[color=888888]Starting Aurum Trust Bank...[/color]\n",
            font_name=MONO_FONT_NAME,
            font_size="11sp",
            markup=True,
            size_hint=(None, None),
            halign="left",
            valign="top",
            color=(0.88, 0.90, 0.95, 1),
        )
        self.terminal_label.bind(texture_size=self._on_label_resize)
        self.scroll_view.add_widget(self.terminal_label)
        root.add_widget(self.scroll_view)

        # Native keyboard input field. No custom keyboard is attached.
        self.input_bar = BoxLayout(
            orientation="horizontal",
            size_hint_y=None,
            height="54dp",
            padding=["8dp", "5dp", "8dp", "5dp"],
            spacing="6dp",
        )
        with self.input_bar.canvas.before:
            Color(0.12, 0.14, 0.20, 1)
            self.input_bar_bg = Rectangle(
                size=self.input_bar.size,
                pos=self.input_bar.pos
            )
        self.input_bar.bind(
            size=self._update_input_bar_bg,
            pos=self._update_input_bar_bg
        )

        self.input_field = TextInput(
            hint_text="Waiting for input...",
            multiline=False,
            size_hint=(1, 1),
            font_name=MONO_FONT_NAME,
            font_size="17sp",
            foreground_color=(0.95, 0.95, 0.98, 1),
            hint_text_color=(0.55, 0.58, 0.65, 1),
            background_normal="",
            background_active="",
            background_color=(0.12, 0.14, 0.20, 1),
            cursor_color=(1, 0.7, 0.18, 1),
            padding=["8dp", "10dp", "8dp", "10dp"],
            write_tab=False,
        )
        self.input_field.bind(on_text_validate=self.submit_input)
        self.input_bar.add_widget(self.input_field)
        root.add_widget(self.input_bar)

        Clock.schedule_interval(self.flush_output, 1.0 / 30.0)

        self.worker = threading.Thread(target=self.run_worker, daemon=True)
        self.worker.start()
        return root

    def _on_label_resize(self, instance, texture_size):
        # No forced screen-width text_size: keep each terminal line unwrapped.
        # Label texture width allows horizontal panning to reveal long lines.
        instance.width = max(texture_size[0] + 4, self.scroll_view.width)
        instance.height = max(texture_size[1] + 4, self.scroll_view.height)

    def _update_root_bg(self, instance, *args):
        self.root_bg.pos = instance.pos
        self.root_bg.size = instance.size

    def _update_input_bar_bg(self, instance, *args):
        self.input_bar_bg.pos = instance.pos
        self.input_bar_bg.size = instance.size

    def queue_output(self, value):
        self.output_queue.put(value)

    def flush_output(self, dt):
        changed = False
        while True:
            try:
                chunk = self.output_queue.get_nowait()
            except queue.Empty:
                break
            self.text_content += chunk
            changed = True

        if changed:
            # Escape Kivy markup only; do not transform table rows or spacing.
            safe_text = (
                self.text_content
                .replace("&", "&amp;")
                .replace("[", "[[")
                .replace("]", "]]")
            )
            self.terminal_label.text = safe_text
            self.scroll_view.scroll_y = 0

    def readline(self, prompt=""):
        if prompt:
            self.queue_output(prompt)

        # Set up and focus the input on Kivy's UI thread.
        Clock.schedule_once(lambda dt: self._prepare_input(), 0)
        value = self.input_queue.get()
        return value

    def _prepare_input(self):
        with self._input_lock:
            self.input_active = True
        self.input_field.text = ""
        self.input_field.hint_text = "Enter your response..."
        self.input_field.focus = True

    def submit_input(self, instance):
        with self._input_lock:
            if not self.input_active:
                return
            self.input_active = False

        submitted = instance.text
        instance.text = ""
        instance.focus = False

        # Echo what the user entered, then unblock input().
        self.queue_output(submitted + "\n")
        self.input_queue.put(submitted + "\n")

    def show_plot_blocking(self, png_bytes):
        dismiss_event = threading.Event()
        Clock.schedule_once(
            lambda dt: self._open_plot_popup(png_bytes, dismiss_event),
            0
        )
        dismiss_event.wait()

    def _open_plot_popup(self, png_bytes, dismiss_event):
        core_image = CoreImage(io.BytesIO(png_bytes), ext="png")
        image_widget = Image(texture=core_image.texture)

        layout = BoxLayout(orientation="vertical", padding=10, spacing=8)
        layout.add_widget(image_widget)

        close_button = Button(
            text="Close Graph",
            size_hint_y=None,
            height="46dp",
            background_normal="",
            background_color=(0.85, 0.3, 0.3, 1),
            font_size="16sp",
        )

        popup = Popup(
            title="Account Analytics Graph",
            content=layout,
            size_hint=(0.95, 0.85),
            auto_dismiss=True,
        )
        close_button.bind(on_release=lambda *args: popup.dismiss())
        popup.bind(on_dismiss=lambda *args: dismiss_event.set())
        layout.add_widget(close_button)
        popup.open()

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

        target_dir = os.path.dirname(os.path.abspath(__file__))
        source_path = os.path.join(target_dir, "ATB EXPERIMENTAL.py")
        bytecode_path = os.path.join(target_dir, "ATB EXPERIMENTAL.pyc")

        try:
            script_globals = {
                "__name__": "__main__",
                "__file__": source_path,
                "input": custom_input,
            }

            if os.path.isfile(source_path):
                # Development builds may include the original source file.
                with open(source_path, "r", encoding="utf-8") as source:
                    code = compile(source.read(), source_path, "exec")
            elif os.path.isfile(bytecode_path):
                # kivy-ios can package Python files as .pyc bytecode.
                # Load the bytecode through Python's supported loader rather
                # than assuming the original .py file remains in the bundle.
                from importlib.machinery import SourcelessFileLoader
                loader = SourcelessFileLoader("aurum_atb_entry", bytecode_path)
                code = loader.get_code("aurum_atb_entry")
                if code is None:
                    raise ImportError("Could not load ATB EXPERIMENTAL.pyc")
                script_globals["__file__"] = bytecode_path
            else:
                available = sorted(
                    name for name in os.listdir(target_dir)
                    if name.startswith("ATB EXPERIMENTAL")
                )
                self.queue_output(
                    "\nError: Could not find the bank program.\n"
                    "Looked for ATB EXPERIMENTAL.py and ATB EXPERIMENTAL.pyc.\n"
                    f"Matching bundled files: {available or 'none'}\n"
                )
                return

            exec(code, script_globals)

        except Exception:
            import traceback
            self.queue_output("\n" + traceback.format_exc() + "\n")
        finally:
            # Keep the final message visible. The user explicitly presses
            # Return in the input bar to close the app; never stop on logout.
            self.queue_output(
                "\n\nPress Return when you're ready to close Aurum Trust Bank.\n"
            )
            self.input_queue.get()
            Clock.schedule_once(lambda dt: self.stop(), 0)


if __name__ == "__main__":
    KivyTerminalApp().run()
