#!/usr/bin/env python3
"""Main application entry point for Snip"""

import sys
import argparse
import gi
gi.require_version('Gtk', '4.0')
gi.require_version('Gdk', '4.0')
gi.require_version('Adw', '1')
from gi.repository import Gtk, Gio, Adw

from .config import Config
from .screenshot import ScreenshotCapture
from .pin_window import PinWindow
from .annotation import AnnotationWindow

class SnipApplication(Adw.Application):
    """Main application class"""

    def __init__(self):
        super().__init__(
            application_id='com.github.snip',
            flags=Gio.ApplicationFlags.HANDLES_COMMAND_LINE
        )
        self.config = Config()
        self.capture = ScreenshotCapture(self.config)
        self.pin_windows = []

    def do_activate(self):
        """Activate the application"""
        # Show help window if no command given
        if not hasattr(self, 'command_executed'):
            self.show_help_window()

    def do_command_line(self, command_line):
        """Handle command line arguments"""
        parser = argparse.ArgumentParser(description='Snip - Wayland Screenshot Tool')
        parser.add_argument(
            'action',
            nargs='?',
            choices=['region', 'fullscreen', 'window', 'gui'],
            default='gui',
            help='Screenshot action to perform'
        )
        parser.add_argument(
            '--annotate',
            action='store_true',
            help='Open annotation window after capture'
        )
        parser.add_argument(
            '--pin',
            action='store_true',
            help='Pin screenshot after capture'
        )
        parser.add_argument(
            '--save',
            action='store_true',
            help='Save screenshot to file'
        )
        parser.add_argument(
            '--output',
            type=str,
            help='Output file path'
        )

        args = parser.parse_args(command_line.get_arguments()[1:])
        self.command_executed = True

        if args.action == 'region':
            self.capture_region(args)
        elif args.action == 'fullscreen':
            self.capture_fullscreen(args)
        elif args.action == 'window':
            self.capture_window(args)
        elif args.action == 'gui':
            self.show_selector_window()

        self.activate()
        return 0

    def capture_region(self, args):
        """Capture a region of the screen"""
        result = self.capture.capture_region()
        if result:
            image, geometry = result
            self.handle_captured_image(image, args)

    def capture_fullscreen(self, args):
        """Capture the entire screen"""
        image = self.capture.capture_fullscreen()
        if image:
            self.handle_captured_image(image, args)

    def capture_window(self, args):
        """Capture active window"""
        image = self.capture.capture_window()
        if image:
            self.handle_captured_image(image, args)

    def handle_captured_image(self, image, args):
        """Handle captured image based on arguments"""
        # Auto-copy to clipboard if configured
        if self.config.get("screenshot", "copy_to_clipboard"):
            self.capture.copy_to_clipboard(image)

        # Auto-save if configured
        if self.config.get("screenshot", "auto_save") or args.save:
            filepath = self.capture.save_image(image, args.output)
            print(f"Screenshot saved to: {filepath}")

        # Open annotation window
        if args.annotate:
            self.show_annotation_window(image)
        # Pin the image
        elif args.pin:
            self.pin_image(image)
        # Default: open annotation window
        elif not args.save:
            self.show_annotation_window(image)

    def show_annotation_window(self, image):
        """Show the annotation window"""
        window = AnnotationWindow(self, image, self.config)
        window.present()

    def pin_image(self, image):
        """Pin an image on screen"""
        window = PinWindow(self, image, self.config)
        window.present()
        self.pin_windows.append(window)

    def show_selector_window(self):
        """Show the main selector window"""
        window = SelectorWindow(self, self.config)
        window.present()

    def show_help_window(self):
        """Show help window"""
        window = HelpWindow(self)
        window.present()

