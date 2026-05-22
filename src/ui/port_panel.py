"""
Port scanner panel UI.
"""

import customtkinter as ctk
from src.ui.theme import COLORS, FONTS, create_card, create_accent_button
from src.ui.components import ScanProgressBar, ScanResultTable


class PortPanel(ctk.CTkFrame):
    """Port scan interface - pick target, mode, see results."""

    def __init__(self, parent, scan_service=None, **kwargs):
        super().__init__(parent, fg_color="transparent", **kwargs)

        self.scan_service = scan_service
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(2, weight=1)

        self._build_header()
        self._build_controls()
        self._build_results()

    def _build_header(self):
        header = ctk.CTkFrame(self, fg_color="transparent")
        header.grid(row=0, column=0, sticky="ew", padx=16, pady=(16, 8))

        title = ctk.CTkLabel(header, text="Port Scanner",
                            font=FONTS["heading"], text_color=COLORS["text"])
        title.pack(anchor="w")

        desc = ctk.CTkLabel(header, text="Scan target hosts for open TCP ports and services",
                           font=FONTS["body"], text_color=COLORS["text_muted"])
        desc.pack(anchor="w", pady=(2, 0))

    def _build_controls(self):
        controls = create_card(self)
        controls.grid(row=1, column=0, sticky="ew", padx=16, pady=8)
        controls.grid_columnconfigure(1, weight=1)

        # Target IP input
        ctk.CTkLabel(controls, text="Target IP:", font=FONTS["body"],
                    text_color=COLORS["text_muted"]).grid(
                        row=0, column=0, padx=(16, 8), pady=(12, 4))

        self.target_entry = ctk.CTkEntry(controls, font=FONTS["mono"],
                                         fg_color=COLORS["input_bg"],
                                         border_color=COLORS["border"],
                                         text_color=COLORS["text"],
                                         placeholder_text="e.g., 192.168.1.1")
        self.target_entry.grid(row=0, column=1, sticky="ew", padx=4, pady=(12, 4))

        # Scan mode selector
        ctk.CTkLabel(controls, text="Mode:", font=FONTS["body"],
                    text_color=COLORS["text_muted"]).grid(
                        row=0, column=2, padx=(12, 8), pady=(12, 4))

        self.mode_var = ctk.StringVar(value="quick")
        mode_menu = ctk.CTkSegmentedButton(controls, values=["quick", "full", "custom"],
                                           variable=self.mode_var,
                                           font=FONTS["small"],
                                           fg_color=COLORS["bg_surface"],
                                           selected_color=COLORS["primary"],
                                           unselected_color=COLORS["card"])
        mode_menu.grid(row=0, column=3, padx=(0, 16), pady=(12, 4))

        # Custom port range (shown when custom mode selected)
        self.custom_frame = ctk.CTkFrame(controls, fg_color="transparent")
        self.custom_frame.grid(row=1, column=0, columnspan=4, sticky="ew",
                              padx=16, pady=(4, 4))

        ctk.CTkLabel(self.custom_frame, text="Port range:", font=FONTS["small"],
                    text_color=COLORS["text_muted"]).pack(side="left")

        self.port_start = ctk.CTkEntry(self.custom_frame, width=80, font=FONTS["mono"],
                                       fg_color=COLORS["input_bg"],
                                       border_color=COLORS["border"],
                                       text_color=COLORS["text"],
                                       placeholder_text="1")
        self.port_start.pack(side="left", padx=4)

        ctk.CTkLabel(self.custom_frame, text="to", font=FONTS["small"],
                    text_color=COLORS["text_muted"]).pack(side="left", padx=4)

        self.port_end = ctk.CTkEntry(self.custom_frame, width=80, font=FONTS["mono"],
                                     fg_color=COLORS["input_bg"],
                                     border_color=COLORS["border"],
                                     text_color=COLORS["text"],
                                     placeholder_text="1024")
        self.port_end.pack(side="left", padx=4)

        # Buttons
        btn_frame = ctk.CTkFrame(controls, fg_color="transparent")
        btn_frame.grid(row=2, column=0, columnspan=4, sticky="ew", padx=16, pady=(4, 8))

        self.scan_btn = create_accent_button(btn_frame, "Start Scan",
                                             command=self._start_scan)
        self.scan_btn.pack(side="left")

        self.stop_btn = create_accent_button(btn_frame, "Stop",
                                             command=self._stop_scan, color="error")
        self.stop_btn.pack(side="left", padx=(8, 0))
        self.stop_btn.configure(state="disabled", width=70)

        # Progress
        self.progress = ScanProgressBar(controls)
        self.progress.grid(row=3, column=0, columnspan=4, sticky="ew",
                          padx=16, pady=(4, 12))

    def _build_results(self):
        results_frame = ctk.CTkFrame(self, fg_color="transparent")
        results_frame.grid(row=2, column=0, sticky="nsew", padx=16, pady=(4, 16))
        results_frame.grid_columnconfigure(0, weight=1)
        results_frame.grid_rowconfigure(1, weight=1)

        # Results header with counter
        header = ctk.CTkFrame(results_frame, fg_color="transparent")
        header.grid(row=0, column=0, sticky="ew", pady=(0, 6))
        header.grid_columnconfigure(0, weight=1)

        ctk.CTkLabel(header, text="Scan Results",
                    font=FONTS["subheading"],
                    text_color=COLORS["text"]).grid(row=0, column=0, sticky="w")

        self.port_count_label = ctk.CTkLabel(header, text="0 open ports",
                                             font=FONTS["small"],
                                             text_color=COLORS["text_muted"])
        self.port_count_label.grid(row=0, column=1, sticky="e")

        # Port results table
        self.result_table = ScanResultTable(results_frame)
        self.result_table.grid(row=1, column=0, sticky="nsew")

    def _start_scan(self):
        if not self.scan_service:
            return

        target = self.target_entry.get().strip()
        if not target:
            return

        mode = self.mode_var.get()
        self.result_table.clear()
        self.progress.reset()
        self.progress.set_scanning(True)
        self.scan_btn.configure(state="disabled")
        self.stop_btn.configure(state="normal")
        self._open_count = 0

        # Determine port range based on mode
        ports = None
        port_range = None

        if mode == "full":
            port_range = (1, 1024)
        elif mode == "custom":
            try:
                start = int(self.port_start.get() or "1")
                end = int(self.port_end.get() or "1024")
                port_range = (start, end)
            except ValueError:
                port_range = (1, 1024)

        self.scan_service.start_port_scan(
            target_ip=target,
            ports=ports,
            port_range=port_range,
            on_port_found=self._on_port_found,
            on_progress=self._on_progress,
            on_complete=self._on_scan_complete
        )

    def _stop_scan(self):
        if self.scan_service:
            self.scan_service.port_scanner.stop_scan()
        self.progress.set_scanning(False)
        self.scan_btn.configure(state="normal")
        self.stop_btn.configure(state="disabled")

    def _on_port_found(self, port_result):
        self.after(0, lambda: self._add_port_result(port_result))

    def _add_port_result(self, port_result):
        self.result_table.add_port_result(port_result)
        self._open_count += 1
        self.port_count_label.configure(text=f"{self._open_count} open ports")

    def _on_progress(self, scanned, total):
        progress = scanned / total if total > 0 else 0
        self.after(0, lambda: self.progress.set_progress(
            progress, f"Scanning... {scanned}/{total} ports"))

    def _on_scan_complete(self, results, duration):
        def _update():
            self.progress.set_scanning(False)
            self.progress.set_progress(1.0,
                f"Complete - {len(results)} open ports ({duration:.1f}s)")
            self.scan_btn.configure(state="normal")
            self.stop_btn.configure(state="disabled")
        self.after(0, _update)

    def set_target(self, ip_address: str):
        self.target_entry.delete(0, "end")
        self.target_entry.insert(0, ip_address)
