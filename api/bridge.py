"""JavaScript bridge for pywebview."""
import logging
from pathlib import Path

log = logging.getLogger(__name__)


class JSBridge:
    """Exposes Python methods to JavaScript via window.pywebview.api."""

    def browse_file(self) -> str:
        """Open native file picker and return selected path."""
        try:
            import tkinter as tk
            from tkinter import filedialog

            root = tk.Tk()
            root.withdraw()  # Hide the main window
            root.attributes("-topmost", True)  # Bring to front

            path = filedialog.askopenfilename(
                title="Select winws.exe",
                filetypes=[("Executable", "*.exe"), ("All files", "*.*")]
            )

            root.destroy()
            return path if path else ""

        except Exception as e:
            log.error("File picker error: %s", e)
            return ""

    def browse_folder(self) -> str:
        """Open native folder picker and return selected path."""
        try:
            import tkinter as tk
            from tkinter import filedialog

            root = tk.Tk()
            root.withdraw()
            root.attributes("-topmost", True)

            path = filedialog.askdirectory(title="Select folder")

            root.destroy()
            return path if path else ""

        except Exception as e:
            log.error("Folder picker error: %s", e)
            return ""

    def get_version(self) -> str:
        """Return app version."""
        return "1.0.0"

    def open_logs_folder(self) -> bool:
        """Open logs folder in file explorer."""
        try:
            import os
            import subprocess
            import sys

            appdata = Path(os.environ.get("APPDATA", Path.home())) / "ZapretUI"
            appdata.mkdir(parents=True, exist_ok=True)

            if sys.platform == "win32":
                os.startfile(str(appdata))
            elif sys.platform == "darwin":
                subprocess.run(["open", str(appdata)])
            else:
                subprocess.run(["xdg-open", str(appdata)])

            return True
        except Exception as e:
            log.error("Failed to open logs folder: %s", e)
            return False
