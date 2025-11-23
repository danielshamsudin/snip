#!/usr/bin/env python3
"""Screenshot capture functionality using grim and slurp"""

import subprocess
import tempfile
import os
from pathlib import Path
from datetime import datetime
from typing import Optional, Tuple
from PIL import Image
import io

class ScreenshotCapture:
    """Handles screenshot capture using Wayland tools"""

    def __init__(self, config):
        self.config = config
        self._check_dependencies()

    def _check_dependencies(self):
        """Check if required tools are available"""
        required = ['grim', 'slurp', 'wl-copy']
        missing = []

        for tool in required:
            try:
                subprocess.run(['which', tool], check=True, capture_output=True)
            except subprocess.CalledProcessError:
                missing.append(tool)

        if missing:
            print(f"Warning: Missing dependencies: {', '.join(missing)}")
            print("Install with: sudo pacman -S grim slurp wl-clipboard")

    def capture_region(self) -> Optional[Tuple[Image.Image, str]]:
        """Capture a user-selected region using slurp and grim"""
        try:
            # Use slurp to select region
            slurp_result = subprocess.run(
                ['slurp'],
                capture_output=True,
                text=True
            )

            if slurp_result.returncode != 0:
                # User cancelled
                return None

            geometry = slurp_result.stdout.strip()

            # Capture the selected region with grim
            grim_result = subprocess.run(
                ['grim', '-g', geometry, '-'],
                capture_output=True,
                check=True
            )

            # Load image from bytes
            image = Image.open(io.BytesIO(grim_result.stdout))
            return image, geometry

        except subprocess.CalledProcessError as e:
            print(f"Error capturing region: {e}")
            return None
        except Exception as e:
            print(f"Unexpected error: {e}")
            return None

    def capture_fullscreen(self, output: Optional[str] = None) -> Optional[Image.Image]:
        """Capture the entire screen or specific output"""
        try:
            cmd = ['grim', '-']
            if output:
                cmd.extend(['-o', output])

            result = subprocess.run(cmd, capture_output=True, check=True)
            image = Image.open(io.BytesIO(result.stdout))
            return image

        except subprocess.CalledProcessError as e:
            print(f"Error capturing fullscreen: {e}")
            return None
        except Exception as e:
            print(f"Unexpected error: {e}")
            return None

    def capture_window(self) -> Optional[Image.Image]:
        """Capture active window using slurp with Hyprland"""
        try:
            # Get the active window geometry from Hyprland
            hyprctl_result = subprocess.run(
                ['hyprctl', 'activewindow', '-j'],
                capture_output=True,
                text=True,
                check=True
            )

            import json
            window_info = json.loads(hyprctl_result.stdout)

            # Extract geometry
            x = window_info['at'][0]
            y = window_info['at'][1]
            w = window_info['size'][0]
            h = window_info['size'][1]

            geometry = f"{x},{y} {w}x{h}"

            # Capture with grim
            result = subprocess.run(
                ['grim', '-g', geometry, '-'],
                capture_output=True,
                check=True
            )

            image = Image.open(io.BytesIO(result.stdout))
            return image

        except subprocess.CalledProcessError:
            # Fallback to slurp if hyprctl fails
            print("Hyprctl not available, using slurp for window selection")
            result = self.capture_region()
            return result[0] if result else None
        except Exception as e:
            print(f"Error capturing window: {e}")
            return None

    def save_image(self, image: Image.Image, filename: Optional[str] = None) -> str:
        """Save image to disk"""
        save_dir = Path(self.config.get("screenshot", "save_directory"))
        save_dir.mkdir(parents=True, exist_ok=True)

        if filename is None:
            timestamp = datetime.now().strftime(
                self.config.get("screenshot", "filename_format")
            )
            filename = timestamp

        filepath = save_dir / filename
        image.save(filepath, 'PNG')
        return str(filepath)

    def copy_to_clipboard(self, image: Image.Image):
        """Copy image to clipboard using wl-clipboard"""
        try:
            # Convert PIL Image to PNG bytes
            img_bytes = io.BytesIO()
            image.save(img_bytes, format='PNG')
            img_bytes.seek(0)

            # Copy to clipboard
            subprocess.run(
                ['wl-copy', '--type', 'image/png'],
                input=img_bytes.read(),
                check=True
            )

        except subprocess.CalledProcessError as e:
            print(f"Error copying to clipboard: {e}")
        except Exception as e:
            print(f"Unexpected error: {e}")

    def get_outputs(self) -> list:
        """Get list of available outputs/monitors"""
        try:
            result = subprocess.run(
                ['hyprctl', 'monitors', '-j'],
                capture_output=True,
                text=True,
                check=True
            )

            import json
            monitors = json.loads(result.stdout)
            return [m['name'] for m in monitors]

        except Exception:
            return []
