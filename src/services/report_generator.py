"""
Report Generator
Creates scan reports in TXT format with structured output.
Handles formatting and file export for scan results.
"""

import os
import time
from datetime import datetime
from typing import List, Optional

from src.scanner.network_scanner import DeviceInfo
from src.scanner.port_scanner import PortResult


class ReportGenerator:
    """
    Generates diagnostic reports from scan data.
    Supports text-based reports with clean formatting.
    """

    def __init__(self, output_dir: str = "reports"):
        self.output_dir = output_dir
        os.makedirs(output_dir, exist_ok=True)

    def generate_network_report(self, devices: List[DeviceInfo],
                                 scan_duration: float = 0.0,
                                 subnet: str = "") -> str:
        """
        Generate a network discovery report.
        Returns the file path of the saved report.
        """
        timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
        filename = f"network_scan_{timestamp}.txt"
        filepath = os.path.join(self.output_dir, filename)

        lines = []
        lines.append(self._header("NETWORK DISCOVERY REPORT"))
        lines.append(f"  Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        lines.append(f"  Target:    {subnet}")
        lines.append(f"  Duration:  {scan_duration:.2f}s")
        lines.append(f"  Devices:   {len(devices)} found")
        lines.append("")
        lines.append(self._separator())
        lines.append("")

        if devices:
            # Summary table
            lines.append("  DISCOVERED DEVICES")
            lines.append("  " + "-" * 70)
            lines.append(f"  {'IP Address':<18}{'Hostname':<25}{'MAC Address':<20}{'Latency':<10}")
            lines.append("  " + "-" * 70)

            for device in sorted(devices, key=lambda d: self._ip_sort_key(d.ip_address)):
                hostname = (device.hostname or "Unknown")[:24]
                mac = device.mac_address or "N/A"
                latency = f"{device.response_time:.1f}ms"
                lines.append(f"  {device.ip_address:<18}{hostname:<25}{mac:<20}{latency:<10}")

            lines.append("  " + "-" * 70)
            lines.append("")
        else:
            lines.append("  No devices discovered.")
            lines.append("")

        # Network summary
        lines.append(self._separator())
        lines.append("")
        lines.append("  SCAN SUMMARY")
        lines.append(f"  • Active hosts: {len(devices)}")
        if devices:
            avg_latency = sum(d.response_time for d in devices) / len(devices)
            lines.append(f"  • Average latency: {avg_latency:.1f}ms")
            lines.append(f"  • Fastest response: {min(d.response_time for d in devices):.1f}ms")
            lines.append(f"  • Slowest response: {max(d.response_time for d in devices):.1f}ms")
        lines.append("")
        lines.append(self._footer())

        content = "\n".join(lines)
        with open(filepath, 'w') as f:
            f.write(content)

        return filepath

    def generate_port_report(self, target_ip: str,
                              ports: List[PortResult],
                              scan_duration: float = 0.0) -> str:
        """
        Generate a port scan report for a specific host.
        Returns the file path of the saved report.
        """
        timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
        filename = f"port_scan_{target_ip}_{timestamp}.txt"
        filepath = os.path.join(self.output_dir, filename)

        lines = []
        lines.append(self._header("PORT SCAN REPORT"))
        lines.append(f"  Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        lines.append(f"  Target:    {target_ip}")
        lines.append(f"  Duration:  {scan_duration:.2f}s")
        lines.append(f"  Open ports: {len(ports)}")
        lines.append("")
        lines.append(self._separator())
        lines.append("")

        if ports:
            lines.append("  OPEN PORTS")
            lines.append("  " + "-" * 60)
            lines.append(f"  {'Port':<10}{'State':<12}{'Service':<18}{'Response':<12}")
            lines.append("  " + "-" * 60)

            for port in sorted(ports, key=lambda p: p.port):
                service = port.service[:17]
                response = f"{port.response_time:.1f}ms"
                lines.append(f"  {port.port:<10}{port.state:<12}{service:<18}{response:<12}")

                # Include banner info if available
                if port.banner:
                    banner_preview = port.banner[:60]
                    lines.append(f"  {'':10}Banner: {banner_preview}")

            lines.append("  " + "-" * 60)
        else:
            lines.append("  No open ports detected.")

        lines.append("")
        lines.append(self._footer())

        content = "\n".join(lines)
        with open(filepath, 'w') as f:
            f.write(content)

        return filepath

    def generate_full_report(self, devices: List[DeviceInfo],
                              port_results: dict = None,
                              scan_duration: float = 0.0,
                              subnet: str = "") -> str:
        """
        Generate a comprehensive scan report combining network and port data.
        port_results should be a dict of {ip: [PortResult, ...]}
        """
        timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
        filename = f"full_report_{timestamp}.txt"
        filepath = os.path.join(self.output_dir, filename)

        lines = []
        lines.append(self._header("FULL NETWORK SCAN REPORT"))
        lines.append(f"  Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        lines.append(f"  Subnet:    {subnet}")
        lines.append(f"  Duration:  {scan_duration:.2f}s")
        lines.append(f"  Hosts:     {len(devices)} active")
        lines.append("")
        lines.append(self._separator())

        for device in sorted(devices, key=lambda d: self._ip_sort_key(d.ip_address)):
            lines.append("")
            lines.append(f"  [{device.ip_address}]")
            lines.append(f"    Hostname: {device.hostname or 'Unknown'}")
            lines.append(f"    MAC:      {device.mac_address or 'N/A'}")
            lines.append(f"    Status:   {device.status}")
            lines.append(f"    Latency:  {device.response_time:.1f}ms")

            # Add port info if available
            if port_results and device.ip_address in port_results:
                open_ports = port_results[device.ip_address]
                if open_ports:
                    lines.append(f"    Ports:    {len(open_ports)} open")
                    for pr in sorted(open_ports, key=lambda p: p.port):
                        lines.append(f"              {pr.port}/{pr.service}")

            lines.append("")

        lines.append(self._separator())
        lines.append("")
        lines.append(self._footer())

        content = "\n".join(lines)
        with open(filepath, 'w') as f:
            f.write(content)

        return filepath

    def _header(self, title: str) -> str:
        """Generate a report header."""
        border = "=" * 74
        return f"\n  {border}\n  {title:^74}\n  Network Scanner Tool\n  {border}\n"

    def _footer(self) -> str:
        """Generate a report footer."""
        return f"  {'─' * 74}\n  Report generated by Network Scanner Tool\n  https://github.com/sahilwadeaitech-art/network-scanner-tool\n"

    def _separator(self) -> str:
        return "  " + "─" * 74

    def _ip_sort_key(self, ip: str):
        """Sort IP addresses numerically."""
        parts = ip.split('.')
        return tuple(int(p) for p in parts)
