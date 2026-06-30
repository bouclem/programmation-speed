#!/usr/bin/env python3
"""Download programming language icons from devicon CDN.

Downloads SVG icons and converts them to PNG (128x128) for use
in benchmark charts. Saves to icons/ directory.

Requires: requests, cairosvg (auto-installed if missing)
"""

import subprocess
import sys
from pathlib import Path

from PIL import Image

ICONS_DIR = Path(__file__).parent.resolve() / "icons"

# devicon CDN URLs — SVG format
ICON_URLS = {
    "c": "https://cdn.jsdelivr.net/gh/devicons/devicon/icons/c/c-original.svg",
    "cpp": "https://cdn.jsdelivr.net/gh/devicons/devicon/icons/cplusplus/cplusplus-original.svg",
    "python": "https://cdn.jsdelivr.net/gh/devicons/devicon/icons/python/python-original.svg",
    "javascript": "https://cdn.jsdelivr.net/gh/devicons/devicon/icons/javascript/javascript-original.svg",
    "vdx": "https://raw.githubusercontent.com/bouclem/vdx/main/website/public/logo.svg",
}

ICON_SIZE = 128


def ensure_cairosvg():
    """Import cairosvg, pip-install if missing."""
    try:
        import cairosvg
        return cairosvg
    except ImportError:
        print("cairosvg not found — installing...")
        subprocess.check_call([sys.executable, "-m", "pip", "install", "cairosvg"])
        import cairosvg
        return cairosvg


def crop_to_content(img, target_size=ICON_SIZE, padding=0.1):
    """Crop image to visible content bbox, then re-center on a square canvas.

    This fixes icons (like VDX) that have lots of transparent padding,
    making the visible logo much smaller than the canvas.
    """
    if img.mode != "RGBA":
        img = img.convert("RGBA")
    bbox = img.getbbox()
    if not bbox:
        return img
    cropped = img.crop(bbox)
    w, h = cropped.size
    side = max(w, h)
    pad = int(side * padding)
    canvas_size = side + 2 * pad
    canvas = Image.new("RGBA", (canvas_size, canvas_size), (0, 0, 0, 0))
    offset = ((canvas_size - w) // 2, (canvas_size - h) // 2)
    canvas.paste(cropped, offset, cropped)
    return canvas.resize((target_size, target_size), Image.LANCZOS)


def download_icons():
    """Download all icons as PNG to icons/ directory, cropped to content."""
    import requests

    cairosvg = ensure_cairosvg()
    ICONS_DIR.mkdir(exist_ok=True)

    for name, url in ICON_URLS.items():
        out_path = ICONS_DIR / f"{name}.png"
        if out_path.exists():
            print(f"  ✓ {name}.png already exists — skipping")
            continue

        print(f"  Downloading {name} from {url}...")
        try:
            resp = requests.get(url, timeout=15)
            resp.raise_for_status()
            svg_data = resp.content
            raw_path = ICONS_DIR / f"{name}_raw.png"
            cairosvg.svg2png(
                bytestring=svg_data,
                write_to=str(raw_path),
                output_width=ICON_SIZE,
                output_height=ICON_SIZE,
            )
            # Crop to content and re-center
            img = Image.open(raw_path)
            img = crop_to_content(img)
            img.save(out_path)
            raw_path.unlink(missing_ok=True)
            print(f"  → Saved: icons/{name}.png ({ICON_SIZE}x{ICON_SIZE}, cropped)")
        except Exception as e:
            print(f"  ✗ Failed to download {name}: {e}")

    print(f"\nDone. Icons saved to {ICONS_DIR}/")


if __name__ == "__main__":
    download_icons()
