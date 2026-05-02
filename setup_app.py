"""
setup_app.py — Builds the macOS app bundle using py2app.

Usage:
    pip install py2app
    python setup_app.py py2app

The finished app is written to:
    dist/LeetCode Formatter.app

Drag it to /Applications to install.
"""

from setuptools import setup

APP = ["main_gui.py"]

# Data files bundled into Contents/Resources/
DATA_FILES = [
    ("templates", [
        "templates/base_py.j2",
        "templates/base_swift.j2",
    ]),
]

OPTIONS = {
    "argv_emulation": False,
    # Third-party packages
    "packages": [
        "selenium",
        "jinja2",
        "yaml",
        # Local packages — py2app must copy these as whole directories
        "models",
        "services",
        "utility",
        "errors",
    ],
    "includes": [
        "tkinter",
        "tkinter.ttk",
    ],
    "plist": {
        "CFBundleName": "LeetCode Formatter",
        "CFBundleDisplayName": "LeetCode Formatter",
        "CFBundleIdentifier": "com.leetcode-formatter",
        "CFBundleVersion": "1.0.0",
        "CFBundleShortVersionString": "1.0.0",
        "NSHighResolutionCapable": True,
        # Allow outbound network connections (needed for Selenium / ChromeDriver)
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
