# estoque/ui/theme.py
import tkinter as tk
from tkinter import ttk

PRIMARY = "#2196F3"
SUCCESS = "#4CAF50"
DANGER  = "#F44336"
INFO    = "#03A9F4"
BG      = "#FAFAFA"

def apply_theme(root: tk.Tk):
    root.configure(bg=BG)
    style = ttk.Style(root)
    try:
        style.theme_use("clam")
    except tk.TclError:
        pass

    base_font = ("Segoe UI", 10)
    h1_font   = ("Segoe UI", 18, "bold")
    h2_font   = ("Segoe UI", 16, "bold")

    # Botões
    style.configure("TButton", font=base_font, padding=8)
    style.configure("Primary.TButton", background=PRIMARY, foreground="white")
    style.map("Primary.TButton", background=[("active", "#1E88E5")])

    style.configure("Success.TButton", background=SUCCESS, foreground="white")
    style.map("Success.TButton", background=[("active", "#43A047")])

    style.configure("Danger.TButton", background=DANGER, foreground="white")
    style.map("Danger.TButton", background=[("active", "#E53935")])

    style.configure("Info.TButton", background=INFO, foreground="white")
    style.map("Info.TButton", background=[("active", "#039BE5")])

    # Labels de título
    style.configure("H1.TLabel", font=h1_font, background=BG)
    style.configure("H2.TLabel", font=h2_font, background=BG)

    # Treeview
    style.configure("Treeview", font=base_font, rowheight=26)
    style.configure("Treeview.Heading", font=("Segoe UI", 10, "bold"))