# LeetCode Formatter

A macOS app that scrapes a LeetCode problem and drops a pre-filled starter file into a local directory, ready to open in your editor. Supports Python and Swift.

## Prerequisites

- Python 3.13+ with Tcl/Tk support
- Google Chrome + ChromeDriver matching your Chrome version
- `pip install -r requirements.txt && pip install py2app`

### pyenv + Tcl/Tk (one-time fix)

If `import tkinter` fails, reinstall Python with Tcl/Tk support:

```bash
brew install tcl-tk

LDFLAGS="-L$(brew --prefix tcl-tk)/lib" \
CPPFLAGS="-I$(brew --prefix tcl-tk)/include" \
PKG_CONFIG_PATH="$(brew --prefix tcl-tk)/lib/pkgconfig" \
PYTHON_CONFIGURE_OPTS="--with-tcltk-includes='-I$(brew --prefix tcl-tk)/include' \
  --with-tcltk-libs='-L$(brew --prefix tcl-tk)/lib -ltcl8.6 -ltk8.6'" \
pyenv install 3.13.0 --force
```

## Build & Install

```bash
python setup_app.py py2app
cp -r "dist/LeetCode Formatter.app" /Applications/
```

## First Launch

A folder picker will appear — choose where your LeetCode files should be saved. That's the only setup required. Everything else (Chrome profile, config) is handled automatically under `~/Library/Application Support/LeetCodeFormatter/`.

## Usage

1. Paste a LeetCode problem URL
2. Select **Python** or **Swift**
3. Click **Parse Problem** — the status log shows live progress
4. If not logged in, a dialog appears — log in in the Chrome window then click **I'm logged in — Continue**
5. When done, click **Close Chrome**

Use **Change** to update the output folder, or **Open in Finder** to open it at any time.

## Output Structure

```
<output folder>/
└── <difficulty>/
    └── q<number>/
        └── q<CamelCaseTitle>.<ext>
```

> The app only creates files — it never modifies or deletes existing content in your output folder.

## Rebuild After Code Changes

```bash
rm -rf build dist
python setup_app.py py2app
cp -r "dist/LeetCode Formatter.app" /Applications/
```
