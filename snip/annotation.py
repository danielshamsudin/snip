#!/usr/bin/env python3
"""Annotation tools for screenshots"""

import gi
gi.require_version('Gtk', '4.0')
gi.require_version('Gdk', '4.0')
from gi.repository import Gtk, Gdk, GdkPixbuf, Gio
from PIL import Image, ImageDraw, ImageFont
import io
from enum import Enum

class AnnotationTool(Enum):
    """Available annotation tools"""
    NONE = 0
    PEN = 1
    LINE = 2
    ARROW = 3
    RECTANGLE = 4
    ELLIPSE = 5
    TEXT = 6
    HIGHLIGHTER = 7

class AnnotationWindow(Gtk.ApplicationWindow):
    """Window for annotating screenshots before pinning"""

    def __init__(self, application, image: Image.Image, config):
        super().__init__(application=application)
        self.original_image = image.copy()
        self.image = image.copy()
        self.config = config

        self.current_tool = AnnotationTool.PEN
        self.current_color = config.get("annotation", "default_color", default="#FF0000")
        self.line_width = config.get("annotation", "default_line_width", default=3)

        self.drawing = False
        self.start_x = 0
        self.start_y = 0
        self.points = []

        self.set_title("Annotate Screenshot")
        self.set_default_size(image.width, image.height)

        # Create main layout
        main_box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL)
        self.set_child(main_box)

        # Toolbar
        toolbar = self._create_toolbar()
        main_box.append(toolbar)

        # Drawing area
        self.drawing_area = Gtk.DrawingArea()
        self.drawing_area.set_draw_func(self._on_draw)
        self.drawing_area.set_vexpand(True)
        main_box.append(self.drawing_area)

        # Set up mouse events
        drag = Gtk.GestureDrag()
        drag.connect("drag-begin", self._on_drag_begin)
        drag.connect("drag-update", self._on_drag_update)
        drag.connect("drag-end", self._on_drag_end)
        self.drawing_area.add_controller(drag)

        # Bottom action bar
        action_bar = self._create_action_bar()
        main_box.append(action_bar)

    def _create_toolbar(self) -> Gtk.Box:
        """Create the toolbar with annotation tools"""
        toolbar = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=5)
        toolbar.set_margin_start(5)
        toolbar.set_margin_end(5)
        toolbar.set_margin_top(5)
        toolbar.set_margin_bottom(5)

        # Tool buttons
        tools = [
            ("Pen", AnnotationTool.PEN),
            ("Line", AnnotationTool.LINE),
            ("Arrow", AnnotationTool.ARROW),
            ("Rectangle", AnnotationTool.RECTANGLE),
            ("Ellipse", AnnotationTool.ELLIPSE),
            ("Text", AnnotationTool.TEXT),
        ]

        for label, tool in tools:
            button = Gtk.Button(label=label)
            button.connect("clicked", lambda b, t=tool: self._set_tool(t))
            toolbar.append(button)

        # Color picker
        color_button = Gtk.ColorButton()
        rgba = Gdk.RGBA()
        rgba.parse(self.current_color)
        color_button.set_rgba(rgba)
        color_button.connect("color-set", self._on_color_changed)
        toolbar.append(color_button)

        # Line width adjustment
        line_width_label = Gtk.Label(label="Width:")
        toolbar.append(line_width_label)

        line_width_spin = Gtk.SpinButton()
        line_width_spin.set_range(1, 20)
        line_width_spin.set_value(self.line_width)
        line_width_spin.set_increments(1, 5)
        line_width_spin.connect("value-changed", self._on_line_width_changed)
        toolbar.append(line_width_spin)

        # Undo button
        undo_button = Gtk.Button(label="Undo")
        undo_button.connect("clicked", self._on_undo)
        toolbar.append(undo_button)

        # Clear button
        clear_button = Gtk.Button(label="Clear")
        clear_button.connect("clicked", self._on_clear)
        toolbar.append(clear_button)

        return toolbar

    def _create_action_bar(self) -> Gtk.Box:
        """Create the action bar with save/copy/pin buttons"""
        action_bar = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=10)
        action_bar.set_margin_start(10)
        action_bar.set_margin_end(10)
        action_bar.set_margin_top(5)
        action_bar.set_margin_bottom(10)
        action_bar.set_halign(Gtk.Align.CENTER)

        # Save button
        save_button = Gtk.Button(label="Save")
        save_button.connect("clicked", self._on_save)
        action_bar.append(save_button)

        # Copy button
        copy_button = Gtk.Button(label="Copy")
        copy_button.connect("clicked", self._on_copy)
        action_bar.append(copy_button)

        # Pin button
        pin_button = Gtk.Button(label="Pin")
        pin_button.connect("clicked", self._on_pin)
        action_bar.append(pin_button)

        # Cancel button
        cancel_button = Gtk.Button(label="Cancel")
        cancel_button.connect("clicked", lambda b: self.close())
        action_bar.append(cancel_button)

        return action_bar

    def _set_tool(self, tool: AnnotationTool):
        """Set the current annotation tool"""
        self.current_tool = tool

    def _on_color_changed(self, color_button):
        """Handle color change"""
        rgba = color_button.get_rgba()
        self.current_color = f"#{int(rgba.red*255):02x}{int(rgba.green*255):02x}{int(rgba.blue*255):02x}"

    def _on_line_width_changed(self, spin_button):
        """Handle line width change"""
        self.line_width = int(spin_button.get_value())

    def _on_drag_begin(self, gesture, x, y):
        """Start drawing"""
        self.drawing = True
        self.start_x = x
        self.start_y = y
        self.points = [(x, y)]

    def _on_drag_update(self, gesture, offset_x, offset_y):
        """Update drawing"""
        if self.drawing:
            x = self.start_x + offset_x
            y = self.start_y + offset_y
            self.points.append((x, y))
            self.drawing_area.queue_draw()

    def _on_drag_end(self, gesture, offset_x, offset_y):
        """Finish drawing"""
        if self.drawing:
            end_x = self.start_x + offset_x
            end_y = self.start_y + offset_y
            self._apply_annotation(self.start_x, self.start_y, end_x, end_y)
            self.drawing = False
            self.points = []
            self.drawing_area.queue_draw()

    def _apply_annotation(self, start_x, start_y, end_x, end_y):
        """Apply the annotation to the image"""
        draw = ImageDraw.Draw(self.image)

        if self.current_tool == AnnotationTool.PEN:
            if len(self.points) > 1:
                draw.line(self.points, fill=self.current_color, width=self.line_width)

        elif self.current_tool == AnnotationTool.LINE:
            draw.line(
                [(start_x, start_y), (end_x, end_y)],
                fill=self.current_color,
                width=self.line_width
            )

        elif self.current_tool == AnnotationTool.ARROW:
            # Draw line
            draw.line(
                [(start_x, start_y), (end_x, end_y)],
                fill=self.current_color,
                width=self.line_width
            )
            # Draw arrowhead (simplified)
            import math
            angle = math.atan2(end_y - start_y, end_x - start_x)
            arrow_length = 15
            arrow_angle = math.pi / 6

            point1_x = end_x - arrow_length * math.cos(angle - arrow_angle)
            point1_y = end_y - arrow_length * math.sin(angle - arrow_angle)
            point2_x = end_x - arrow_length * math.cos(angle + arrow_angle)
            point2_y = end_y - arrow_length * math.sin(angle + arrow_angle)

            draw.line([(end_x, end_y), (point1_x, point1_y)], fill=self.current_color, width=self.line_width)
            draw.line([(end_x, end_y), (point2_x, point2_y)], fill=self.current_color, width=self.line_width)

        elif self.current_tool == AnnotationTool.RECTANGLE:
            draw.rectangle(
                [(start_x, start_y), (end_x, end_y)],
                outline=self.current_color,
                width=self.line_width
            )

        elif self.current_tool == AnnotationTool.ELLIPSE:
            draw.ellipse(
                [(start_x, start_y), (end_x, end_y)],
                outline=self.current_color,
                width=self.line_width
            )

    def _on_draw(self, area, cr, width, height, user_data=None):
        """Draw the image and current annotations"""
        # Convert PIL Image to surface
        img_byte_arr = io.BytesIO()
        self.image.save(img_byte_arr, format='PNG')
        img_byte_arr.seek(0)

        loader = GdkPixbuf.PixbufLoader()
        loader.write(img_byte_arr.read())
        loader.close()

        pixbuf = loader.get_pixbuf()
        texture = Gdk.Texture.new_for_pixbuf(pixbuf)

        # Draw the image
        texture.download(cr.get_target().get_data(), cr.get_target().get_stride())

    def _on_undo(self, button):
        """Undo last annotation"""
        self.image = self.original_image.copy()
        self.drawing_area.queue_draw()

    def _on_clear(self, button):
        """Clear all annotations"""
        self.image = self.original_image.copy()
        self.drawing_area.queue_draw()

    def _on_save(self, button):
        """Save the annotated image"""
        from .screenshot import ScreenshotCapture
        capture = ScreenshotCapture(self.config)
        filepath = capture.save_image(self.image)
        print(f"Image saved to {filepath}")
        self.close()

    def _on_copy(self, button):
        """Copy the annotated image to clipboard"""
        from .screenshot import ScreenshotCapture
        capture = ScreenshotCapture(self.config)
        capture.copy_to_clipboard(self.image)
        print("Image copied to clipboard")
        self.close()

    def _on_pin(self, button):
        """Pin the annotated image"""
        from .pin_window import PinWindow
        pin_win = PinWindow(self.get_application(), self.image, self.config)
        pin_win.present()
        self.close()
