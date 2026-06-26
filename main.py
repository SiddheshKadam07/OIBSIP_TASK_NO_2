# ============================================================
#  main.py  –  BMI Calculator Pro  |  Entry Point
#
#  Run:   python main.py
# ============================================================

import tkinter as tk
from tkinter import ttk

from database       import init_db
from gui_calculator import CalculatorTab
from gui_history    import HistoryTab
from gui_trend      import TrendTab
from gui_bulk       import BulkEntryTab
from constants      import BG, CARD, ACCENT, MUTED


class BMIApp(tk.Tk):
    """Root window – hosts the notebook with three tabs."""

    def __init__(self):
        super().__init__()
        self.title("BMI Calculator Pro")
        self.geometry("900x680")
        self.minsize(800, 600)
        self.configure(bg=BG)

        init_db()          # ensure database + table exist
        self._build_ui()

    def _build_ui(self):
        # ── Header bar ────────────────────────────────────────────────────────
        hdr = tk.Frame(self, bg=CARD, height=64)
        hdr.pack(fill="x")
        tk.Label(hdr, text="⚖  BMI Calculator Pro",
                 font=("Helvetica", 20, "bold"),
                 bg=CARD, fg=ACCENT).pack(side="left", padx=24, pady=14)
        tk.Label(hdr, text="Track · Analyse · Improve",
                 font=("Helvetica", 10),
                 bg=CARD, fg=MUTED).pack(side="left", pady=14)

        # ── Notebook style ────────────────────────────────────────────────────
        style = ttk.Style(self)
        style.theme_use("clam")
        style.configure("TNotebook",      background=BG, borderwidth=0)
        style.configure("TNotebook.Tab",  background=CARD, foreground=MUTED,
                        padding=[18, 8],  font=("Helvetica", 10))
        style.map("TNotebook.Tab",
                  background=[("selected", ACCENT)],
                  foreground=[("selected", "#1a1a2e")])

        # ── Notebook ──────────────────────────────────────────────────────────
        nb = ttk.Notebook(self)
        nb.pack(fill="both", expand=True, padx=16, pady=12)

        # Instantiate tabs; CalculatorTab notifies the others on save
        self.tab_history = HistoryTab(nb)
        self.tab_trend   = TrendTab(nb)
        self.tab_calc    = CalculatorTab(nb, on_save_callback=self._on_record_saved)
        self.tab_bulk    = BulkEntryTab(nb, on_save_callback=self._on_record_saved)

        nb.add(self.tab_calc,    text="  Calculator  ")
        nb.add(self.tab_bulk,    text="  Bulk Entry  ")
        nb.add(self.tab_history, text="  History  ")
        nb.add(self.tab_trend,   text="  Trend Analysis  ")

    def _on_record_saved(self):
        """Refresh sibling tabs whenever a new record is saved."""
        self.tab_history.refresh()
        self.tab_trend.refresh_users()


if __name__ == "__main__":
    app = BMIApp()
    app.mainloop()
