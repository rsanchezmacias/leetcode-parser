"""
main_gui.py — Desktop UI for LeetCode Formatter.

Run with:
    python main_gui.py
"""

import os
import queue
import subprocess
import sys
import threading
import tkinter as tk
from tkinter import ttk, messagebox, filedialog

# Ensure the project root is on the path when run directly
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from errors.exceptions import InvalidInputException
from models.language import Language
from services.app_launcher import AppLauncher
from services.file_manager import FileManager
from services.leetcode_parser import LeetcodeParser
from services.question_formatter import QuestionFormatter
from utility.url_validator import URLValidator


class App(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("LeetCode Formatter")
        self.resizable(False, False)

        self._url_validator = URLValidator()
        self._question_formatter = QuestionFormatter()
        self._app_launcher = AppLauncher()
        self._file_manager = FileManager()
        self._file_manager.set_working_directory()

        self._log_queue: queue.Queue = queue.Queue()
        self._app_config = None
        self._build_ui()
        self._poll_log()
        # Check config after the window is fully drawn
        self.after(200, self._check_questions_dir)

    # ------------------------------------------------------------------ #
    #  UI construction
    # ------------------------------------------------------------------ #

    def _build_ui(self):
        PAD = 20

        outer = ttk.Frame(self, padding=PAD)
        outer.grid(row=0, column=0, sticky="nsew")

        # ── Header ──────────────────────────────────────────────────────
        ttk.Label(outer, text="LeetCode Formatter", font=("Helvetica", 17, "bold")).grid(
            row=0, column=0, columnspan=2, sticky="w", pady=(0, 4)
        )
        ttk.Label(outer, text="Paste a problem URL and pick a language to get started.",
                  foreground="#888").grid(row=1, column=0, columnspan=2, sticky="w", pady=(0, PAD))

        # ── URL ─────────────────────────────────────────────────────────
        ttk.Label(outer, text="Problem URL").grid(row=2, column=0, columnspan=2, sticky="w")
        self._url_var = tk.StringVar()
        url_entry = ttk.Entry(outer, textvariable=self._url_var, width=58)
        url_entry.grid(row=3, column=0, columnspan=2, sticky="ew", pady=(4, PAD))
        url_entry.focus()

        # ── Language ────────────────────────────────────────────────────
        ttk.Label(outer, text="Language").grid(row=4, column=0, columnspan=2, sticky="w")
        self._lang_var = tk.StringVar(value=Language.PYTHON.value)
        lang_row = ttk.Frame(outer)
        lang_row.grid(row=5, column=0, columnspan=2, sticky="w", pady=(4, PAD))
        ttk.Radiobutton(lang_row, text="Python", variable=self._lang_var,
                        value=Language.PYTHON.value).pack(side="left", padx=(0, 20))
        ttk.Radiobutton(lang_row, text="Swift", variable=self._lang_var,
                        value=Language.SWIFT.value).pack(side="left")

        # ── Output folder ────────────────────────────────────────────────
        ttk.Label(outer, text="Output folder").grid(row=6, column=0, columnspan=2, sticky="w")
        folder_row = ttk.Frame(outer)
        folder_row.grid(row=7, column=0, columnspan=2, sticky="ew", pady=(4, PAD))
        folder_row.columnconfigure(0, weight=1)

        self._folder_var = tk.StringVar(value="Not set")
        folder_label = ttk.Label(folder_row, textvariable=self._folder_var,
                                 foreground="#888", anchor="w")
        folder_label.grid(row=0, column=0, sticky="ew", padx=(0, 8))

        ttk.Button(folder_row, text="Change", width=8,
                   command=self._pick_questions_dir).grid(row=0, column=1, padx=(0, 6))
        ttk.Button(folder_row, text="Open in Finder", width=12,
                   command=self._open_in_finder).grid(row=0, column=2)

        # ── Parse button ────────────────────────────────────────────────
        self._parse_btn = ttk.Button(outer, text="Parse Problem", command=self._on_parse)
        self._parse_btn.grid(row=8, column=0, columnspan=2, sticky="ew", pady=(0, PAD))

        # ── Status log ──────────────────────────────────────────────────
        ttk.Label(outer, text="Status").grid(row=9, column=0, columnspan=2, sticky="w")
        self._log = tk.Text(
            outer, height=12, width=60, state="disabled", wrap="word",
            bg="#1c1c1e", fg="#e5e5ea", insertbackground="white",
            font=("Menlo", 11), relief="flat", padx=8, pady=8,
        )
        self._log.grid(row=10, column=0, columnspan=2, sticky="ew", pady=(4, 0))

    # ------------------------------------------------------------------ #
    #  Helpers
    # ------------------------------------------------------------------ #

    def _poll_log(self):
        """Drain the UI queue, executing each callable on the main thread every 100 ms."""
        try:
            while True:
                fn = self._log_queue.get_nowait()
                fn()
        except queue.Empty:
            pass
        self.after(100, self._poll_log)

    def _dispatch(self, fn):
        """Enqueue any callable to run on the main thread — safe to call from any thread."""
        self._log_queue.put(fn)

    def _log_msg(self, msg: str):
        """Enqueue a log line — safe to call from any thread."""
        def _append():
            self._log.config(state="normal")
            self._log.insert(tk.END, msg + "\n")
            self._log.see(tk.END)
            self._log.config(state="disabled")
        self._dispatch(_append)

    def _clear_log(self):
        """Clear the log widget (call from the main thread only)."""
        self._log.config(state="normal")
        self._log.delete("1.0", tk.END)
        self._log.config(state="disabled")

    def _set_busy(self, busy: bool):
        """Disable the button while parsing — safe to call from any thread."""
        self._dispatch(lambda: self._parse_btn.config(
            state="disabled" if busy else "normal",
            text="Parsing…" if busy else "Parse Problem",
            command=self._on_parse,
        ))

    # ------------------------------------------------------------------ #
    #  Output folder management
    # ------------------------------------------------------------------ #

    def _check_questions_dir(self):
        """Called once on startup — shows folder picker if dir is not yet configured."""
        try:
            self._app_config = self._file_manager.get_app_config()
        except Exception:
            self._app_config = None

        if self._app_config and self._file_manager.is_questions_dir_configured(self._app_config):
            self._folder_var.set(self._app_config.questions_path_directory)
        else:
            messagebox.showinfo(
                "Welcome to LeetCode Formatter",
                "Please choose a folder where your LeetCode files will be saved.",
            )
            self._pick_questions_dir()

    def _pick_questions_dir(self):
        """Open a folder picker and persist the chosen path to config.yaml."""
        chosen = filedialog.askdirectory(title="Choose output folder for LeetCode files")
        if not chosen:
            return

        try:
            self._file_manager.save_questions_dir(chosen)
            # Reload config so the rest of the app sees the new value
            self._app_config = self._file_manager.get_app_config()
            self._folder_var.set(chosen)
        except Exception as e:
            messagebox.showerror("Error", f"Could not save folder setting:\n{e}")

    def _open_in_finder(self):
        """Open the configured output folder in Finder."""
        path = self._folder_var.get()
        if not path or path == "Not set":
            messagebox.showinfo("No folder set", "Please choose an output folder first.")
            return
        if not os.path.exists(path):
            messagebox.showwarning("Folder not found", f"The folder doesn't exist yet:\n{path}")
            return
        subprocess.run(["open", path])

    # ------------------------------------------------------------------ #
    #  Parse action
    # ------------------------------------------------------------------ #

    def _on_parse(self):
        url = self._url_var.get().strip()

        try:
            self._url_validator.validate_url(url)
        except InvalidInputException as e:
            messagebox.showerror("Invalid URL", str(e))
            return

        language = Language(self._lang_var.get())
        self._clear_log()
        self._set_busy(True)
        threading.Thread(target=self._run_parse, args=(url, language), daemon=True).start()

    def _run_parse(self, url: str, language: Language):
        try:
            app_config = self._app_config or self._file_manager.get_app_config()
        except Exception as e:
            self._log_msg(f"❌ Config error: {e}")
            self._set_busy(False)
            return

        try:
            self._log_msg("🔍 Fetching problem from LeetCode…")
            raw_question = LeetcodeParser().parse(url=url, language=language)

            self._log_msg("✏️  Formatting question…")
            formatted_question = self._question_formatter.format_question(raw_question)

            self._log_msg("💾 Writing file…")
            output_path = self._file_manager.write_question_to_template(
                question=formatted_question,
                language=language,
                path=app_config.questions_path_directory,
            )

            self._log_msg(f"✅ Done!\n   {output_path}")

            try:
                self._app_launcher.open(path=output_path, language=language)
            except Exception as e:
                self._log_msg(f"⚠️  Could not open file automatically: {e}")

        except Exception as e:
            self._log_msg(f"❌ Error: {e}")
        finally:
            self._set_busy(False)


if __name__ == "__main__":
    app = App()
    app.mainloop()
