"""
Main Application Window
Root window for Network Scanner Tool.
Manages navigation, panel switching, and top-level application state.
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
    """
    Main application window for Network Scanner Tool.
    Contains sidebar navigation and panel management.
    """

    def __init__(self):
        super().__init__()

        # Apply the Cyber Grid theme
        apply_theme()

        # Window configuration
        self.title(f"{APP_NAME} v{APP_VERSION}")
        self.geometry("1280x780")
        self.minsize(1024, 600)
        self.configure(fg_color=COLORS["bg_deep"])

        # Initialize backend services
        self.scan_service = ScanService()
        self.network_stats = NetworkStats()

        # Build the UI structure
        self._build_sidebar()
        self._build_main_area()
        self._init_panels()

        # Show dashboard by default
        self._show_panel("dashboard")

        # Handle window close
        self.protocol("WM_DELETE_WINDOW", self._on_close)

    def _build_sidebar(self):
        """Build the left navigation sidebar."""
        self.sidebar = ctk.CTkFrame(self, fg_color=COLORS["bg_surface"], width=220,
                                    corner_radius=0)
        self.sidebar.pack(side="left", fill="y")
        self.sidebar.pack_propagate(False)

        # App branding
        brand_frame = ctk.CTkFrame(self.sidebar, fg_color="transparent")
        brand_frame.pack(fill="x", padx=16, pady=(20, 24))

        app_icon = ctk.CTkLabel(brand_frame, text="◉", font=("Segoe UI", 24),
                                text_color=COLORS["primary"])
        app_icon.pack(side="left")

        title_frame = ctk.CTkFrame(brand_frame, fg_color="transparent")
        title_frame.pack(side="left", padx=(8, 0))

        ctk.CTkLabel(title_frame, text="NetScanner", font=("Segoe UI", 14, "bold"),
                    text_color=COLORS["text"]).pack(anchor="w")
        ctk.CTkLabel(title_frame, text=f"v{APP_VERSION}", font=FONTS["small"],
                    text_color=COLORS["text_muted"]).pack(anchor="w")

        # Navigation items
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

        # Spacer
        spacer = ctk.CTkFrame(self.sidebar, fg_color="transparent")
        spacer.pack(fill="both", expand=True)

        # Export button at bottom
        export_btn = ctk.CTkButton(self.sidebar, text="⬡  Export Report",
                                   font=FONTS["body"],
                                   fg_color=COLORS["card"],
                                   hover_color=COLORS["hover"],
                                   text_color=COLORS["text_muted"],
                                   anchor="w", height=36, corner_radius=6,
                                   command=self._export_report)
        export_btn.pack(fill="x", padx=12, pady=4)

        # Footer info
        footer = ctk.CTkFrame(self.sidebar, fg_color="transparent")
        footer.pack(fill="x", padx=16, pady=(8, 16))

        ctk.CTkLabel(footer, text=f"Built by {AUTHOR}",
                    font=FONTS["small"],
                    text_color=COLORS["text_muted"]).pack(anchor="w")

    def _build_main_area(self):
        """Build the main content area container."""
        self.main_area = ctk.CTkFrame(self, fg_color=COLORS["bg_deep"], corner_radius=0)
        self.main_area.pack(side="left", fill="both", expand=True)

    def _init_panels(self):
        """Initialize all panels (lazy creation for efficiency)."""
        self.panels = {}

        self.panels["dashboard"] = DashboardPanel(self.main_area,
                                                  scan_service=self.scan_service)
        self.panels["scanner"] = ScannerPanel(self.main_area,
                                              scan_service=self.scan_service)
        self.panels["ports"] = PortPanel(self.main_area,
                                         scan_service=self.scan_service)
        self.panels["diagnostics"] = DiagnosticsPanel(self.main_area,
                                                      scan_service=self.scan_service)

        # Wire up dashboard quick actions
        self.panels["dashboard"]._handle_action = self._handle_dashboard_action

        self.active_panel = None

    def _show_panel(self, panel_id: str):
        """Switch to the specified panel view."""
        # Hide current panel
        if self.active_panel:
            self.active_panel.pack_forget()

        # Update navigation highlighting
        for btn_id, btn in self.nav_buttons.items():
            if btn_id == panel_id:
                btn.configure(fg_color=COLORS["primary"], text_color=COLORS["text"])
            else:
                btn.configure(fg_color="transparent", text_color=COLORS["text_muted"])

        # Show selected panel
        panel = self.panels.get(panel_id)
        if panel:
            panel.pack(fill="both", expand=True)
            self.active_panel = panel

    def _handle_dashboard_action(self, action_id: str):
        """Route quick action clicks from the dashboard."""
        action_map = {
            "scan_network": "scanner",
            "scan_ports": "ports",
            "ping": "diagnostics",
            "dns": "diagnostics",
            "export": None,
        }

        if action_id == "export":
            self._export_report()
        else:
            target_panel = action_map.get(action_id)
            if target_panel:
                self._show_panel(target_panel)

    def _export_report(self):
        """Export scan results to a report file."""
        filepath = self.scan_service.export_report("network")
        if filepath:
            # Log to dashboard
            dashboard = self.panels.get("dashboard")
            if dashboard:
                dashboard.log_console.log(f"Report exported: {filepath}", "success")
        else:
            dashboard = self.panels.get("dashboard")
            if dashboard:
                dashboard.log_console.log("No scan data to export. Run a scan first.", "warning")

    def _on_close(self):
        """Clean up resources before closing."""
        self.scan_service.stop_all()
        self.destroy()
        sys.exit(0)

    def run(self):
        """Start the application main loop."""
        self.mainloop()
