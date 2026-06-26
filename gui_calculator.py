# ============================================================
#  gui_calculator.py  –  Calculator Tab (Tkinter Frame)
# ============================================================

import tkinter as tk
from tkinter import messagebox
from calculator import (calculate_bmi, classify_bmi, get_health_tip,
                        convert_imperial_to_metric, validate_inputs)
from database import save_record
from constants import (BG, CARD, ACCENT, TEXT, MUTED, WHITE, ENTRY_BG)


class CalculatorTab(tk.Frame):
    """
    First tab of the application.
    Handles user input, BMI calculation, result display, and data saving.
    """

    def __init__(self, parent, on_save_callback=None, **kwargs):
        super().__init__(parent, bg=BG, **kwargs)
        self.on_save_callback = on_save_callback   # called after each save
        self._build()

    # ── Build UI ──────────────────────────────────────────────────────────────
    def _build(self):
        outer = tk.Frame(self, bg=BG)
        outer.pack(expand=True)

        card = tk.Frame(outer, bg=CARD)
        card.pack(padx=40, pady=30, ipadx=30, ipady=24)

        tk.Label(card, text="Enter Your Details",
                 font=("Helvetica", 14, "bold"), bg=CARD, fg=ACCENT
                 ).grid(row=0, column=0, columnspan=2, pady=(0, 18))

        # Input fields
        labels  = ["👤  Name", "⚖  Weight (kg)", "📏  Height (m)"]
        attribs = ["entry_name", "entry_weight", "entry_height"]
        for i, (lbl, attr) in enumerate(zip(labels, attribs), start=1):
            tk.Label(card, text=lbl, font=("Helvetica", 11),
                     bg=CARD, fg=TEXT, anchor="w", width=18
                     ).grid(row=i, column=0, pady=8, sticky="w")
            entry = tk.Entry(card, font=("Helvetica", 12),
                             bg=ENTRY_BG, fg=WHITE, insertbackground=WHITE,
                             relief="flat", width=22, bd=6)
            entry.grid(row=i, column=1, pady=8, padx=(10, 0))
            setattr(self, attr, entry)

        # Unit radio buttons
        self.unit_var = tk.StringVar(value="metric")
        uf = tk.Frame(card, bg=CARD)
        uf.grid(row=4, column=0, columnspan=2, pady=(4, 10))
        tk.Label(uf, text="Units:", font=("Helvetica", 10),
                 bg=CARD, fg=MUTED).pack(side="left", padx=(0, 8))
        for val, txt in [("metric", "Metric (kg / m)"),
                         ("imperial", "Imperial (lbs / ft·in)")]:
            tk.Radiobutton(uf, text=txt, variable=self.unit_var, value=val,
                           command=self._toggle_units,
                           bg=CARD, fg=MUTED, selectcolor=ENTRY_BG,
                           activebackground=CARD, font=("Helvetica", 10)
                           ).pack(side="left", padx=6)

        # Imperial sub-fields (hidden by default)
        self.imp_frame = tk.Frame(card, bg=CARD)
        self.imp_frame.grid(row=5, column=0, columnspan=2)
        for lbl, attr, w in [("Weight (lbs)", "entry_lbs", 8),
                               ("ft", "entry_ft", 4),
                               ("in", "entry_in", 4)]:
            tk.Label(self.imp_frame, text=lbl, font=("Helvetica", 10),
                     bg=CARD, fg=MUTED).pack(side="left", padx=3)
            e = tk.Entry(self.imp_frame, font=("Helvetica", 11),
                         bg=ENTRY_BG, fg=WHITE, insertbackground=WHITE,
                         relief="flat", width=w, bd=4)
            e.pack(side="left", padx=3)
            setattr(self, attr, e)
        self.imp_frame.grid_remove()

        # Action buttons
        bf = tk.Frame(card, bg=CARD)
        bf.grid(row=6, column=0, columnspan=2, pady=14)
        tk.Button(bf, text="  Calculate BMI  ",
                  font=("Helvetica", 12, "bold"), bg=ACCENT, fg="#1a1a2e",
                  relief="flat", cursor="hand2", command=self._calculate
                  ).pack(side="left", padx=6, ipady=6, ipadx=6)
        tk.Button(bf, text="Clear",
                  font=("Helvetica", 11), bg=ENTRY_BG, fg=MUTED,
                  relief="flat", cursor="hand2", command=self._clear
                  ).pack(side="left", padx=6, ipady=6, ipadx=6)

        # Result widgets
        self.lbl_bmi = tk.Label(card, text="", font=("Helvetica", 36, "bold"),
                                 bg=CARD, fg=ACCENT)
        self.lbl_bmi.grid(row=7, column=0, columnspan=2, pady=(10, 0))

        self.lbl_cat = tk.Label(card, text="", font=("Helvetica", 14),
                                 bg=CARD, fg=TEXT)
        self.lbl_cat.grid(row=8, column=0, columnspan=2)

        self.lbl_tip = tk.Label(card, text="", font=("Helvetica", 10),
                                 bg=CARD, fg=MUTED, wraplength=400,
                                 justify="center")
        self.lbl_tip.grid(row=9, column=0, columnspan=2, pady=(4, 0))

        # BMI scale bar canvas
        self.bar = tk.Canvas(card, width=400, height=36,
                             bg=CARD, highlightthickness=0)
        self.bar.grid(row=10, column=0, columnspan=2, pady=(10, 4))

    # ── Logic ─────────────────────────────────────────────────────────────────
    def _toggle_units(self):
        if self.unit_var.get() == "imperial":
            self.entry_weight.grid_remove()
            self.entry_height.grid_remove()
            self.imp_frame.grid()
        else:
            self.imp_frame.grid_remove()
            self.entry_weight.grid()
            self.entry_height.grid()

    def _calculate(self):
        name = self.entry_name.get().strip()
        if not name:
            messagebox.showwarning("Name Required",
                                   "Please enter a name to track your record.")
            return

        try:
            if self.unit_var.get() == "imperial":
                lbs = float(self.entry_lbs.get())
                ft  = float(self.entry_ft.get())
                ins = float(self.entry_in.get() or 0)
                weight, height = convert_imperial_to_metric(lbs, ft, ins)
            else:
                weight = float(self.entry_weight.get())
                height = float(self.entry_height.get())
        except ValueError:
            messagebox.showerror("Invalid Input",
                                 "Please enter valid numeric values.")
            return

        err = validate_inputs(weight, height)
        if err:
            messagebox.showerror("Out of Range", err)
            return

        bmi       = calculate_bmi(weight, height)
        cat, color = classify_bmi(bmi)
        tip        = get_health_tip(cat)

        # Update result labels
        self.lbl_bmi.config(text=f"BMI: {bmi}", fg=color)
        self.lbl_cat.config(text=f"Category: {cat}", fg=color)
        self.lbl_tip.config(text=tip)
        self._draw_bar(bmi)

        # Persist and notify sibling tabs
        save_record(name, weight, height, bmi, cat)
        if self.on_save_callback:
            self.on_save_callback()

    def _draw_bar(self, bmi: float):
        c = self.bar
        c.delete("all")
        W, H = 400, 28
        # Coloured zone bands  (range: 10–40)
        segments = [(18.5, "#3498db"), (25, "#2ecc71"),
                    (30, "#f39c12"),   (40, "#e74c3c")]
        prev = 10
        for val, col in segments:
            x1 = int((prev - 10) / 30 * W)
            x2 = int((val  - 10) / 30 * W)
            c.create_rectangle(x1, 10, x2, H, fill=col, outline="")
            prev = val
        c.create_rectangle(int((prev-10)/30*W), 10, W, H,
                           fill="#c0392b", outline="")
        # Triangle marker
        mx = min(max(int((bmi - 10) / 30 * W), 6), W - 6)
        c.create_polygon(mx, 0, mx-6, 10, mx+6, 10, fill=WHITE, outline="")
        # Threshold labels
        for val, txt in [(18.5, "18.5"), (25, "25"), (30, "30")]:
            lx = int((val - 10) / 30 * W)
            c.create_text(lx, 30, text=txt, fill=MUTED, font=("Helvetica", 7))

    def _clear(self):
        for attr in ("entry_name", "entry_weight", "entry_height",
                     "entry_lbs", "entry_ft", "entry_in"):
            getattr(self, attr).delete(0, "end")
        self.lbl_bmi.config(text="")
        self.lbl_cat.config(text="")
        self.lbl_tip.config(text="")
        self.bar.delete("all")
