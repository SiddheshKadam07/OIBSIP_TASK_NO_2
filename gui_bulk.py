# ============================================================
#  gui_bulk.py  –  Bulk Entry Tab (Add Multiple People)
# ============================================================

import tkinter as tk
from tkinter import ttk, messagebox
from calculator import calculate_bmi, classify_bmi, validate_inputs
from database import save_record
from constants import BG, CARD, ACCENT, TEXT, MUTED, ENTRY_BG, WHITE


class BulkEntryTab(tk.Frame):
    """
    Tab 4 – Add BMI records for multiple people at once.
    Each row = one person (Name, Weight, Height).
    """

    def __init__(self, parent, on_save_callback=None, **kwargs):
        super().__init__(parent, bg=BG, **kwargs)
        self.on_save_callback = on_save_callback
        self.rows = []        # list of (name_var, weight_var, height_var, result_label)
        self._build()

    # ── Build UI ──────────────────────────────────────────────────────────────
    def _build(self):
        # ── Title ─────────────────────────────────────────────────────────────
        title_f = tk.Frame(self, bg=BG)
        title_f.pack(fill="x", padx=20, pady=(16, 4))
        tk.Label(title_f, text="👥  Bulk BMI Entry",
                 font=("Helvetica", 15, "bold"), bg=BG, fg=ACCENT).pack(side="left")
        tk.Label(title_f, text="  Add multiple people at once",
                 font=("Helvetica", 10), bg=BG, fg=MUTED).pack(side="left", pady=4)

        # ── Column headers ─────────────────────────────────────────────────────
        hdr = tk.Frame(self, bg=CARD)
        hdr.pack(fill="x", padx=20, pady=(4, 0))
        for text, w in [("#", 4), ("Name", 18), ("Weight (kg)", 12),
                         ("Height (m)", 12), ("Result", 22)]:
            tk.Label(hdr, text=text, font=("Helvetica", 10, "bold"),
                     bg=CARD, fg=ACCENT, width=w, anchor="w"
                     ).pack(side="left", padx=6, pady=6)

        # ── Scrollable rows area ───────────────────────────────────────────────
        outer = tk.Frame(self, bg=BG)
        outer.pack(fill="both", expand=True, padx=20, pady=4)

        canvas = tk.Canvas(outer, bg=BG, highlightthickness=0)
        vsb    = ttk.Scrollbar(outer, orient="vertical", command=canvas.yview)
        canvas.configure(yscrollcommand=vsb.set)
        vsb.pack(side="right", fill="y")
        canvas.pack(side="left", fill="both", expand=True)

        self.rows_frame = tk.Frame(canvas, bg=BG)
        self.canvas_window = canvas.create_window((0, 0), window=self.rows_frame,
                                                   anchor="nw")
        self.rows_frame.bind("<Configure>",
                             lambda e: canvas.configure(
                                 scrollregion=canvas.bbox("all")))
        canvas.bind("<Configure>",
                    lambda e: canvas.itemconfig(self.canvas_window,
                                                width=e.width))

        # ── Add initial 3 rows ─────────────────────────────────────────────────
        for _ in range(3):
            self._add_row()

        # ── Bottom buttons ─────────────────────────────────────────────────────
        btn_f = tk.Frame(self, bg=BG)
        btn_f.pack(fill="x", padx=20, pady=10)

        tk.Button(btn_f, text="➕  Add Row",
                  font=("Helvetica", 11), bg=ENTRY_BG, fg=ACCENT,
                  relief="flat", cursor="hand2",
                  command=self._add_row
                  ).pack(side="left", padx=6, ipady=5, ipadx=8)

        tk.Button(btn_f, text="✅  Calculate & Save All",
                  font=("Helvetica", 11, "bold"), bg=ACCENT, fg="#1a1a2e",
                  relief="flat", cursor="hand2",
                  command=self._calculate_all
                  ).pack(side="left", padx=6, ipady=5, ipadx=8)

        tk.Button(btn_f, text="🗑  Clear All Rows",
                  font=("Helvetica", 11), bg="#6b2020", fg=TEXT,
                  relief="flat", cursor="hand2",
                  command=self._clear_all
                  ).pack(side="left", padx=6, ipady=5, ipadx=8)

        # ── Summary label ──────────────────────────────────────────────────────
        self.lbl_summary = tk.Label(self, text="",
                                     font=("Helvetica", 11, "bold"),
                                     bg=BG, fg=ACCENT)
        self.lbl_summary.pack(pady=(0, 10))

    # ── Add a single row ──────────────────────────────────────────────────────
    def _add_row(self):
        idx  = len(self.rows) + 1
        row  = tk.Frame(self.rows_frame, bg=CARD if idx % 2 == 0 else BG)
        row.pack(fill="x", pady=2)

        # Row number
        tk.Label(row, text=str(idx), font=("Helvetica", 10),
                 bg=row["bg"], fg=MUTED, width=4
                 ).pack(side="left", padx=6)

        name_var   = tk.StringVar()
        weight_var = tk.StringVar()
        height_var = tk.StringVar()

        for var, w in [(name_var, 18), (weight_var, 12), (height_var, 12)]:
            tk.Entry(row, textvariable=var, font=("Helvetica", 11),
                     bg=ENTRY_BG, fg=WHITE, insertbackground=WHITE,
                     relief="flat", width=w, bd=5
                     ).pack(side="left", padx=6, pady=6)

        result_lbl = tk.Label(row, text="—", font=("Helvetica", 10),
                               bg=row["bg"], fg=MUTED, width=24, anchor="w")
        result_lbl.pack(side="left", padx=6)

        # Delete this row button
        tk.Button(row, text="✕", font=("Helvetica", 9),
                  bg=row["bg"], fg="#e74c3c", relief="flat", cursor="hand2",
                  command=lambda r=row, i=idx-1: self._delete_row(r, i)
                  ).pack(side="left", padx=4)

        self.rows.append((name_var, weight_var, height_var, result_lbl, row))

    # ── Calculate & save all rows ─────────────────────────────────────────────
    def _calculate_all(self):
        saved   = 0
        skipped = 0
        errors  = []

        for i, (name_var, weight_var, height_var, result_lbl, _) in enumerate(self.rows, 1):
            name   = name_var.get().strip()
            w_str  = weight_var.get().strip()
            h_str  = height_var.get().strip()

            # Skip completely empty rows silently
            if not name and not w_str and not h_str:
                skipped += 1
                continue

            # Validate name
            if not name:
                result_lbl.config(text="❌ Name missing", fg="#e74c3c")
                errors.append(f"Row {i}: Name is missing")
                continue

            # Validate numbers
            try:
                weight = float(w_str)
                height = float(h_str)
            except ValueError:
                result_lbl.config(text="❌ Invalid numbers", fg="#e74c3c")
                errors.append(f"Row {i} ({name}): Invalid weight/height")
                continue

            # Range validation
            err = validate_inputs(weight, height)
            if err:
                result_lbl.config(text=f"❌ {err}", fg="#e74c3c")
                errors.append(f"Row {i} ({name}): {err}")
                continue

            # Calculate & save
            bmi        = calculate_bmi(weight, height)
            cat, color = classify_bmi(bmi)
            save_record(name, weight, height, bmi, cat)
            result_lbl.config(text=f"✅  BMI {bmi}  |  {cat}", fg=color)
            saved += 1

        # Summary
        if saved > 0:
            self.lbl_summary.config(
                text=f"✅  {saved} record(s) saved successfully!"
                     + (f"   ⚠ {len(errors)} error(s)" if errors else ""),
                fg=ACCENT)
            if self.on_save_callback:
                self.on_save_callback()
        elif errors:
            self.lbl_summary.config(
                text=f"❌  {len(errors)} error(s) found. Please fix and try again.",
                fg="#e74c3c")
        else:
            self.lbl_summary.config(text="⚠  No data entered.", fg=MUTED)

    # ── Delete a specific row ─────────────────────────────────────────────────
    def _delete_row(self, row_frame, index):
        if len(self.rows) <= 1:
            messagebox.showwarning("Cannot Delete", "At least one row must remain.")
            return
        row_frame.destroy()
        self.rows.pop(index)
        # Renumber remaining rows
        for i, (_, _, _, _, rf) in enumerate(self.rows, 1):
            for widget in rf.winfo_children():
                if isinstance(widget, tk.Label) and widget.cget("width") == 4:
                    widget.config(text=str(i))
                    break

    # ── Clear all rows and reset ───────────────────────────────────────────────
    def _clear_all(self):
        if messagebox.askyesno("Clear All", "Clear all rows and results?"):
            for _, _, _, _, rf in self.rows:
                rf.destroy()
            self.rows.clear()
            self.lbl_summary.config(text="")
            for _ in range(3):
                self._add_row()
