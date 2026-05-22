"""
Diagnostics panel - ping, DNS, traceroute tabs.
"""

import customtkinter as ctk
from src.ui.theme import COLORS, FONTS, create_card, create_accent_button
from src.ui.components import LogConsole


class DiagnosticsPanel(ctk.CTkFrame):
    """Tabbed diagnostics: ping, DNS, traceroute."""

    def __init__(self, parent, scan_service=None, **kwargs):
        super().__init__(parent, fg_color="transparent", **kwargs)

        self.scan_service = scan_service
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(1, weight=1)

        self._build_header()
        self._build_tools()

    def _build_header(self):
        header = ctk.CTkFrame(self, fg_color="transparent")
        header.grid(row=0, column=0, sticky="ew", padx=16, pady=(16, 8))

        title = ctk.CTkLabel(header, text="Diagnostic Tools",
                            font=FONTS["heading"], text_color=COLORS["text"])
        title.pack(anchor="w")

        desc = ctk.CTkLabel(header,
                           text="Quick network diagnostics - ping, DNS lookup, and traceroute",
                           font=FONTS["body"], text_color=COLORS["text_muted"])
        desc.pack(anchor="w", pady=(2, 0))

    def _build_tools(self):
        # Tab container
        self.tabview = ctk.CTkTabview(self, fg_color=COLORS["bg_surface"],
                                      segmented_button_fg_color=COLORS["card"],
                                      segmented_button_selected_color=COLORS["primary"],
                                      segmented_button_unselected_color=COLORS["bg_surface"],
                                      corner_radius=8)
        self.tabview.grid(row=1, column=0, sticky="nsew", padx=16, pady=(0, 16))

        # Create tabs
        self.tab_ping = self.tabview.add("Ping")
        self.tab_dns = self.tabview.add("DNS Lookup")
        self.tab_trace = self.tabview.add("Traceroute")

        self._build_ping_tab()
        self._build_dns_tab()
        self._build_trace_tab()

    def _build_ping_tab(self):
        tab = self.tab_ping
        tab.grid_columnconfigure(0, weight=1)
        tab.grid_rowconfigure(1, weight=1)

        # Input area
        input_frame = ctk.CTkFrame(tab, fg_color="transparent")
        input_frame.grid(row=0, column=0, sticky="ew", pady=(8, 8))
        input_frame.grid_columnconfigure(1, weight=1)

        ctk.CTkLabel(input_frame, text="Host:", font=FONTS["body"],
                    text_color=COLORS["text_muted"]).grid(row=0, column=0, padx=(0, 8))

        self.ping_entry = ctk.CTkEntry(input_frame, font=FONTS["mono"],
                                       fg_color=COLORS["input_bg"],
                                       border_color=COLORS["border"],
                                       text_color=COLORS["text"],
                                       placeholder_text="e.g., 8.8.8.8 or google.com")
        self.ping_entry.grid(row=0, column=1, sticky="ew", padx=4)

        ctk.CTkLabel(input_frame, text="Count:", font=FONTS["body"],
                    text_color=COLORS["text_muted"]).grid(row=0, column=2, padx=(8, 4))

        self.ping_count = ctk.CTkEntry(input_frame, width=50, font=FONTS["mono"],
                                       fg_color=COLORS["input_bg"],
                                       border_color=COLORS["border"],
                                       text_color=COLORS["text"])
        self.ping_count.grid(row=0, column=3, padx=4)
        self.ping_count.insert(0, "4")

        self.ping_btn = create_accent_button(input_frame, "Ping",
                                             command=self._run_ping)
        self.ping_btn.grid(row=0, column=4, padx=(8, 0))

        # Output console
        self.ping_output = LogConsole(tab)
        self.ping_output.grid(row=1, column=0, sticky="nsew", pady=(4, 0))

    def _build_dns_tab(self):
        tab = self.tab_dns
        tab.grid_columnconfigure(0, weight=1)
        tab.grid_rowconfigure(1, weight=1)

        # Input area
        input_frame = ctk.CTkFrame(tab, fg_color="transparent")
        input_frame.grid(row=0, column=0, sticky="ew", pady=(8, 8))
        input_frame.grid_columnconfigure(1, weight=1)

        ctk.CTkLabel(input_frame, text="Query:", font=FONTS["body"],
                    text_color=COLORS["text_muted"]).grid(row=0, column=0, padx=(0, 8))

        self.dns_entry = ctk.CTkEntry(input_frame, font=FONTS["mono"],
                                      fg_color=COLORS["input_bg"],
                                      border_color=COLORS["border"],
                                      text_color=COLORS["text"],
                                      placeholder_text="e.g., example.com or 8.8.8.8")
        self.dns_entry.grid(row=0, column=1, sticky="ew", padx=4)

        self.dns_btn = create_accent_button(input_frame, "Resolve",
                                            command=self._run_dns,
                                            color="warning")
        self.dns_btn.grid(row=0, column=2, padx=(8, 0))

        # Output console
        self.dns_output = LogConsole(tab)
        self.dns_output.grid(row=1, column=0, sticky="nsew", pady=(4, 0))

    def _build_trace_tab(self):
        tab = self.tab_trace
        tab.grid_columnconfigure(0, weight=1)
        tab.grid_rowconfigure(1, weight=1)

        # Input area
        input_frame = ctk.CTkFrame(tab, fg_color="transparent")
        input_frame.grid(row=0, column=0, sticky="ew", pady=(8, 8))
        input_frame.grid_columnconfigure(1, weight=1)

        ctk.CTkLabel(input_frame, text="Target:", font=FONTS["body"],
                    text_color=COLORS["text_muted"]).grid(row=0, column=0, padx=(0, 8))

        self.trace_entry = ctk.CTkEntry(input_frame, font=FONTS["mono"],
                                        fg_color=COLORS["input_bg"],
                                        border_color=COLORS["border"],
                                        text_color=COLORS["text"],
                                        placeholder_text="e.g., 8.8.8.8 or google.com")
        self.trace_entry.grid(row=0, column=1, sticky="ew", padx=4)

        self.trace_btn = create_accent_button(input_frame, "Trace",
                                              command=self._run_traceroute,
                                              color="secondary")
        self.trace_btn.grid(row=0, column=2, padx=(8, 0))

        # Output console
        self.trace_output = LogConsole(tab)
        self.trace_output.grid(row=1, column=0, sticky="nsew", pady=(4, 0))

    def _run_ping(self):
        if not self.scan_service:
            return

        target = self.ping_entry.get().strip()
        if not target:
            self.ping_output.log("Please enter a target hostname or IP", "warning")
            return

        try:
            count = int(self.ping_count.get() or "4")
        except ValueError:
            count = 4

        self.ping_output.clear()
        self.ping_output.log(f"Pinging {target} with {count} requests...", "scan")
        self.ping_btn.configure(state="disabled")

        def on_result(ping_result):
            if ping_result.success:
                self.after(0, lambda: self.ping_output.log(
                    f"Reply: time={ping_result.response_time:.1f}ms TTL={ping_result.ttl}",
                    "success"))
            else:
                self.after(0, lambda: self.ping_output.log(
                    f"Request timed out", "error"))

        def on_complete(stats):
            def _update():
                self.ping_output.log("", "info")
                self.ping_output.log(f"--- Ping Statistics for {stats.target} ---", "info")
                self.ping_output.log(
                    f"Packets: sent={stats.packets_sent}, received={stats.packets_received}, "
                    f"loss={stats.loss_percentage:.0f}%", "info")
                if stats.packets_received > 0:
                    self.ping_output.log(
                        f"RTT: min={stats.min_time:.1f}ms, avg={stats.avg_time:.1f}ms, "
                        f"max={stats.max_time:.1f}ms", "info")
                self.ping_btn.configure(state="normal")
            self.after(0, _update)

        self.scan_service.run_ping(target, count=count,
                                   on_result=on_result,
                                   on_complete=on_complete)

    def _run_dns(self):
        if not self.scan_service:
            return

        query = self.dns_entry.get().strip()
        if not query:
            self.dns_output.log("Please enter a hostname or IP address", "warning")
            return

        self.dns_output.clear()
        self.dns_output.log(f"Resolving: {query}", "scan")
        self.dns_btn.configure(state="disabled")

        def on_complete(result):
            def _update():
                if result.success:
                    self.dns_output.log(f"Query: {result.query}", "info")

                    if result.hostname:
                        self.dns_output.log(f"Hostname: {result.hostname}", "success")

                    if result.resolved_ips:
                        for ip in result.resolved_ips:
                            self.dns_output.log(f"Address: {ip}", "success")

                    if result.aliases:
                        for alias in result.aliases:
                            self.dns_output.log(f"Alias: {alias}", "info")

                    if result.nameserver:
                        self.dns_output.log(f"Server: {result.nameserver}", "info")

                    self.dns_output.log(
                        f"Lookup time: {result.lookup_time:.1f}ms", "info")
                else:
                    self.dns_output.log(f"Lookup failed: {result.error}", "error")

                self.dns_btn.configure(state="normal")
            self.after(0, _update)

        self.scan_service.run_dns_lookup(query, on_complete=on_complete)

    def _run_traceroute(self):
        if not self.scan_service:
            return

        target = self.trace_entry.get().strip()
        if not target:
            self.trace_output.log("Please enter a target hostname or IP", "warning")
            return

        self.trace_output.clear()
        self.trace_output.log(f"Tracing route to {target}...", "scan")
        self.trace_output.log("(This may take a moment)", "info")
        self.trace_btn.configure(state="disabled")

        def on_hop(hop):
            def _update():
                if hop.is_timeout:
                    self.trace_output.log(f"  {hop.hop_number:>2}  * * * (timeout)", "warning")
                else:
                    rtt_str = ", ".join(f"{t:.1f}ms" for t in hop.rtt_times) if hop.rtt_times else "N/A"
                    host = hop.hostname or hop.ip_address or "*"
                    self.trace_output.log(f"  {hop.hop_number:>2}  {host:<40} {rtt_str}", "success")
            self.after(0, _update)

        def on_complete(result):
            def _update():
                self.trace_output.log("", "info")
                if result.completed:
                    self.trace_output.log(
                        f"Trace complete: {len(result.hops)} hops, "
                        f"{result.total_time:.0f}ms total", "success")
                elif result.error:
                    self.trace_output.log(f"Error: {result.error}", "error")
                else:
                    self.trace_output.log(
                        f"Trace ended: {len(result.hops)} hops (destination not reached)", "warning")
                self.trace_btn.configure(state="normal")
            self.after(0, _update)

        self.scan_service.run_traceroute(target, on_hop=on_hop, on_complete=on_complete)
