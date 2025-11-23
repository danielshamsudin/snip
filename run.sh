#!/bin/bash
# Quick run script for Snip without installation

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$SCRIPT_DIR"

# Check Python version
python_version=$(python3 --version 2>&1 | awk '{print $2}' | cut -d. -f1,2)
required_version="3.8"

if [ "$(printf '%s\n' "$required_version" "$python_version" | sort -V | head -n1)" != "$required_version" ]; then
    echo "Error: Python $required_version or higher is required"
    exit 1
fi

# Check for dependencies
missing_deps=()

for cmd in grim slurp wl-copy; do
    if ! command -v "$cmd" &> /dev/null; then
        missing_deps+=("$cmd")
    fi
done

if [ ${#missing_deps[@]} -gt 0 ]; then
    echo "Warning: Missing dependencies: ${missing_deps[*]}"
    echo "Install with: sudo pacman -S grim slurp wl-clipboard"
    echo ""
fi

# Check for Python dependencies
if ! python3 -c "import gi" &> /dev/null; then
    echo "Error: PyGObject not installed"
    echo "Install with: sudo pacman -S python-gobject gtk4"
    exit 1
fi

# Run the application
export PYTHONPATH="$SCRIPT_DIR:$PYTHONPATH"
python3 -m snip.main "$@"
