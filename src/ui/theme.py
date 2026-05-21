"""
Cyber Grid Theme Configuration
Manages the visual theme system for the application.
Provides consistent colors, fonts, and styling across all UI components.
"""

import customtkinter as ctk


# Core color palette
COLORS = {
    "bg_deep": "#020617",       # Deep Space Navy - main background
    "bg_surface": "#0F172A",    # Cyber Slate - card/panel backgrounds
    "primary": "#2563EB",       # Signal Blue - primary accent
    "secondary": "#06B6D4",     # Cyber Cyan - secondary accent
    "highlight": "#14B8A6",     # Electric Teal - highlights
    "warning": "#F59E0B",       # Alert Amber
    "error": "#EF4444",         # Threat Red
    "success": "#22C55E",       # Secure Green
    "text": "#F8FAFC",          # Ice White - primary text
    "text_muted": "#94A3B8",    # Steel Gray - secondary text
    "border": "#1E293B",        # Subtle borders
    "card": "#1E293B",          # Card background
    "hover": "#334155",         # Hover state
    "input_bg": "#0F172A",      # Input field background
    "scrollbar": "#334155",     # Scrollbar color
}

# Font configuration
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

# Spacing and sizing
PADDING = {
    "xs": 4,
    "sm": 8,
    "md": 12,
    "lg": 16,
    "xl": 24,
}

BORDER_RADIUS = 8


def apply_theme():
    """Apply the Cyber Grid theme to CustomTkinter."""
    ctk.set_appearance_mode("dark")
    ctk.set_default_color_theme("blue")


def create_styled_frame(parent, **kwargs):
    """Create a frame with consistent Cyber Grid styling."""
    defaults = {
        "fg_color": COLORS["bg_surface"],
        "corner_radius": BORDER_RADIUS,
    }
    defaults.update(kwargs)
    return ctk.CTkFrame(parent, **defaults)


def create_card(parent, **kwargs):
    """Create a card-style container with subtle depth."""
    defaults = {
        "fg_color": COLORS["card"],
        "corner_radius": BORDER_RADIUS,
        "border_width": 1,
        "border_color": COLORS["border"],
    }
    defaults.update(kwargs)
    return ctk.CTkFrame(parent, **defaults)


def create_accent_button(parent, text, command=None, color="primary", **kwargs):
    """Create a styled button with the accent color."""
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
