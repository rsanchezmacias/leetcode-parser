"""
setup_app.py — Builds the macOS app bundle using py2app.

Usage:
    pip install py2app Pillow
    python setup_app.py py2app

The finished app is written to:
    dist/LeetCode Formatter.app

Drag it to /Applications to install.
"""

import io
import os
import struct
import sys

from setuptools import setup

# ── Icon generation ────────────────────────────────────────────────────────────

def _build_icon() -> str:
    """Render icon.icns next to this script and return its path."""
    try:
        from PIL import Image, ImageDraw, ImageFont
    except ImportError:
        print("Pillow is required to generate the icon: pip install Pillow")
        sys.exit(1)

    BG     = (26, 26, 26, 255)
    ORANGE = (255, 161, 22, 255)

    font_candidates = [
        "/usr/share/fonts/opentype/urw-base35/NimbusMonoPS-Bold.otf",   # Linux
        "/System/Library/Fonts/Supplemental/Courier New Bold.ttf",       # macOS
        "/Library/Fonts/Courier New Bold.ttf",
        "/System/Library/Fonts/Monaco.ttf",
    ]

    def find_font(size):
        for path in font_candidates:
            if os.path.exists(path):
                return ImageFont.truetype(path, size)
        raise RuntimeError("No monospace font found. Install one of: " + ", ".join(font_candidates))

    def render(px):
        img  = Image.new("RGBA", (px, px), (0, 0, 0, 0))
        draw = ImageDraw.Draw(img)
        draw.rounded_rectangle([(0, 0), (px - 1, px - 1)], radius=int(px * 0.22), fill=BG)
        font = find_font(int(px * 0.42))
        text = "</>"
        bbox = draw.textbbox((0, 0), text, font=font)
        draw.text(
            ((px - (bbox[2] - bbox[0])) / 2 - bbox[0],
             (px - (bbox[3] - bbox[1])) / 2 - bbox[1]),
            text, fill=ORANGE, font=font,
        )
        buf = io.BytesIO()
        img.save(buf, format="PNG")
        return buf.getvalue()

    entries = [
        (b"icp4",   16), (b"icp5",  32), (b"icp6",   64),
        (b"ic07",  128), (b"ic08", 256), (b"ic09",  512), (b"ic10", 1024),
    ]

    chunks = b"".join(
        t + struct.pack(">I", 8 + len(d)) + d
        for t, d in ((ot, render(px)) for ot, px in entries)
    )
    total    = 8 + len(chunks)
    icns_path = os.path.join(os.path.dirname(__file__), "icon.icns")
    with open(icns_path, "wb") as f:
        f.write(b"icns" + struct.pack(">I", total) + chunks)

    print(f"icon.icns generated ({total // 1024} KB)")
    return icns_path


# Generate icon before py2app reads OPTIONS
_build_icon()

# ── py2app configuration ───────────────────────────────────────────────────────

APP = ["main_gui.py"]

DATA_FILES = [
    ("templates", [
        "templates/base_py.j2",
        "templates/base_swift.j2",
    ]),
]

OPTIONS = {
    "argv_emulation": False,
    "packages": [
        "selenium", "jinja2", "yaml",
        "models", "services", "utility", "errors",
    ],
    "includes": ["tkinter", "tkinter.ttk"],
    "iconfile": "icon.icns",
    "plist": {
        "CFBundleName": "LeetCode Formatter",
        "CFBundleDisplayName": "LeetCode Formatter",
        "CFBundleIdentifier": "com.leetcode-formatter",
        "CFBundleVersion": "1.0.0",
        "CFBundleShortVersionString": "1.0.0",
        "NSHighResolutionCapable": True,
        "NSAppTransportSecurity": {"NSAllowsArbitraryLoads": True},
    },
}

setup(
    name="LeetCode Formatter",
    app=APP,
    data_files=DATA_FILES,
    options={"py2app": OPTIONS},
    setup_requires=["py2app"],
)
