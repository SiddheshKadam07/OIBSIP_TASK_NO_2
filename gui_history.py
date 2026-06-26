# ============================================================
#  gui_history.py  –  History Tab (Tkinter Frame)
# ============================================================

import tkinter as tk
from tkinter import ttk, messagebox
from database import get_all_users, get_records_for_user, get_all_records, delete_all_records
from constants import BG, CARD, ACCENT, TEXT, MUTED, ENTRY_BG


class HistoryTab(tk.Frame):
    """
    Second tab – shows all saved BMI records in a sortable table.
    Supports filtering by user and deleting all records.
    """

    def __init__(self, parent, **kwargs):
        super().__init__(parent, bg=BG, **kwargs)
        self._build()

    def _build(self):
        # ── Filter bar ────────────────────────────────────────────────────────
        ff = tk.Frame(self, bg=BG)
        ff.pack(fill="x", padx=16, pady=(12, 6))

        tk.Label(ff, text="Filter by user:", bg=BG, fg=MUTED,
                 font=("Helvetica", 10)).pack(side="left")

        self.filter_var = tk.StringVar(value="All")
        self.user_combo = ttk.Combobox(ff, textvariable=self.filter_var,
                                        state="readonly", width=20)
        self.user_combo.pack(side="left", padx=8)
        self.user_combo.bind("<<ComboboxSelected>>", lambda _e: self.refresh())

        tk.Button(ff, text="↻  Refresh", bg=ENTRY_BG, fg=MUTED,
                  relief="flat", font=("Helvetica", 10), cursor="hand2",
                  command=self.refresh).pack(side="left", padx=4, ipady=3)

        tk.Button(ff, text="🗑  Clear All Records", bg="#6b2020", fg=TEXT,
                  relief="flat", font=("Helvetica", 10), cursor="hand2",
                  command=self._clear_all).pack(side="right", padx=4, ipady=3)

        # ── Treeview ──────────────────────────────────────────────────────────
        style = ttk.Style()
        style.configure("Hist.Treeview",
                        background=CARD, foreground=TEXT,
                        fieldbackground=CARD, rowheight=26,
                        font=("Helvetica", 10))
        style.configure("Hist.Treeview.Heading",
                        background=ENTRY_BG, foreground=ACCENT,
                        font=("Helvetica", 10, "bold"))
        style.map("Hist.Treeview",
                  background=[("selected", ACCENT)],
                  foreground=[("selected", "#1a1a2e")])

        columns = ("ID", "User", "Weight (kg)", "Height (m)",
                   "BMI", "Category", "Date")
        frame_t = tk.Frame(self, bg=BG)
        frame_t.pack(fill="both", expand=True, padx=16, pady=6)

        vsb = ttk.Scrollbar(frame_t, orient="vertical")
        self.tree = ttk.Treeview(frame_t, columns=columns, show="headings",
                                  style="Hist.Treeview", yscrollcommand=vsb.set)
        vsb.config(command=self.tree.yview)
        vsb.pack(side="right", fill="y")
        self.tree.pack(fill="both", expand=True)

        widths = [40, 130, 95, 95, 70, 110, 140]
        for col, w in zip(columns, widths):
            self.tree.heading(col, text=col,
                              command=lambda c=col: self._sort_by(c))
            self.tree.column(col, width=w, anchor="center")

        # colour tags per category
        self._cat_colors = {
            "Normal":      "#2ecc71",
            "Underweight": "#3498db",
            "Overweight":  "#f39c12",
            "Obese":       "#e74c3c",
        }
        for cat, col in self._cat_colors.items():
            self.tree.tag_configure(cat, foreground=col)

        self.refresh()

    # ── Public ────────────────────────────────────────────────────────────────
    def refresh(self):
        """Reload user list and records from the database."""
        users = ["All"] + get_all_users()
        self.user_combo["values"] = users
        if self.filter_var.get() not in users:
            self.filter_var.set("All")

        sel = self.filter_var.get()
        rows = get_records_for_user(sel) if sel != "All" else get_all_records()

        self.tree.delete(*self.tree.get_children())
        for row in rows:
            cat = row[5]
            self.tree.insert("", "end", values=row, tags=(cat,))

    # ── Private ───────────────────────────────────────────────────────────────
    def _clear_all(self):
        if messagebox.askyesno("Confirm Delete",
                               "This will permanently delete ALL records.\nContinue?"):
            delete_all_records()
            self.refresh()

    def _sort_by(self, col):
        """Sort treeview rows by clicked column (toggle asc/desc)."""
        data = [(self.tree.set(child, col), child)
                for child in self.tree.get_children("")]
        try:
            data.sort(key=lambda t: float(t[0]))
        except ValueError:
            data.sort()
        reverse = getattr(self, "_sort_reverse", False)
        if reverse:
            data.reverse()
        self._sort_reverse = not reverse
        for i, (_val, child) in enumerate(data):
            self.tree.move(child, "", i)
