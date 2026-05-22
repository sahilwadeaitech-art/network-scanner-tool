"""
Dashboard - overview stats, activity log, quick action buttons.
"""

import customtkinter as ctk
from src.ui.theme import COLORS, FONTS, create_card, create_accent_button
from src.ui.components import StatCard, LogConsole


class DashboardPanel(ctk.CTkFrame):
    """Main dashboard with stat cards, log, and quick actions."""

    def __init__(self, parent, scan_service=None, **kwargs):
        super().__init__(parent, fg_color="transparent", **kwargs)

        self.scan_service = scan_service
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(2, weight=1)

        self._build_header()
        self._build_stats_row()
        self._build_content_area()

    def _build_header(self):
        header = ctk.CTkFrame(self, fg_color="transparent")
        header.grid(row=0, column=0, sticky="ew", padx=16, pady=(16, 8))

        title = ctk.CTkLabel(header, text="Network Overview",
                            font=FONTS["heading"], text_color=COLORS["text"])
        title.pack(anchor="w")

        # Local network info
        if self.scan_service:
            info = self.scan_service.get_local_info()
            subtitle = f"Local: {info['local_ip']}  •  Subnet: {info['subnet']}"
        else:
            subtitle = "Network Scanner Tool"

        sub = ctk.CTkLabel(header, text=subtitle,
                          font=FONTS["body"], text_color=COLORS["text_muted"])
        sub.pack(anchor="w", pady=(2, 0))

    def _build_stats_row(self):
        stats_frame = ctk.CTkFrame(self, fg_color="transparent")
        stats_frame.grid(row=1, column=0, sticky="ew", padx=16, pady=8)
        stats_frame.grid_columnconfigure((0, 1, 2, 3), weight=1)

        self.card_devices = StatCard(stats_frame, title="Active Devices",
                                     value="0", icon="⬡",
                                     accent_color=COLORS["primary"])
        self.card_devices.grid(row=0, column=0, sticky="ew", padx=(0, 6), pady=4)

        self.card_ports = StatCard(stats_frame, title="Open Ports",
                                   value="0", icon="⊡",
                                   accent_color=COLORS["secondary"])
        self.card_ports.grid(row=0, column=1, sticky="ew", padx=6, pady=4)

        self.card_latency = StatCard(stats_frame, title="Avg Latency",
                                     value="—", icon="◈",
                                     accent_color=COLORS["highlight"])
        self.card_latency.grid(row=0, column=2, sticky="ew", padx=6, pady=4)

        self.card_health = StatCard(stats_frame, title="Health Score",
                                    value="—", icon="◉",
                                    accent_color=COLORS["success"])
        self.card_health.grid(row=0, column=3, sticky="ew", padx=(6, 0), pady=4)

    def _build_content_area(self):
        content = ctk.CTkFrame(self, fg_color="transparent")
        content.grid(row=2, column=0, sticky="nsew", padx=16, pady=(8, 16))
        content.grid_columnconfigure(0, weight=2)
        content.grid_columnconfigure(1, weight=1)
        content.grid_rowconfigure(0, weight=1)

        # Activity log
        log_section = create_card(content)
        log_section.grid(row=0, column=0, sticky="nsew", padx=(0, 6))
        log_section.grid_columnconfigure(0, weight=1)
        log_section.grid_rowconfigure(1, weight=1)

        log_header = ctk.CTkLabel(log_section, text="  Activity Log",
                                  font=FONTS["subheading"], text_color=COLORS["text"])
        log_header.grid(row=0, column=0, sticky="w", padx=12, pady=(12, 4))

        self.log_console = LogConsole(log_section)
        self.log_console.grid(row=1, column=0, sticky="nsew", padx=8, pady=(4, 8))

        # Initial log entries
        self.log_console.log("Network Scanner Tool initialized", "info")
        if self.scan_service:
            info = self.scan_service.get_local_info()
            self.log_console.log(f"Local IP: {info['local_ip']}", "info")
            self.log_console.log(f"Subnet: {info['subnet']}", "info")
        self.log_console.log("Ready to scan", "success")

        # Quick actions panel
        actions_frame = create_card(content)
        actions_frame.grid(row=0, column=1, sticky="nsew", padx=(6, 0))
        actions_frame.grid_columnconfigure(0, weight=1)

        actions_title = ctk.CTkLabel(actions_frame, text="  Quick Actions",
                                     font=FONTS["subheading"], text_color=COLORS["text"])
        actions_title.grid(row=0, column=0, sticky="w", padx=12, pady=(12, 8))

        # Quick action buttons
        actions = [
            ("Network Scan", COLORS["primary"], "scan_network"),
            ("Port Scan", COLORS["secondary"], "scan_ports"),
            ("Ping Test", COLORS["highlight"], "ping"),
            ("DNS Lookup", COLORS["warning"], "dns"),
            ("Export Report", COLORS["text_muted"], "export"),
        ]

        for i, (text, color, action_id) in enumerate(actions):
            btn = ctk.CTkButton(actions_frame, text=text,
                               fg_color=color, hover_color=COLORS["hover"],
                               font=FONTS["body_bold"], height=36, corner_radius=6)
            btn.grid(row=i + 1, column=0, sticky="ew", padx=12, pady=4)
            btn.configure(command=lambda a=action_id: self._handle_action(a))

        # Network info card at bottom
        info_card = ctk.CTkFrame(actions_frame, fg_color=COLORS["bg_deep"],
                                 corner_radius=6)
        info_card.grid(row=len(actions) + 1, column=0, sticky="ew",
                      padx=12, pady=(16, 12))

        ctk.CTkLabel(info_card, text="Scanner Status",
                    font=FONTS["small"], text_color=COLORS["text_muted"]).pack(
                        anchor="w", padx=12, pady=(8, 2))

        self.status_indicator = ctk.CTkLabel(info_card, text="● Idle",
                                             font=FONTS["body"],
                                             text_color=COLORS["success"])
        self.status_indicator.pack(anchor="w", padx=12, pady=(0, 8))

    def update_stats(self, stats: dict):
        self.card_devices.update_value(str(stats.get("active_devices", 0)))
        self.card_ports.update_value(str(stats.get("total_open_ports", 0)))

        avg_lat = stats.get("avg_latency", 0)
        self.card_latency.update_value(f"{avg_lat:.1f}ms" if avg_lat > 0 else "—")

        health = stats.get("health_score", 0)
        self.card_health.update_value(f"{health:.0f}" if health > 0 else "—")

    def set_scanning_state(self, is_scanning: bool):
        if is_scanning:
            self.status_indicator.configure(text="● Scanning", text_color=COLORS["secondary"])
        else:
            self.status_indicator.configure(text="● Idle", text_color=COLORS["success"])

    def _handle_action(self, action_id: str):
        # overridden by the main app window
        pass
