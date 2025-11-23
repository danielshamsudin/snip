#!/usr/bin/env python3
"""Pin window for displaying screenshots on top"""

import gi
gi.require_version('Gtk', '4.0')
gi.require_version('Gdk', '4.0')
from gi.repository import Gtk, Gdk, GdkPixbuf, Gio
from PIL import Image
import io

class PinWindow(Gtk.ApplicationWindow):
    """A floating window that displays a pinned screenshot"""

    def __init__(self, application, image: Image.Image, config):
        super().__init__(application=application)
        self.image = image
        self.config = config
        self.scale_factor = 1.0
        self.offset_x = 0
        self.offset_y = 0

        # Window setup
        self.set_decorated(False)
        self.set_resizable(True)

        # Create picture widget
        self.picture = Gtk.Picture()
        self.update_image()

        # Create overlay for border
        overlay = Gtk.Overlay()
        overlay.set_child(self.picture)

        # Add drawing area for border
        self.drawing_area = Gtk.DrawingArea()
        self.drawing_area.set_draw_func(self._draw_border)
        overlay.add_overlay(self.drawing_area)

        self.set_child(overlay)

        # Set up drag to move window
        self.drag_controller = Gtk.GestureDrag()
        self.drag_controller.connect("drag-begin", self._on_drag_begin)
        self.drag_controller.connect("drag-update", self._on_drag_update)
        self.add_controller(self.drag_controller)

        # Set up scroll for zoom
        scroll_controller = Gtk.EventControllerScroll()
        scroll_controller.set_flags(Gtk.EventControllerScrollFlags.VERTICAL)
        scroll_controller.connect("scroll", self._on_scroll)
        self.add_controller(scroll_controller)

        # Set up right-click menu
        right_click = Gtk.GestureClick(button=3)
        right_click.connect("pressed", self._show_context_menu)
        self.add_controller(right_click)

        # Keyboard shortcuts
        key_controller = Gtk.EventControllerKey()
        key_controller.connect("key-pressed", self._on_key_pressed)
        self.add_controller(key_controller)

        # Set initial size
        width, height = image.size
        self.set_default_size(width, height)

    def update_image(self):
        """Update the displayed image"""
        # Convert PIL Image to GdkPixbuf
        img_byte_arr = io.BytesIO()
        self.image.save(img_byte_arr, format='PNG')
        img_byte_arr.seek(0)

        loader = GdkPixbuf.PixbufLoader()
        loader.write(img_byte_arr.read())
        loader.close()

        pixbuf = loader.get_pixbuf()

        # Apply scale
        if self.scale_factor != 1.0:
            new_width = int(pixbuf.get_width() * self.scale_factor)
            new_height = int(pixbuf.get_height() * self.scale_factor)
            pixbuf = pixbuf.scale_simple(
                new_width, new_height, GdkPixbuf.InterpType.BILINEAR
            )

        texture = Gdk.Texture.new_for_pixbuf(pixbuf)
        self.picture.set_paintable(texture)

    def _draw_border(self, area, cr, width, height, user_data=None):
        """Draw border around the window"""
        border_width = self.config.get("pin", "border_width", default=2)
        border_color = self.config.get("pin", "border_color", default="#00FF00")

        # Parse color
        color = Gdk.RGBA()
        color.parse(border_color)

        cr.set_source_rgba(color.red, color.green, color.blue, color.alpha)
        cr.set_line_width(border_width)
        cr.rectangle(0, 0, width, height)
        cr.stroke()

    def _on_drag_begin(self, gesture, x, y):
        """Start dragging the window"""
        self.drag_start_x = x
        self.drag_start_y = y

    def _on_drag_update(self, gesture, offset_x, offset_y):
        """Update window position while dragging"""
        surface = self.get_surface()
        if surface:
            # Get current position
            current_x, current_y = surface.get_position()

            # Calculate new position
            new_x = current_x + offset_x
            new_y = current_y + offset_y

            # This doesn't work directly in Wayland, but we keep it for compatibility
            # In Wayland, window positioning is controlled by the compositor

    def _on_scroll(self, controller, dx, dy):
        """Handle scroll for zooming"""
        if dy < 0:
            self.scale_factor *= 1.1
        else:
            self.scale_factor /= 1.1

        # Clamp scale factor
        self.scale_factor = max(0.1, min(5.0, self.scale_factor))

        self.update_image()
        return True

    def _on_key_pressed(self, controller, keyval, keycode, state):
        """Handle keyboard shortcuts"""
        if keyval == Gdk.KEY_Escape or keyval == Gdk.KEY_q:
            self.close()
            return True
        elif keyval == Gdk.KEY_c and state & Gdk.ModifierType.CONTROL_MASK:
            self._copy_to_clipboard()
            return True
        elif keyval == Gdk.KEY_s and state & Gdk.ModifierType.CONTROL_MASK:
            self._save_image()
            return True
        return False

    def _show_context_menu(self, gesture, n_press, x, y):
        """Show context menu on right-click"""
        menu = Gio.Menu()
        menu.append("Copy", "win.copy")
        menu.append("Save", "win.save")
        menu.append("Close", "win.close")

        # Create actions
        copy_action = Gio.SimpleAction.new("copy", None)
        copy_action.connect("activate", lambda a, p: self._copy_to_clipboard())
        self.add_action(copy_action)

        save_action = Gio.SimpleAction.new("save", None)
        save_action.connect("activate", lambda a, p: self._save_image())
        self.add_action(save_action)

        close_action = Gio.SimpleAction.new("close", None)
        close_action.connect("activate", lambda a, p: self.close())
        self.add_action(close_action)

        popover = Gtk.PopoverMenu()
        popover.set_menu_model(menu)
        popover.set_parent(self)
        popover.set_pointing_to(Gdk.Rectangle(x, y, 1, 1))
        popover.popup()

    def _copy_to_clipboard(self):
        """Copy image to clipboard"""
        from .screenshot import ScreenshotCapture
        capture = ScreenshotCapture(self.config)
        capture.copy_to_clipboard(self.image)
        print("Image copied to clipboard")

    def _save_image(self):
        """Save image to file"""
        dialog = Gtk.FileDialog()
        dialog.set_title("Save Screenshot")
        dialog.set_initial_name("screenshot.png")

        dialog.save(self, None, self._on_save_response)

    def _on_save_response(self, dialog, result):
        """Handle save dialog response"""
        try:
            file = dialog.save_finish(result)
            if file:
                filepath = file.get_path()
                self.image.save(filepath, 'PNG')
                print(f"Image saved to {filepath}")
        except Exception as e:
            print(f"Error saving image: {e}")
