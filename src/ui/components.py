"""
Reusable UI Components
Custom widgets used throughout the application.
Includes stat cards, progress indicators, and data display elements.
"""

import customtkinter as ctk
from src.ui.theme import COLORS, FONTS, PADDING, create_card


class StatCard(ctk.CTkFrame):
    """
    Animated statistics card for the dashboard.
    Shows a metric label, value, and optional trend indicator.
    """

    def __init__(self, parent, title="", value="0", icon="●", accent_color=None, **kwargs):
        super().__init__(parent, fg_color=COLORS["card"], corner_radius=8,
                        border_width=1, border_color=COLORS["border"], **kwargs)

        self._accent = accent_color or COLORS["primary"]
        self._target_value = value

        # Layout
        self.grid_columnconfigure(0, weight=1)

        # Accent bar at top
        accent_bar = ctk.CTkFrame(self, fg_color=self._accent, height=3, corner_radius=2)
        accent_bar.grid(row=0, column=0, sticky="ew", padx=12, pady=(12, 0))

        # Icon and title
        header = ctk.CTkFrame(self, fg_color="transparent")
        header.grid(row=1, column=0, sticky="w", padx=16, pady=(8, 0))

        icon_label = ctk.CTkLabel(header, text=icon, font=("Segoe UI", 14),
                                  text_color=self._accent)
        icon_label.pack(side="left")

        title_label = ctk.CTkLabel(header, text=title, font=FONTS["small"],
                                   text_color=COLORS["text_muted"])
        title_label.pack(side="left", padx=(6, 0))

        # Value display
        self.value_label = ctk.CTkLabel(self, text=value, font=FONTS["stat_large"],
                                        text_color=COLORS["text"])
        self.value_label.grid(row=2, column=0, sticky="w", padx=16, pady=(4, 16))

    def update_value(self, new_value):
        """Update the displayed value."""
        self._target_value = str(new_value)
        self.value_label.configure(text=self._target_value)


class ScanProgressBar(ctk.CTkFrame):
    """
    Custom scan progress indicator with pulse animation.
    Shows scan state with percentage and animated glow.
    """

    def __init__(self, parent, **kwargs):
        super().__init__(parent, fg_color="transparent", **kwargs)

        self.grid_columnconfigure(0, weight=1)

        # Status label
        self.status_frame = ctk.CTkFrame(self, fg_color="transparent")
        self.status_frame.grid(row=0, column=0, sticky="ew", pady=(0, 4))

        self.status_label = ctk.CTkLabel(self.status_frame, text="Ready",
                                         font=FONTS["small"],
                                         text_color=COLORS["text_muted"])
        self.status_label.pack(side="left")

        self.percent_label = ctk.CTkLabel(self.status_frame, text="",
                                          font=FONTS["small"],
                                          text_color=COLORS["secondary"])
        self.percent_label.pack(side="right")

        # Progress bar
        self.progress_bar = ctk.CTkProgressBar(self, fg_color=COLORS["border"],
                                               progress_color=COLORS["primary"],
                                               height=6, corner_radius=3)
        self.progress_bar.grid(row=1, column=0, sticky="ew")
        self.progress_bar.set(0)

        self._is_animating = False

    def set_progress(self, value: float, status_text: str = None):
        """Update progress (0.0 to 1.0) and optional status text."""
        self.progress_bar.set(value)
        self.percent_label.configure(text=f"{int(value * 100)}%")
        if status_text:
            self.status_label.configure(text=status_text)

    def set_scanning(self, is_scanning: bool):
        """Toggle between scanning and idle states."""
        if is_scanning:
            self.status_label.configure(text="Scanning...", text_color=COLORS["secondary"])
            self._pulse_animation()
        else:
            self._is_animating = False
            self.status_label.configure(text="Complete", text_color=COLORS["success"])

    def reset(self):
        """Reset to initial state."""
        self._is_animating = False
        self.progress_bar.set(0)
        self.status_label.configure(text="Ready", text_color=COLORS["text_muted"])
        self.percent_label.configure(text="")

    def _pulse_animation(self):
        """Subtle pulsing effect while scanning."""
        self._is_animating = True
        self._pulse_step(True)

    def _pulse_step(self, forward):
        """Animate the progress bar color between primary and secondary."""
        if not self._is_animating:
            return
        color = COLORS["secondary"] if forward else COLORS["primary"]
        self.progress_bar.configure(progress_color=color)
        self.after(800, lambda: self._pulse_step(not forward))