class SelectorWindow(Gtk.ApplicationWindow):
    """Main window for selecting screenshot type"""

    def __init__(self, application, config):
        super().__init__(application=application)
        self.config = config

        self.set_title("Snip - Screenshot Tool")
        self.set_default_size(400, 300)

        # Create main layout
        box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=20)
        box.set_margin_start(20)
        box.set_margin_end(20)
        box.set_margin_top(20)
        box.set_margin_bottom(20)
        self.set_child(box)

        # Title
        title = Gtk.Label(label="<big><b>Snip Screenshot Tool</b></big>")
        title.set_use_markup(True)
        box.append(title)

        # Description
        desc = Gtk.Label(label="Select screenshot type:")
        box.append(desc)

        # Buttons
        button_box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=10)
        box.append(button_box)

        # Region button
        region_btn = Gtk.Button(label="Capture Region")
        region_btn.connect("clicked", self._on_capture_region)
        button_box.append(region_btn)

        # Fullscreen button
        fullscreen_btn = Gtk.Button(label="Capture Fullscreen")
        fullscreen_btn.connect("clicked", self._on_capture_fullscreen)
        button_box.append(fullscreen_btn)

        # Window button
        window_btn = Gtk.Button(label="Capture Window")
        window_btn.connect("clicked", self._on_capture_window)
        button_box.append(window_btn)

        # Settings label
        settings_label = Gtk.Label(label="<small>Configure in ~/.config/snip/config.json</small>")
        settings_label.set_use_markup(True)
        box.append(settings_label)

    def _on_capture_region(self, button):
        """Capture region"""
        self.hide()
        result = self.get_application().capture.capture_region()
        if result:
            image, geometry = result
            self.get_application().show_annotation_window(image)
        self.close()

    def _on_capture_fullscreen(self, button):
        """Capture fullscreen"""
        self.hide()
        image = self.get_application().capture.capture_fullscreen()
        if image:
            self.get_application().show_annotation_window(image)
        self.close()

    def _on_capture_window(self, button):
        """Capture window"""
        self.hide()
        image = self.get_application().capture.capture_window()
        if image:
            self.get_application().show_annotation_window(image)
        self.close()

class HelpWindow(Gtk.ApplicationWindow):
    """Help/About window"""

    def __init__(self, application):
        super().__init__(application=application)

        self.set_title("Snip - Help")
        self.set_default_size(500, 400)

        # Create scrolled window
        scrolled = Gtk.ScrolledWindow()
        self.set_child(scrolled)

        # Create text view
        text_view = Gtk.TextView()
        text_view.set_editable(False)
        text_view.set_wrap_mode(Gtk.WrapMode.WORD)
        text_view.set_margin_start(10)
        text_view.set_margin_end(10)
        text_view.set_margin_top(10)
        text_view.set_margin_bottom(10)
        scrolled.set_child(text_view)

        # Add help text
        buffer = text_view.get_buffer()
        help_text = """
Snip - Wayland Screenshot Tool

USAGE:
  snip [action] [options]

ACTIONS:
  region       - Capture a selected region
  fullscreen   - Capture entire screen
  window       - Capture active window
  gui          - Show GUI selector (default)

OPTIONS:
  --annotate   - Open annotation window after capture
  --pin        - Pin screenshot after capture
  --save       - Save screenshot to file
  --output     - Specify output file path

EXAMPLES:
  snip region --annotate
  snip fullscreen --save --output ~/screenshot.png
  snip window --pin

KEYBOARD SHORTCUTS (in Pin Window):
  Esc/Q        - Close window
  Ctrl+C       - Copy to clipboard
  Ctrl+S       - Save to file
  Scroll       - Zoom in/out

ANNOTATION TOOLS:
  - Pen: Free-hand drawing
  - Line: Draw straight lines
  - Arrow: Draw arrows
  - Rectangle: Draw rectangles
  - Ellipse: Draw ellipses
  - Text: Add text (planned)

CONFIGURATION:
  Edit ~/.config/snip/config.json to customize:
  - Save directory
  - Default colors
  - Line widths
  - Keyboard shortcuts

DEPENDENCIES:
  - grim: Screenshot capture
  - slurp: Region selection
  - wl-clipboard: Clipboard support
  - hyprctl: Window detection (optional)

Install dependencies:
  sudo pacman -S grim slurp wl-clipboard

HYPRLAND INTEGRATION:
  Add to ~/.config/hypr/hyprland.conf:

  bind = SUPER SHIFT, A, exec, snip region
  bind = SUPER SHIFT, S, exec, snip fullscreen
  bind = SUPER SHIFT, W, exec, snip window
"""
        buffer.set_text(help_text)

def main():
    """Main entry point"""
    app = SnipApplication()
    return app.run(sys.argv)

if __name__ == '__main__':
    sys.exit(main())
