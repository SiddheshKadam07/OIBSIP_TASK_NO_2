# ============================================================
#  gui_trend.py  –  Trend Analysis Tab (Tkinter + Matplotlib)
# ============================================================

import tkinter as tk
from tkinter import ttk, messagebox
import datetime
from database import get_all_users, get_records_for_user
from constants import BG, CARD, ACCENT, TEXT, MUTED, ENTRY_BG, WHITE

try:
    import matplotlib
    matplotlib.use("TkAgg")
    import matplotlib.pyplot as plt
    import matplotlib.dates as mdates
    from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
    HAS_MPL = True
except ImportError:
    HAS_MPL = False


class TrendTab(tk.Frame):
    def __init__(self, parent, **kwargs):
        super().__init__(parent, bg=BG, **kwargs)
        self._build()

    def _build(self):
        ctrl = tk.Frame(self, bg=BG)
        ctrl.pack(fill="x", padx=16, pady=12)

        tk.Label(ctrl, text="Select User:", bg=BG, fg=MUTED,
                 font=("Helvetica", 10)).pack(side="left")

        self.user_var = tk.StringVar()
        self.user_combo = ttk.Combobox(ctrl, textvariable=self.user_var,
                                        state="readonly", width=22)
        self.user_combo.pack(side="left", padx=8)

        tk.Button(ctrl, text="Plot Trend", bg=ACCENT, fg="#1a1a2e",
                  relief="flat", font=("Helvetica", 10, "bold"), cursor="hand2",
                  command=self._plot).pack(side="left", padx=4, ipady=4, ipadx=6)

        tk.Button(ctrl, text="Refresh", bg=ENTRY_BG, fg=MUTED, relief="flat",
                  font=("Helvetica", 10), cursor="hand2",
                  command=self.refresh_users).pack(side="left", padx=2, ipady=4, ipadx=4)

        chart_frame = tk.Frame(self, bg=BG)
        chart_frame.pack(fill="both", expand=True, padx=16, pady=6)

        if not HAS_MPL:
            tk.Label(chart_frame,
                     text="matplotlib is not installed.\nRun: pip install matplotlib\nthen restart.",
                     bg=BG, fg=MUTED, font=("Helvetica", 12),
                     justify="center").pack(expand=True)
            return

        self.fig, self.ax = plt.subplots(figsize=(8, 4.2), facecolor=BG)
        self.canvas = FigureCanvasTkAgg(self.fig, master=chart_frame)
        self.canvas.get_tk_widget().pack(fill="both", expand=True)
        self._draw_empty()
        self.refresh_users()

    def refresh_users(self):
        users = get_all_users()
        self.user_combo["values"] = users
        if users:
            self.user_var.set(users[0])

    def _draw_empty(self):
        self.ax.clear()
        self.ax.set_facecolor(CARD)
        self.ax.set_title("Select a user and click Plot Trend", color=MUTED, fontsize=11)
        self._style_axes()
        self.canvas.draw()

    def _style_axes(self):
        self.ax.tick_params(colors=MUTED, labelsize=8)
        for spine in self.ax.spines.values():
            spine.set_edgecolor(ENTRY_BG)

    def _plot(self):
        if not HAS_MPL:
            return

        user = self.user_var.get()
        if not user:
            messagebox.showwarning("No User", "Please select a user first.")
            return

        rows = get_records_for_user(user)
        if not rows:
            messagebox.showinfo("No Data", f"No records found for '{user}'.")
            return

        dates = [datetime.datetime.strptime(r[6], "%Y-%m-%d %H:%M") for r in rows]
        bmis  = [r[4] for r in rows]

        self.ax.clear()
        self.ax.set_facecolor(CARD)
        self.fig.patch.set_facecolor(BG)

        # Shaded zones
        for lo, hi, col, lbl in [(0, 18.5, "#3498db", "Underweight"),
                                   (18.5, 25, "#2ecc71", "Normal"),
                                   (25, 30, "#f39c12", "Overweight"),
                                   (30, 60, "#e74c3c", "Obese")]:
            self.ax.axhspan(lo, hi, alpha=0.13, color=col, label=lbl)

        # Threshold lines
        for val, col in [(18.5, "#3498db"), (25, "#2ecc71"), (30, "#f39c12")]:
            self.ax.axhline(val, color=col, linewidth=0.9, linestyle="--", alpha=0.7)

        # Plot BMI
        self.ax.plot(dates, bmis, color=ACCENT, linewidth=2.5,
                     marker="o", markersize=8,
                     markerfacecolor=WHITE, zorder=5, label="BMI")

        # Annotate each point with its value
        for d, b in zip(dates, bmis):
            self.ax.annotate(f" {b}", xy=(d, b),
                             color=ACCENT, fontsize=9, fontweight="bold",
                             va="bottom")

        self.ax.set_title(f"BMI Trend  —  {user}", color=TEXT, fontsize=12, pad=10)
        self.ax.set_xlabel("Date", color=MUTED, fontsize=9)
        self.ax.set_ylabel("BMI",  color=MUTED, fontsize=9)
        self._style_axes()

        # ── Smart date axis based on data range ───────────────────────────────
        if len(dates) == 1:
            # Single point: show exact date, ±1 day margin
            margin = datetime.timedelta(days=1)
            self.ax.set_xlim(dates[0] - margin, dates[0] + margin)
            self.ax.xaxis.set_major_formatter(mdates.DateFormatter("%d %b %Y"))
            self.ax.xaxis.set_major_locator(mdates.DayLocator(interval=1))
        else:
            date_range = (dates[-1] - dates[0]).days
            margin = datetime.timedelta(days=max(1, int(date_range * 0.05)))
            self.ax.set_xlim(dates[0] - margin, dates[-1] + margin)

            if date_range <= 7:
                self.ax.xaxis.set_major_locator(mdates.DayLocator(interval=1))
                self.ax.xaxis.set_major_formatter(mdates.DateFormatter("%d %b %Y"))
            elif date_range <= 31:
                self.ax.xaxis.set_major_locator(mdates.DayLocator(interval=2))
                self.ax.xaxis.set_major_formatter(mdates.DateFormatter("%d %b"))
            elif date_range <= 180:
                self.ax.xaxis.set_major_locator(mdates.WeekdayLocator(interval=2))
                self.ax.xaxis.set_major_formatter(mdates.DateFormatter("%d %b"))
            elif date_range <= 365:
                self.ax.xaxis.set_major_locator(mdates.MonthLocator())
                self.ax.xaxis.set_major_formatter(mdates.DateFormatter("%b %Y"))
            else:
                self.ax.xaxis.set_major_locator(mdates.MonthLocator(interval=3))
                self.ax.xaxis.set_major_formatter(mdates.DateFormatter("%b %Y"))

        self.fig.autofmt_xdate(rotation=30, ha="right")

        y_min = max(0,  min(bmis) - 3)
        y_max = max(40, max(bmis) + 3)
        self.ax.set_ylim(y_min, y_max)

        self.ax.legend(loc="upper right", fontsize=8,
                       facecolor=CARD, edgecolor=ENTRY_BG, labelcolor=TEXT)

        self.fig.tight_layout()
        self.canvas.draw()
