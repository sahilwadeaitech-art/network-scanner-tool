"""
Scan service - coordinates the scanner, port scanner, and diagnostic tools.
Manages background threads and exposes callbacks for the UI.
"""

import threading
import time
from typing import Optional, Callable, List
from dataclasses import dataclass

from src.scanner.network_scanner import NetworkScanner, DeviceInfo
from src.scanner.port_scanner import PortScanner, PortResult
from src.diagnostics.ping import PingTool, PingStats
from src.diagnostics.dns_lookup import DNSLookup, DNSResult
from src.diagnostics.traceroute import TracerouteTool, TracerouteResult
from src.services.report_generator import ReportGenerator
from src.utils.network_utils import get_local_ip, get_subnet


@dataclass
class ScanState:
    is_network_scanning: bool = False
    is_port_scanning: bool = False
    is_diagnostic_running: bool = False
    network_progress: float = 0.0
    port_progress: float = 0.0
    devices_found: int = 0
    ports_found: int = 0
    scan_start_time: float = 0.0
    last_scan_duration: float = 0.0


class ScanService:
    """Ties everything together. UI talks to this, this talks to scanners."""

    def __init__(self):
        self.network_scanner = NetworkScanner()
        self.port_scanner = PortScanner()
        self.ping_tool = PingTool()
        self.dns_tool = DNSLookup()
        self.traceroute_tool = TracerouteTool()
        self.report_gen = ReportGenerator()
        self.state = ScanState()

        self.discovered_devices: List[DeviceInfo] = []
        self.port_results: dict = {}
        self.last_ping: Optional[PingStats] = None
        self.last_dns: Optional[DNSResult] = None
        self.last_traceroute: Optional[TracerouteResult] = None

    def start_network_scan(self, target_subnet: Optional[str] = None,
                           on_device_found: Optional[Callable] = None,
                           on_progress: Optional[Callable] = None,
                           on_complete: Optional[Callable] = None):
        """Kick off network scan in background thread."""
        if self.state.is_network_scanning:
            return

        def _scan_thread():
            self.state.is_network_scanning = True
            self.state.scan_start_time = time.time()
            self.discovered_devices = []

            subnet = target_subnet or get_subnet()

            def _on_device(device):
                self.state.devices_found = len(self.discovered_devices) + 1
                if on_device_found:
                    on_device_found(device)

            def _on_progress(scanned, total):
                self.state.network_progress = scanned / total if total > 0 else 0
                if on_progress:
                    on_progress(scanned, total)

            results = self.network_scanner.scan_network(
                target_subnet=subnet,
                callback=_on_device,
                progress_callback=_on_progress
            )

            self.discovered_devices = results
            self.state.is_network_scanning = False
            self.state.last_scan_duration = time.time() - self.state.scan_start_time

            if on_complete:
                on_complete(results)

        threading.Thread(target=_scan_thread, daemon=True).start()

    def start_port_scan(self, target_ip: str, ports=None, port_range=None,
                        on_port_found: Optional[Callable] = None,
                        on_progress: Optional[Callable] = None,
                        on_complete: Optional[Callable] = None):
        """Port scan in background thread."""
        if self.state.is_port_scanning:
            return

        def _scan_thread():
            self.state.is_port_scanning = True
            self.state.ports_found = 0
            start = time.time()

            def _on_port(result):
                self.state.ports_found += 1
                if on_port_found:
                    on_port_found(result)

            def _on_progress(scanned, total):
                self.state.port_progress = scanned / total if total > 0 else 0
                if on_progress:
                    on_progress(scanned, total)

            results = self.port_scanner.scan_ports(
                target_ip=target_ip, ports=ports, port_range=port_range,
                callback=_on_port, progress_callback=_on_progress
            )

            self.port_results[target_ip] = results
            self.state.is_port_scanning = False
            duration = time.time() - start

            if on_complete:
                on_complete(results, duration)

        threading.Thread(target=_scan_thread, daemon=True).start()

    def run_ping(self, target: str, count: int = 4,
                 on_result: Optional[Callable] = None,
                 on_complete: Optional[Callable] = None):
        def _ping_thread():
            self.state.is_diagnostic_running = True
            stats = self.ping_tool.ping(target, count=count, callback=on_result)
            self.last_ping = stats
            self.state.is_diagnostic_running = False
            if on_complete:
                on_complete(stats)

        threading.Thread(target=_ping_thread, daemon=True).start()

    def run_dns_lookup(self, query: str, on_complete: Optional[Callable] = None):
        def _dns_thread():
            self.state.is_diagnostic_running = True
            result = self.dns_tool.lookup(query)
            self.last_dns = result
            self.state.is_diagnostic_running = False
            if on_complete:
                on_complete(result)

        threading.Thread(target=_dns_thread, daemon=True).start()

    def run_traceroute(self, target: str,
                       on_hop: Optional[Callable] = None,
                       on_complete: Optional[Callable] = None):
        def _trace_thread():
            self.state.is_diagnostic_running = True
            result = self.traceroute_tool.trace(target, callback=on_hop)
            self.last_traceroute = result
            self.state.is_diagnostic_running = False
            if on_complete:
                on_complete(result)

        threading.Thread(target=_trace_thread, daemon=True).start()

    def stop_all(self):
        self.network_scanner.stop_scan()
        self.port_scanner.stop_scan()
        self.ping_tool.stop()
        self.traceroute_tool.stop()

    def export_report(self, report_type: str = "network") -> Optional[str]:
        """Save current results to a txt report."""
        if report_type == "network":
            return self.report_gen.generate_network_report(
                devices=self.discovered_devices,
                scan_duration=self.state.last_scan_duration,
                subnet=get_subnet()
            )
        elif report_type == "full":
            return self.report_gen.generate_full_report(
                devices=self.discovered_devices,
                port_results=self.port_results,
                scan_duration=self.state.last_scan_duration,
                subnet=get_subnet()
            )
        return None

    def get_local_info(self) -> dict:
        local_ip = get_local_ip()
        subnet = get_subnet(local_ip)
        return {"local_ip": local_ip, "subnet": subnet}
