"""
Generates txt scan reports. Nothing fancy, just structured text output.
"""

import os
from datetime import datetime
from typing import List, Optional

from src.scanner.network_scanner import DeviceInfo
from src.scanner.port_scanner import PortResult


class ReportGenerator:

    def __init__(self, output_dir: str = "reports"):
        self.output_dir = output_dir
        os.makedirs(output_dir, exist_ok=True)

    def generate_network_report(self, devices: List[DeviceInfo],
                                 scan_duration: float = 0.0,
                                 subnet: str = "") -> str:
        """Save network scan results to a text file. Returns filepath."""
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

        lines.append(self._separator())
        lines.append("")
        lines.append("  SUMMARY")
        lines.append(f"  Active hosts: {len(devices)}")
        if devices:
            avg_latency = sum(d.response_time for d in devices) / len(devices)
            lines.append(f"  Average latency: {avg_latency:.1f}ms")
            lines.append(f"  Fastest: {min(d.response_time for d in devices):.1f}ms")
            lines.append(f"  Slowest: {max(d.response_time for d in devices):.1f}ms")
        lines.append("")
        lines.append(self._footer())

        with open(filepath, 'w') as f:
            f.write("\n".join(lines))
        return filepath

    def generate_port_report(self, target_ip: str,
                              ports: List[PortResult],
                              scan_duration: float = 0.0) -> str:
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
                if port.banner:
                    lines.append(f"  {'':10}Banner: {port.banner[:60]}")

            lines.append("  " + "-" * 60)
        else:
            lines.append("  No open ports detected.")

        lines.append("")
        lines.append(self._footer())

        with open(filepath, 'w') as f:
            f.write("\n".join(lines))
        return filepath

    def generate_full_report(self, devices: List[DeviceInfo],
                              port_results: dict = None,
                              scan_duration: float = 0.0,
                              subnet: str = "") -> str:
        """Combined network + port scan report."""
        timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
        filename = f"full_report_{timestamp}.txt"
        filepath = os.path.join(self.output_dir, filename)

        lines = []
        lines.append(self._header("FULL SCAN REPORT"))
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

        with open(filepath, 'w') as f:
            f.write("\n".join(lines))
        return filepath

    def _header(self, title: str) -> str:
        border = "=" * 74
        return f"\n  {border}\n  {title:^74}\n  Network Scanner Tool\n  {border}\n"

    def _footer(self) -> str:
        return f"  {'─' * 74}\n  Generated by Network Scanner Tool\n"

    def _separator(self) -> str:
        return "  " + "─" * 74

    def _ip_sort_key(self, ip: str):
        parts = ip.split('.')
        return tuple(int(p) for p in parts)
