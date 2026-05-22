"""
Network scan panel - device discovery UI.
"""

import customtkinter as ctk
import threading
from src.ui.theme import COLORS, FONTS, create_card, create_accent_button
from src.ui.components import ScanProgressBar, DeviceListItem


class ScannerPanel(ctk.CTkFrame):
    """Network discovery panel - scan subnet, show found devices."""

    def __init__(self, parent, scan_service=None, **kwargs):
        super().__init__(parent, fg_color="transparent", **kwargs)

        self.scan_service = scan_service
        self._device_widgets = []

        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(2, weight=1)

        self._build_header()
        self._build_controls()
        self._build_results_area()

    def _build_header(self):
        header = ctk.CTkFrame(self, fg_color="transparent")
        header.grid(row=0, column=0, sticky="ew", padx=16, pady=(16, 8))
        header.grid_columnconfigure(0, weight=1)

        title = ctk.CTkLabel(header, text="Network Discovery",
                            font=FONTS["heading"], text_color=COLORS["text"])
        title.grid(row=0, column=0, sticky="w")

        desc = ctk.CTkLabel(header, text="Scan your local network for active devices",
                           font=FONTS["body"], text_color=COLORS["text_muted"])
        desc.grid(row=1, column=0, sticky="w", pady=(2, 0))

    def _build_controls(self):
        controls = create_card(self)
        controls.grid(row=1, column=0, sticky="ew", padx=16, pady=8)
        controls.grid_columnconfigure(1, weight=1)

        # Target subnet input
        ctk.CTkLabel(controls, text="Target:", font=FONTS["body"],
                    text_color=COLORS["text_muted"]).grid(
                        row=0, column=0, padx=(16, 8), pady=12)

        # Get default subnet
        default_subnet = ""
        if self.scan_service:
            info = self.scan_service.get_local_info()
            default_subnet = info.get("subnet", "")

        self.target_entry = ctk.CTkEntry(controls, font=FONTS["mono"],
                                         fg_color=COLORS["input_bg"],
                                         border_color=COLORS["border"],
                                         text_color=COLORS["text"],
                                         placeholder_text="e.g., 192.168.1.0/24")
        self.target_entry.grid(row=0, column=1, sticky="ew", padx=4, pady=12)
        if default_subnet:
            self.target_entry.insert(0, default_subnet)

        # Scan button
        self.scan_btn = create_accent_button(controls, "Scan Network",
                                             command=self._start_scan)
        self.scan_btn.grid(row=0, column=2, padx=(8, 16), pady=12)

        self.stop_btn = create_accent_button(controls, "Stop",
                                             command=self._stop_scan,
                                             color="error")
        self.stop_btn.grid(row=0, column=3, padx=(0, 16), pady=12)
        self.stop_btn.configure(state="disabled", width=70)

        # Progress bar
        self.progress = ScanProgressBar(controls)
        self.progress.grid(row=1, column=0, columnspan=4, sticky="ew",
                          padx=16, pady=(0, 12))

    def _build_results_area(self):
        results_frame = ctk.CTkFrame(self, fg_color="transparent")
        results_frame.grid(row=2, column=0, sticky="nsew", padx=16, pady=(4, 16))
        results_frame.grid_columnconfigure(0, weight=1)
        results_frame.grid_rowconfigure(1, weight=1)

        # Results header
        header_frame = ctk.CTkFrame(results_frame, fg_color="transparent")
        header_frame.grid(row=0, column=0, sticky="ew", pady=(0, 6))
        header_frame.grid_columnconfigure(0, weight=1)

        self.results_label = ctk.CTkLabel(header_frame, text="Discovered Devices",
                                          font=FONTS["subheading"],
                                          text_color=COLORS["text"])
        self.results_label.grid(row=0, column=0, sticky="w")

        self.count_label = ctk.CTkLabel(header_frame, text="0 devices",
                                        font=FONTS["small"],
                                        text_color=COLORS["text_muted"])
        self.count_label.grid(row=0, column=1, sticky="e")

        # Scrollable device list
        self.device_list = ctk.CTkScrollableFrame(results_frame,
                                                  fg_color=COLORS["bg_surface"],
                                                  corner_radius=8)
        self.device_list.grid(row=1, column=0, sticky="nsew")
        self.device_list.grid_columnconfigure(0, weight=1)

        # Empty state message
        self.empty_label = ctk.CTkLabel(self.device_list,
                                        text="\n\nNo devices discovered yet.\nClick 'Scan Network' to begin.\n",
                                        font=FONTS["body"],
                                        text_color=COLORS["text_muted"])
        self.empty_label.grid(row=0, column=0, pady=40)

    def _start_scan(self):
        if not self.scan_service:
            return

        if self.scan_service.state.is_network_scanning:
            return

        # Clear previous results
        self._clear_devices()
        self.progress.reset()
        self.progress.set_scanning(True)
        self.scan_btn.configure(state="disabled")
        self.stop_btn.configure(state="normal")

        target = self.target_entry.get().strip()
        if not target:
            info = self.scan_service.get_local_info()
            target = info.get("subnet", "")

        self.scan_service.start_network_scan(
            target_subnet=target,
            on_device_found=self._on_device_found,
            on_progress=self._on_progress,
            on_complete=self._on_scan_complete
        )

    def _stop_scan(self):
        if self.scan_service:
            self.scan_service.stop_all()
        self.progress.set_scanning(False)
        self.scan_btn.configure(state="normal")
        self.stop_btn.configure(state="disabled")

    def _on_device_found(self, device):
        self.after(0, lambda: self._add_device_to_list(device))

    def _on_progress(self, scanned, total):
        progress = scanned / total if total > 0 else 0
        self.after(0, lambda: self.progress.set_progress(
            progress, f"Scanning... {scanned}/{total} hosts"))

    def _on_scan_complete(self, results):
        def _update():
            self.progress.set_scanning(False)
            self.progress.set_progress(1.0, f"Complete - {len(results)} devices found")
            self.scan_btn.configure(state="normal")
            self.stop_btn.configure(state="disabled")
            self.count_label.configure(text=f"{len(results)} devices")
        self.after(0, _update)

    def _add_device_to_list(self, device):
        # Hide empty state
        if self.empty_label.winfo_exists():
            self.empty_label.grid_forget()

        device_data = device.to_dict()
        item = DeviceListItem(self.device_list, device_data,
                             on_select=self._on_device_select)
        item.grid(row=len(self._device_widgets), column=0,
                 sticky="ew", padx=4, pady=2)
        self._device_widgets.append(item)

        count = len(self._device_widgets)
        self.count_label.configure(text=f"{count} devices")

    def _on_device_select(self, device_data):
        pass

    def _clear_devices(self):
        for widget in self._device_widgets:
            widget.destroy()
        self._device_widgets = []
        self.count_label.configure(text="0 devices")

        # Show empty state again
        self.empty_label = ctk.CTkLabel(self.device_list,
                                        text="\n\nScanning...\n",
                                        font=FONTS["body"],
                                        text_color=COLORS["text_muted"])
        self.empty_label.grid(row=0, column=0, pady=40)