class DeviceListItem(ctk.CTkFrame):
    """
    Single device entry in the scan results list.
    Shows IP, hostname, status indicator, and latency.
    """

    def __init__(self, parent, device_data, on_select=None, **kwargs):
        super().__init__(parent, fg_color=COLORS["bg_surface"], corner_radius=6,
                        height=48, **kwargs)

        self.device = device_data
        self._on_select = on_select

        self.grid_columnconfigure(1, weight=1)
        self.grid_propagate(False)
        self.configure(height=52)

        # Status dot
        status_color = COLORS["success"] if device_data.get("status") == "Online" else COLORS["error"]
        dot = ctk.CTkLabel(self, text="●", font=("Segoe UI", 10), text_color=status_color)
        dot.grid(row=0, column=0, padx=(12, 6), pady=8)

        # IP and hostname
        info_frame = ctk.CTkFrame(self, fg_color="transparent")
        info_frame.grid(row=0, column=1, sticky="w", pady=8)

        ip_label = ctk.CTkLabel(info_frame, text=device_data.get("ip", ""),
                                font=FONTS["body_bold"], text_color=COLORS["text"])
        ip_label.pack(anchor="w")

        hostname = device_data.get("hostname", "Unknown")
        host_label = ctk.CTkLabel(info_frame, text=hostname,
                                  font=FONTS["small"], text_color=COLORS["text_muted"])
        host_label.pack(anchor="w")

        # Latency
        latency = device_data.get("response_time", 0)
        latency_color = COLORS["success"] if latency < 20 else COLORS["warning"] if latency < 100 else COLORS["error"]
        latency_label = ctk.CTkLabel(self, text=f"{latency:.1f}ms",
                                     font=FONTS["mono_small"], text_color=latency_color)
        latency_label.grid(row=0, column=2, padx=12, pady=8)

        # Click binding
        self.bind("<Button-1>", self._handle_click)
        for child in self.winfo_children():
            child.bind("<Button-1>", self._handle_click)

    def _handle_click(self, event=None):
        if self._on_select:
            self._on_select(self.device)


class ScanResultTable(ctk.CTkFrame):
    """
    Scrollable table displaying port scan results.
    Supports sorting and filtering.
    """

    def __init__(self, parent, **kwargs):
        super().__init__(parent, fg_color=COLORS["bg_surface"], corner_radius=8, **kwargs)

        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(1, weight=1)

        # Table header
        header = ctk.CTkFrame(self, fg_color=COLORS["card"], corner_radius=0, height=36)
        header.grid(row=0, column=0, sticky="ew")
        header.grid_columnconfigure((0, 1, 2, 3), weight=1)

        headers = ["Port", "State", "Service", "Response"]
        for i, h in enumerate(headers):
            ctk.CTkLabel(header, text=h, font=FONTS["small"],
                        text_color=COLORS["text_muted"]).grid(row=0, column=i, padx=8, pady=6)

        # Scrollable results area
        self.scroll_frame = ctk.CTkScrollableFrame(self, fg_color="transparent")
        self.scroll_frame.grid(row=1, column=0, sticky="nsew", padx=2, pady=2)
        self.scroll_frame.grid_columnconfigure((0, 1, 2, 3), weight=1)

        self._row_count = 0

    def add_port_result(self, port_result):
        """Add a port result row to the table."""
        row = self._row_count
        bg = COLORS["bg_surface"] if row % 2 == 0 else COLORS["card"]

        state_color = COLORS["success"] if port_result.state == "open" else COLORS["text_muted"]

        ctk.CTkLabel(self.scroll_frame, text=str(port_result.port),
                    font=FONTS["mono"], text_color=COLORS["text"]).grid(
                        row=row, column=0, padx=8, pady=3, sticky="w")

        ctk.CTkLabel(self.scroll_frame, text=port_result.state.upper(),
                    font=FONTS["mono_small"], text_color=state_color).grid(
                        row=row, column=1, padx=8, pady=3, sticky="w")

        ctk.CTkLabel(self.scroll_frame, text=port_result.service,
                    font=FONTS["body"], text_color=COLORS["text"]).grid(
                        row=row, column=2, padx=8, pady=3, sticky="w")

        ctk.CTkLabel(self.scroll_frame, text=f"{port_result.response_time:.1f}ms",
                    font=FONTS["mono_small"], text_color=COLORS["text_muted"]).grid(
                        row=row, column=3, padx=8, pady=3, sticky="w")

        self._row_count += 1

    def clear(self):
        """Clear all rows from the table."""
        for widget in self.scroll_frame.winfo_children():
            widget.destroy()
        self._row_count = 0


class LogConsole(ctk.CTkFrame):
    """
    Live log/event console with color-coded entries.
    Shows real-time scan events and diagnostic output.
    """

    def __init__(self, parent, max_lines=200, **kwargs):
        super().__init__(parent, fg_color=COLORS["bg_surface"], corner_radius=8,
                        border_width=1, border_color=COLORS["border"], **kwargs)

        self.max_lines = max_lines
        self._line_count = 0

        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(0, weight=1)

        self.textbox = ctk.CTkTextbox(self, fg_color="transparent",
                                      text_color=COLORS["text"],
                                      font=FONTS["mono_small"],
                                      activate_scrollbars=True)
        self.textbox.grid(row=0, column=0, sticky="nsew", padx=4, pady=4)
        self.textbox.configure(state="disabled")

    def log(self, message: str, level: str = "info"):
        """Add a log entry with timestamp and level coloring."""
        import time
        timestamp = time.strftime("%H:%M:%S")
        prefix_map = {
            "info": "[•]",
            "success": "[✓]",
            "warning": "[!]",
            "error": "[✗]",
            "scan": "[~]",
        }
        prefix = prefix_map.get(level, "[•]")
        full_line = f" {timestamp} {prefix} {message}\n"

        self.textbox.configure(state="normal")
        self.textbox.insert("end", full_line)
        self._line_count += 1

        # Trim old lines if needed
        if self._line_count > self.max_lines:
            self.textbox.delete("1.0", "2.0")
            self._line_count -= 1

        self.textbox.see("end")
        self.textbox.configure(state="disabled")

    def clear(self):
        """Clear the console."""
        self.textbox.configure(state="normal")
        self.textbox.delete("1.0", "end")
        self.textbox.configure(state="disabled")
        self._line_count = 0
