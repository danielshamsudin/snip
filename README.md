# Snip 📸

A Snipaste-like screenshot tool built natively for Wayland/Hyprland. Capture, annotate, and pin screenshots with ease!

## ✨ Features

- **📷 Multiple Capture Modes**
  - Region selection (with visual feedback)
  - Fullscreen capture
  - Active window capture

- **📌 Pin Screenshots**
  - Float screenshots on top of other windows
  - Zoom in/out with scroll wheel
  - Drag to reposition
  - Quick access context menu

- **🎨 Annotation Tools**
  - Pen for free-hand drawing
  - Line and arrow tools
  - Rectangle and ellipse shapes
  - Customizable colors and line widths
  - Undo/Clear functionality

- **📋 Quick Actions**
  - Copy to clipboard
  - Save to file
  - Pin on screen
  - All with keyboard shortcuts

- **⚙️ Wayland Native**
  - Built for Wayland compositors
  - Optimized for Hyprland
  - No X11 dependencies

## 🚀 Installation

### Prerequisites

**System Dependencies:**
```bash
# Arch Linux / Manjaro
sudo pacman -S grim slurp wl-clipboard python-gobject gtk4 libadwaita python-pillow python-cairo

# Fedora
sudo dnf install grim slurp wl-clipboard python3-gobject gtk4 libadwaita python3-pillow python3-cairo

# Ubuntu (requires newer repositories for GTK4)
sudo apt install grim slurp wl-clipboard python3-gi python3-gi-cairo gir1.2-gtk-4.0 gir1.2-adw-1 python3-pil
```

### Install Snip

**Option 1: Development Install**
```bash
git clone https://github.com/danielshamsudin/snip.git
cd snip
pip install -e .
```

**Option 2: Direct Install**
```bash
pip install git+https://github.com/danielshamsudin/snip.git
```

**Option 3: Run Without Installing**
```bash
git clone https://github.com/danielshamsudin/snip.git
cd snip
python -m snip.main
```

## 🎮 Usage

### Command Line

```bash
# Show GUI selector
snip

# Capture region and annotate
snip region --annotate

# Capture fullscreen and save
snip fullscreen --save

# Capture window and pin
snip window --pin

# Capture region, save to specific location
snip region --save --output ~/my-screenshot.png

# Show help
snip --help
```

### Hyprland Integration

Add these keybindings to your `~/.config/hypr/hyprland.conf`:

```conf
# Screenshot keybindings
bind = SUPER SHIFT, A, exec, snip region --annotate
bind = SUPER SHIFT, S, exec, snip fullscreen --save
bind = SUPER SHIFT, W, exec, snip window --pin
bind = SUPER SHIFT, X, exec, snip region --save

# Quick clipboard screenshot
bind = SUPER SHIFT, C, exec, snip region
```

### Keyboard Shortcuts

**In Pin Window:**
- `Esc` or `Q` - Close window
- `Ctrl+C` - Copy to clipboard
- `Ctrl+S` - Save to file
- `Scroll` - Zoom in/out
- `Right-click` - Context menu

**In Annotation Window:**
- Various tools available in toolbar
- `Undo` - Remove last annotation
- `Clear` - Remove all annotations

## ⚙️ Configuration

Snip creates a configuration file at `~/.config/snip/config.json`. You can customize:

```json
{
  "screenshot": {
    "save_directory": "~/Pictures/Snip",
    "filename_format": "snip_%Y%m%d_%H%M%S.png",
    "copy_to_clipboard": true,
    "auto_save": false
  },
  "shortcuts": {
    "capture_region": "Super+Shift+A",
    "capture_fullscreen": "Super+Shift+S",
    "capture_window": "Super+Shift+W"
  },
  "annotation": {
    "default_color": "#FF0000",
    "default_line_width": 3,
    "font_size": 14,
    "font_family": "Sans"
  },
  "pin": {
    "border_width": 2,
    "border_color": "#00FF00",
    "always_on_top": true
  }
}
```

## 🎨 Annotation Tools

| Tool | Description |
|------|-------------|
| **Pen** | Free-hand drawing |
| **Line** | Draw straight lines |
| **Arrow** | Draw arrows with heads |
| **Rectangle** | Draw rectangular shapes |
| **Ellipse** | Draw circular/elliptical shapes |
| **Color Picker** | Choose annotation color |
| **Line Width** | Adjust stroke width (1-20px) |

## 🔧 Troubleshooting

### Missing Dependencies

If you see "Missing dependencies" warnings:

```bash
# Check which tools are missing
which grim slurp wl-copy

# Install missing tools (Arch)
sudo pacman -S grim slurp wl-clipboard
```

### GTK/GObject Errors

Ensure you have the correct Python GObject bindings:

```bash
# Verify installation
python -c "import gi; gi.require_version('Gtk', '4.0'); from gi.repository import Gtk; print('GTK4 OK')"
```

### Wayland Session Required

Snip requires a Wayland session. Verify with:

```bash
echo $XDG_SESSION_TYPE  # Should output "wayland"
```

### Hyprctl Not Found

Window capture uses `hyprctl` for Hyprland. If not available, it falls back to region selection.

## 🤝 Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## 📝 License

MIT License - see LICENSE file for details

## 🙏 Credits

- Inspired by [Snipaste](https://www.snipaste.com/)
- Uses [grim](https://sr.ht/~emersion/grim/) for Wayland screenshots
- Uses [slurp](https://github.com/emersion/slurp) for region selection
- Built with GTK4 and Python

## 🔗 Similar Projects

- [Flameshot](https://flameshot.org/) - X11 screenshot tool
- [Swappy](https://github.com/jtheoof/swappy) - Wayland snapshot editor
- [Grimblast](https://github.com/hyprwm/contrib) - Hyprland screenshot script

---

**Note:** This is a native Wayland application designed for Hyprland and other wlroots-based compositors. It will not work on X11 sessions.
