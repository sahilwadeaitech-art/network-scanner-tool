"""
Scan Service - Orchestration Layer
Coordinates scanner modules and manages scan workflows.
Acts as the bridge between the UI and backend logic.
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
    """Tracks the current state of all scanning operations."""
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
    """
    Central service that manages all scanning operations.
    Handles threading, state management, and result aggregation.
    """

    def __init__(self):
        self.network_scanner = NetworkScanner()
        self.port_scanner = PortScanner()
        self.ping_tool = PingTool()
        self.dns_tool = DNSLookup()
        self.traceroute_tool = TracerouteTool()
        self.report_gen = ReportGenerator()
        self.state = ScanState()

        # Store results
        self.discovered_devices: List[DeviceInfo] = []
        self.port_results: dict = {}  # {ip: [PortResult]}
        self.last_ping: Optional[PingStats] = None
        self.last_dns: Optional[DNSResult] = None
        self.last_traceroute: Optional[TracerouteResult] = None

    def start_network_scan(self, target_subnet: Optional[str] = None,
                           on_device_found: Optional[Callable] = None,
                           on_progress: Optional[Callable] = None,
                           on_complete: Optional[Callable] = None):
        """
        Start a network discovery scan in a background thread.
        Results are available via self.discovered_devices after completion.
        """
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

        thread = threading.Thread(target=_scan_thread, daemon=True)
        thread.start()

    def start_port_scan(self, target_ip: str, ports=None, port_range=None,
                        on_port_found: Optional[Callable] = None,
                        on_progress: Optional[Callable] = None,
                        on_complete: Optional[Callable] = None):
        """
        Start a port scan on a specific host in a background thread.
        """
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
                target_ip=target_ip,
                ports=ports,
                port_range=port_range,
                callback=_on_port,
                progress_callback=_on_progress
            )

            self.port_results[target_ip] = results
            self.state.is_port_scanning = False
            duration = time.time() - start

            if on_complete:
                on_complete(results, duration)

        thread = threading.Thread(target=_scan_thread, daemon=True)
        thread.start()

    def run_ping(self, target: str, count: int = 4,
                 on_result: Optional[Callable] = None,
                 on_complete: Optional[Callable] = None):
        """Run a ping test in a background thread."""
        def _ping_thread():
            self.state.is_diagnostic_running = True
            stats = self.ping_tool.ping(target, count=count, callback=on_result)
            self.last_ping = stats
            self.state.is_diagnostic_running = False
            if on_complete:
                on_complete(stats)

        thread = threading.Thread(target=_ping_thread, daemon=True)
        thread.start()

    def run_dns_lookup(self, query: str,
                       on_complete: Optional[Callable] = None):
        """Run a DNS lookup in a background thread."""
        def _dns_thread():
            self.state.is_diagnostic_running = True
            result = self.dns_tool.lookup(query)
            self.last_dns = result
            self.state.is_diagnostic_running = False
            if on_complete:
                on_complete(result)

        thread = threading.Thread(target=_dns_thread, daemon=True)
        thread.start()

    def run_traceroute(self, target: str,
                       on_hop: Optional[Callable] = None,
                       on_complete: Optional[Callable] = None):
        """Run a traceroute in a background thread."""
        def _trace_thread():
            self.state.is_diagnostic_running = True
            result = self.traceroute_tool.trace(target, callback=on_hop)
            self.last_traceroute = result
            self.state.is_diagnostic_running = False
            if on_complete:
                on_complete(result)

        thread = threading.Thread(target=_trace_thread, daemon=True)
        thread.start()

    def stop_all(self):
        """Stop all running scans."""
        self.network_scanner.stop_scan()
        self.port_scanner.stop_scan()
        self.ping_tool.stop()
        self.traceroute_tool.stop()

    def export_report(self, report_type: str = "network") -> Optional[str]:
        """
        Export current results to a report file.
        Returns the filepath of the generated report.
        """
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
        """Get information about the local machine."""
        local_ip = get_local_ip()
        subnet = get_subnet(local_ip)
        return {
            "local_ip": local_ip,
            "subnet": subnet,
        }
