# Quick Start Guide

Get up and running with Snip in minutes!

## 1. Install Dependencies

```bash
# Arch Linux / Manjaro / Hyprland users
sudo pacman -S grim slurp wl-clipboard python-gobject gtk4 libadwaita python-pillow python-cairo
```

## 2. Run Snip

**Option A: Run directly (no installation)**
```bash
cd /home/user/snip
./run.sh
```

**Option B: Install system-wide**
```bash
cd /home/user/snip
pip install -e .
snip
```

## 3. Add Hyprland Keybindings

Add to `~/.config/hypr/hyprland.conf`:

```conf
# Quick screenshot keybindings
bind = SUPER SHIFT, A, exec, /home/user/snip/run.sh region --annotate
bind = SUPER SHIFT, S, exec, /home/user/snip/run.sh fullscreen --save
bind = SUPER SHIFT, W, exec, /home/user/snip/run.sh window --pin
bind = SUPER SHIFT, C, exec, /home/user/snip/run.sh region
```

Then reload Hyprland: `Super + Shift + C` and restart

## 4. Usage Examples

```bash
# Select region and annotate
./run.sh region --annotate

# Capture fullscreen and auto-save
./run.sh fullscreen --save

# Capture window and pin it
./run.sh window --pin

# Open GUI selector
./run.sh
```

## Common Workflows

### 1. Quick Screenshot to Clipboard
```bash
./run.sh region
```
- Select area with mouse
- Automatically copied to clipboard
- Paste anywhere with Ctrl+V

### 2. Annotate and Pin
```bash
./run.sh region --annotate
```
- Select area
- Draw arrows, rectangles, etc.
- Click "Pin" to keep it on screen
- Zoom with scroll wheel

### 3. Save Screenshot
```bash
./run.sh fullscreen --save --output ~/my-screenshot.png
```

## Troubleshooting

**"Command not found" errors:**
```bash
# Check dependencies
which grim slurp wl-copy

# If missing, install:
sudo pacman -S grim slurp wl-clipboard
```

**GTK errors:**
```bash
# Test GTK4 installation
python3 -c "import gi; gi.require_version('Gtk', '4.0'); from gi.repository import Gtk; print('OK')"
```

**Not working in Hyprland:**
- Ensure you're in a Wayland session: `echo $XDG_SESSION_TYPE`
- Reload Hyprland config after adding keybindings

## Next Steps

- Read the full [README.md](README.md) for all features
- Customize settings in `~/.config/snip/config.json`
- Create your own keybindings

Enjoy using Snip! 📸
