"""
Main app window - sidebar nav + panel switching.
"""

import customtkinter as ctk
import sys
import os

from src.ui.theme import apply_theme, COLORS, FONTS
from src.ui.dashboard_panel import DashboardPanel
from src.ui.scanner_panel import ScannerPanel
from src.ui.port_panel import PortPanel
from src.ui.diagnostics_panel import DiagnosticsPanel
from src.services.scan_service import ScanService
from src.analytics.network_stats import NetworkStats
from src.utils.constants import APP_NAME, APP_VERSION, AUTHOR


class NetworkScannerApp(ctk.CTk):

    def __init__(self):
        super().__init__()
        apply_theme()

        self.title(f"{APP_NAME} v{APP_VERSION}")
        self.geometry("1280x780")
        self.minsize(1024, 600)
        self.configure(fg_color=COLORS["bg_deep"])

        self.scan_service = ScanService()
        self.network_stats = NetworkStats()

        self._build_sidebar()
        self._build_main_area()
        self._init_panels()
        self._show_panel("dashboard")

        self.protocol("WM_DELETE_WINDOW", self._on_close)

    def _build_sidebar(self):
        self.sidebar = ctk.CTkFrame(self, fg_color=COLORS["bg_surface"], width=220,
                                    corner_radius=0)
        self.sidebar.pack(side="left", fill="y")
        self.sidebar.pack_propagate(False)

        # branding
        brand_frame = ctk.CTkFrame(self.sidebar, fg_color="transparent")
        brand_frame.pack(fill="x", padx=16, pady=(20, 24))

        ctk.CTkLabel(brand_frame, text="◉", font=("Segoe UI", 24),
                     text_color=COLORS["primary"]).pack(side="left")

        title_frame = ctk.CTkFrame(brand_frame, fg_color="transparent")
        title_frame.pack(side="left", padx=(8, 0))
        ctk.CTkLabel(title_frame, text="NetScanner", font=("Segoe UI", 14, "bold"),
                    text_color=COLORS["text"]).pack(anchor="w")
        ctk.CTkLabel(title_frame, text=f"v{APP_VERSION}", font=FONTS["small"],
                    text_color=COLORS["text_muted"]).pack(anchor="w")

        # nav buttons
        self.nav_buttons = {}
        nav_items = [
            ("dashboard", "◫  Dashboard"),
            ("scanner", "◎  Network Scan"),
            ("ports", "⊡  Port Scanner"),
            ("diagnostics", "◈  Diagnostics"),
        ]

        for panel_id, label in nav_items:
            btn = ctk.CTkButton(self.sidebar, text=label, font=FONTS["body"],
                               fg_color="transparent", text_color=COLORS["text_muted"],
                               hover_color=COLORS["hover"], anchor="w",
                               height=40, corner_radius=6,
                               command=lambda pid=panel_id: self._show_panel(pid))
            btn.pack(fill="x", padx=12, pady=2)
            self.nav_buttons[panel_id] = btn

        # push export to bottom
        ctk.CTkFrame(self.sidebar, fg_color="transparent").pack(fill="both", expand=True)

        ctk.CTkButton(self.sidebar, text="⬡  Export Report", font=FONTS["body"],
                     fg_color=COLORS["card"], hover_color=COLORS["hover"],
                     text_color=COLORS["text_muted"], anchor="w",
                     height=36, corner_radius=6,
                     command=self._export_report).pack(fill="x", padx=12, pady=4)

        footer = ctk.CTkFrame(self.sidebar, fg_color="transparent")
        footer.pack(fill="x", padx=16, pady=(8, 16))
        ctk.CTkLabel(footer, text=f"Built by {AUTHOR}", font=FONTS["small"],
                    text_color=COLORS["text_muted"]).pack(anchor="w")

    def _build_main_area(self):
        self.main_area = ctk.CTkFrame(self, fg_color=COLORS["bg_deep"], corner_radius=0)
        self.main_area.pack(side="left", fill="both", expand=True)

    def _init_panels(self):
        self.panels = {
            "dashboard": DashboardPanel(self.main_area, scan_service=self.scan_service),
            "scanner": ScannerPanel(self.main_area, scan_service=self.scan_service),
            "ports": PortPanel(self.main_area, scan_service=self.scan_service),
            "diagnostics": DiagnosticsPanel(self.main_area, scan_service=self.scan_service),
        }
        self.panels["dashboard"]._handle_action = self._handle_dashboard_action
        self.active_panel = None

    def _show_panel(self, panel_id: str):
        if self.active_panel:
            self.active_panel.pack_forget()

        for btn_id, btn in self.nav_buttons.items():
            if btn_id == panel_id:
                btn.configure(fg_color=COLORS["primary"], text_color=COLORS["text"])
            else:
                btn.configure(fg_color="transparent", text_color=COLORS["text_muted"])

        panel = self.panels.get(panel_id)
        if panel:
            panel.pack(fill="both", expand=True)
            self.active_panel = panel

    def _handle_dashboard_action(self, action_id: str):
        action_map = {
            "scan_network": "scanner",
            "scan_ports": "ports",
            "ping": "diagnostics",
            "dns": "diagnostics",
        }
        if action_id == "export":
            self._export_report()
        else:
            target = action_map.get(action_id)
            if target:
                self._show_panel(target)

    def _export_report(self):
        filepath = self.scan_service.export_report("network")
        dashboard = self.panels.get("dashboard")
        if filepath and dashboard:
            dashboard.log_console.log(f"Report saved: {filepath}", "success")
        elif dashboard:
            dashboard.log_console.log("No scan data to export yet", "warning")

    def _on_close(self):
        self.scan_service.stop_all()
        self.destroy()
        sys.exit(0)

    def run(self):
        self.mainloop()
