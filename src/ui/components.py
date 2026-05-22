"""
Reusable UI widgets - stat cards, progress bars, device list items, etc.
"""

import customtkinter as ctk
from src.ui.theme import COLORS, FONTS, PADDING, create_card


class StatCard(ctk.CTkFrame):
    """Dashboard stat card with icon, label, and big number."""

    def __init__(self, parent, title="", value="0", icon="●", accent_color=None, **kwargs):
        super().__init__(parent, fg_color=COLORS["card"], corner_radius=8,
                        border_width=1, border_color=COLORS["border"], **kwargs)

        self._accent = accent_color or COLORS["primary"]
        self._target_value = value

        self.grid_columnconfigure(0, weight=1)

        accent_bar = ctk.CTkFrame(self, fg_color=self._accent, height=3, corner_radius=2)
        accent_bar.grid(row=0, column=0, sticky="ew", padx=12, pady=(12, 0))

        header = ctk.CTkFrame(self, fg_color="transparent")
        header.grid(row=1, column=0, sticky="w", padx=16, pady=(8, 0))

        ctk.CTkLabel(header, text=icon, font=("Segoe UI", 14),
                     text_color=self._accent).pack(side="left")
        ctk.CTkLabel(header, text=title, font=FONTS["small"],
                     text_color=COLORS["text_muted"]).pack(side="left", padx=(6, 0))

        self.value_label = ctk.CTkLabel(self, text=value, font=FONTS["stat_large"],
                                        text_color=COLORS["text"])
        self.value_label.grid(row=2, column=0, sticky="w", padx=16, pady=(4, 16))

    def update_value(self, new_value):
        self._target_value = str(new_value)
        self.value_label.configure(text=self._target_value)


class ScanProgressBar(ctk.CTkFrame):
    """Progress bar with status text and pulse animation during scans."""

    def __init__(self, parent, **kwargs):
        super().__init__(parent, fg_color="transparent", **kwargs)
        self.grid_columnconfigure(0, weight=1)

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

        self.progress_bar = ctk.CTkProgressBar(self, fg_color=COLORS["border"],
                                               progress_color=COLORS["primary"],
                                               height=6, corner_radius=3)
        self.progress_bar.grid(row=1, column=0, sticky="ew")
        self.progress_bar.set(0)

        self._is_animating = False

    def set_progress(self, value: float, status_text: str = None):
        self.progress_bar.set(value)
        self.percent_label.configure(text=f"{int(value * 100)}%")
        if status_text:
            self.status_label.configure(text=status_text)

    def set_scanning(self, is_scanning: bool):
        if is_scanning:
            self.status_label.configure(text="Scanning...", text_color=COLORS["secondary"])
            self._pulse_animation()
        else:
            self._is_animating = False
            self.status_label.configure(text="Complete", text_color=COLORS["success"])

    def reset(self):
        self._is_animating = False
        self.progress_bar.set(0)
        self.status_label.configure(text="Ready", text_color=COLORS["text_muted"])
        self.percent_label.configure(text="")

    def _pulse_animation(self):
        self._is_animating = True
        self._pulse_step(True)

    def _pulse_step(self, forward):
        if not self._is_animating:
            return
        color = COLORS["secondary"] if forward else COLORS["primary"]
        self.progress_bar.configure(progress_color=color)
        self.after(800, lambda: self._pulse_step(not forward))


class DeviceListItem(ctk.CTkFrame):
    """Row in the discovered devices list."""

    def __init__(self, parent, device_data, on_select=None, **kwargs):
        super().__init__(parent, fg_color=COLORS["bg_surface"], corner_radius=6,
                        height=48, **kwargs)

        self.device = device_data
        self._on_select = on_select

        self.grid_columnconfigure(1, weight=1)
        self.grid_propagate(False)
        self.configure(height=52)

        # status dot
        status_color = COLORS["success"] if device_data.get("status") == "Online" else COLORS["error"]
        dot = ctk.CTkLabel(self, text="●", font=("Segoe UI", 10), text_color=status_color)
        dot.grid(row=0, column=0, padx=(12, 6), pady=8)

        info_frame = ctk.CTkFrame(self, fg_color="transparent")
        info_frame.grid(row=0, column=1, sticky="w", pady=8)

        ctk.CTkLabel(info_frame, text=device_data.get("ip", ""),
                     font=FONTS["body_bold"], text_color=COLORS["text"]).pack(anchor="w")
        ctk.CTkLabel(info_frame, text=device_data.get("hostname", "Unknown"),
                     font=FONTS["small"], text_color=COLORS["text_muted"]).pack(anchor="w")

        # latency with color coding
        latency = device_data.get("response_time", 0)
        if latency < 20:
            lat_color = COLORS["success"]
        elif latency < 100:
            lat_color = COLORS["warning"]
        else:
            lat_color = COLORS["error"]

        ctk.CTkLabel(self, text=f"{latency:.1f}ms",
                     font=FONTS["mono_small"], text_color=lat_color).grid(
                         row=0, column=2, padx=12, pady=8)

        self.bind("<Button-1>", self._handle_click)
        for child in self.winfo_children():
            child.bind("<Button-1>", self._handle_click)

    def _handle_click(self, event=None):
        if self._on_select:
            self._on_select(self.device)


class ScanResultTable(ctk.CTkFrame):
    """Simple table for port scan results."""

    def __init__(self, parent, **kwargs):
        super().__init__(parent, fg_color=COLORS["bg_surface"], corner_radius=8, **kwargs)

        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(1, weight=1)

        header = ctk.CTkFrame(self, fg_color=COLORS["card"], corner_radius=0, height=36)
        header.grid(row=0, column=0, sticky="ew")
        header.grid_columnconfigure((0, 1, 2, 3), weight=1)

        for i, h in enumerate(["Port", "State", "Service", "Response"]):
            ctk.CTkLabel(header, text=h, font=FONTS["small"],
                        text_color=COLORS["text_muted"]).grid(row=0, column=i, padx=8, pady=6)

        self.scroll_frame = ctk.CTkScrollableFrame(self, fg_color="transparent")
        self.scroll_frame.grid(row=1, column=0, sticky="nsew", padx=2, pady=2)
        self.scroll_frame.grid_columnconfigure((0, 1, 2, 3), weight=1)

        self._row_count = 0

    def add_port_result(self, port_result):
        row = self._row_count
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
        for widget in self.scroll_frame.winfo_children():
            widget.destroy()
        self._row_count = 0


class LogConsole(ctk.CTkFrame):
    """Scrolling log output area with timestamps."""

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

        if self._line_count > self.max_lines:
            self.textbox.delete("1.0", "2.0")
            self._line_count -= 1

        self.textbox.see("end")
        self.textbox.configure(state="disabled")

    def clear(self):
        self.textbox.configure(state="normal")
        self.textbox.delete("1.0", "end")
        self.textbox.configure(state="disabled")
        self._line_count = 0
