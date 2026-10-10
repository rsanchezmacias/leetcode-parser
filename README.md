# LeetCode Formatter

A macOS app that fetches a LeetCode problem and drops a pre-filled starter file into a local directory, ready to open in your editor. Supports Python and Swift.

## Prerequisites

- Python 3.13+ — if using pyenv, install with Tcl/Tk support:
    ```bash
    brew install tcl-tk

    LDFLAGS="-L$(brew --prefix tcl-tk)/lib" \
    CPPFLAGS="-I$(brew --prefix tcl-tk)/include" \
    PKG_CONFIG_PATH="$(brew --prefix tcl-tk)/lib/pkgconfig" \
    PYTHON_CONFIGURE_OPTS="--with-tcltk-includes='-I$(brew --prefix tcl-tk)/include' \
      --with-tcltk-libs='-L$(brew --prefix tcl-tk)/lib -ltcl8.6 -ltk8.6'" \
    pyenv install 3.13.0 --force
    ```
- Google Chrome, logged into leetcode.com, for Premium problems (optional)
- `pip install -r requirements.txt && pip install py2app`

## Build & Install

```bash
python setup_app.py py2app
cp -r "dist/LeetCode Formatter.app" /Applications/
```

After rebuilding, macOS may forget the app's Full Disk Access (and Keychain) permission; re-enable it in System Settings → Privacy & Security → Full Disk Access.

## First Launch

A folder picker will appear — choose where your LeetCode files should be saved. That's the only setup required. Everything else (config) is handled automatically under `~/Library/Application Support/LeetCodeFormatter/`.

## Usage

1. Paste a LeetCode problem URL
2. Select **Python** or **Swift**
3. Click **Parse Problem**. The file is created and opened.

For Premium problems, stay logged into leetcode.com in Chrome. The first time, macOS asks to allow access to "Chrome Safe Storage"; click **Allow** (you are asked each time a Premium problem is fetched). **Always Allow** stops the prompts but lets any app on the Mac read Chrome's cookie encryption key without asking, so choose it only if you accept that. Because macOS protects Chrome's data, the app (or Terminal, when using the CLI) also needs **Full Disk Access** in System Settings → Privacy & Security → Full Disk Access.

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
