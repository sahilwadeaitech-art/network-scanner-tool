"""
Theme config for the dark UI. Colors, fonts, spacing, helper functions.
"""

import customtkinter as ctk


COLORS = {
    "bg_deep": "#020617",
    "bg_surface": "#0F172A",
    "primary": "#2563EB",
    "secondary": "#06B6D4",
    "highlight": "#14B8A6",
    "warning": "#F59E0B",
    "error": "#EF4444",
    "success": "#22C55E",
    "text": "#F8FAFC",
    "text_muted": "#94A3B8",
    "border": "#1E293B",
    "card": "#1E293B",
    "hover": "#334155",
    "input_bg": "#0F172A",
    "scrollbar": "#334155",
}

FONTS = {
    "heading": ("Segoe UI", 20, "bold"),
    "subheading": ("Segoe UI", 14, "bold"),
    "body": ("Segoe UI", 12),
    "body_bold": ("Segoe UI", 12, "bold"),
    "small": ("Segoe UI", 10),
    "mono": ("Consolas", 11),
    "mono_small": ("Consolas", 10),
    "stat_large": ("Segoe UI", 28, "bold"),
    "stat_medium": ("Segoe UI", 18, "bold"),
}

PADDING = {"xs": 4, "sm": 8, "md": 12, "lg": 16, "xl": 24}
BORDER_RADIUS = 8


def apply_theme():
    ctk.set_appearance_mode("dark")
    ctk.set_default_color_theme("blue")


def create_styled_frame(parent, **kwargs):
    defaults = {"fg_color": COLORS["bg_surface"], "corner_radius": BORDER_RADIUS}
    defaults.update(kwargs)
    return ctk.CTkFrame(parent, **defaults)


def create_card(parent, **kwargs):
    defaults = {
        "fg_color": COLORS["card"],
        "corner_radius": BORDER_RADIUS,
        "border_width": 1,
        "border_color": COLORS["border"],
    }
    defaults.update(kwargs)
    return ctk.CTkFrame(parent, **defaults)


def create_accent_button(parent, text, command=None, color="primary", **kwargs):
    color_map = {
        "primary": COLORS["primary"],
        "secondary": COLORS["secondary"],
        "success": COLORS["success"],
        "warning": COLORS["warning"],
        "error": COLORS["error"],
    }
    btn_color = color_map.get(color, COLORS["primary"])
    defaults = {
        "text": text,
        "command": command,
        "fg_color": btn_color,
        "hover_color": COLORS["hover"],
        "corner_radius": 6,
        "font": FONTS["body_bold"],
        "height": 36,
    }
    defaults.update(kwargs)
    return ctk.CTkButton(parent, **defaults)
