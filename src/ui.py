import threading
import tkinter as tk
from tkinter import filedialog, scrolledtext
from collections.abc import Callable

_BASE_TITLE = "Mockwise"


class App(tk.Tk):
    def __init__(self, on_import: Callable[[str, Callable[[str], None], Callable[[int, int], None]], None]):
        super().__init__()
        self.title(_BASE_TITLE)
        self.resizable(True, True)
        self._on_import = on_import
        self._build()
        w = self.winfo_screenwidth() // 2
        h = self.winfo_screenheight() // 2
        self.geometry(f"{w}x{h}")

    def _build(self) -> None:
        # File picker row: [path text box] [Browse] [Run]
        row = tk.Frame(self)
        row.pack(padx=16, pady=8, fill="x")

        self._path_var = tk.StringVar()
        self._path_entry = tk.Entry(row, textvariable=self._path_var, state="readonly", width=44)
        self._path_entry.pack(side="left", fill="x", expand=True)

        self._browse_btn = tk.Button(row, text="Browse", width=8, command=self._browse)
        self._browse_btn.pack(side="left", padx=(6, 0))

        self._run_btn = tk.Button(row, text="Run", width=6, command=self._run_click, state="disabled")
        self._run_btn.pack(side="left", padx=(4, 0))

        tk.Label(self, text="Status:", anchor="w").pack(fill="x", padx=16)

        self._status = scrolledtext.ScrolledText(
            self,
            width=64,
            height=18,
            state="disabled",
            wrap="word",
            font=("Consolas", 9),
        )
        self._status.pack(padx=16, pady=(2, 16), fill="both", expand=True)
        self.columnconfigure(0, weight=1)
        self.rowconfigure(1, weight=1)

    def _browse(self) -> None:
        path = filedialog.askopenfilename(
            title="Select Excel file",
            filetypes=[("Excel files", "*.xlsx")],
        )
        if not path:
            return
        self._path_var.set(path)
        self._run_btn.config(state="normal")

    def _run_click(self) -> None:
        path = self._path_var.get()
        if not path:
            return
        self._browse_btn.config(state="disabled")
        self._run_btn.config(state="disabled")
        self._clear_status()
        self.append_status(f"File: {path}")
        self.append_status("-" * 52)
        self.attributes("-topmost", True)   # float above the target application
        threading.Thread(target=self._worker, args=(path,), daemon=True).start()

    def _worker(self, path: str) -> None:
        try:
            self._on_import(path, self.append_status, self.set_progress)
        except Exception as exc:
            self.append_status(f"Unexpected error: {exc}")
        finally:
            self.after(0, self._on_done)

    def _on_done(self) -> None:
        self._restore_buttons()
        self.attributes("-topmost", False)  # return to normal z-order when finished

    def _restore_buttons(self) -> None:
        self._browse_btn.config(state="normal")
        self._run_btn.config(state="normal")
        self.title(_BASE_TITLE)

    def set_progress(self, done: int, total: int) -> None:
        """Update the title bar with current row progress. Safe to call from any thread."""
        pct = int(done / total * 100) if total else 0
        new_title = f"{_BASE_TITLE}  —  {done}/{total}  ({pct}% done)"
        self.after(0, lambda t=new_title: self.title(t))

    def _clear_status(self) -> None:
        self._status.config(state="normal")
        self._status.delete("1.0", "end")
        self._status.config(state="disabled")

    def append_status(self, message: str) -> None:
        def _update() -> None:
            self._status.config(state="normal")
            self._status.insert("end", message + "\n")
            self._status.see("end")
            self._status.config(state="disabled")

        self.after(0, _update)
