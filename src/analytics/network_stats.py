"""
Stats calculations for the dashboard. Takes scan results and produces
metrics, distributions, and health scores.
"""

import time
from typing import List, Dict, Optional
from dataclasses import dataclass, field
from collections import Counter

from src.scanner.network_scanner import DeviceInfo
from src.scanner.port_scanner import PortResult


@dataclass
class ScanSummary:
    total_hosts_scanned: int = 0
    active_hosts: int = 0
    inactive_hosts: int = 0
    avg_response_time: float = 0.0
    min_response_time: float = 0.0
    max_response_time: float = 0.0
    scan_duration: float = 0.0
    total_open_ports: int = 0
    timestamp: float = field(default_factory=time.time)

    def to_dict(self):
        return {
            "total_scanned": self.total_hosts_scanned,
            "active": self.active_hosts,
            "inactive": self.inactive_hosts,
            "avg_latency": round(self.avg_response_time, 2),
            "min_latency": round(self.min_response_time, 2),
            "max_latency": round(self.max_response_time, 2),
            "duration": round(self.scan_duration, 2),
            "open_ports": self.total_open_ports,
        }


class NetworkStats:
    """Computes stats from scan data for the dashboard."""

    def __init__(self):
        self.scan_history: List[ScanSummary] = []
        self._current_devices: List[DeviceInfo] = []
        self._port_data: Dict[str, List[PortResult]] = {}

    def update_devices(self, devices: List[DeviceInfo]):
        self._current_devices = devices

    def update_ports(self, ip: str, ports: List[PortResult]):
        self._port_data[ip] = ports

    def get_summary(self, scan_duration: float = 0.0, total_scanned: int = 0) -> ScanSummary:
        """Build summary after a scan finishes."""
        devices = self._current_devices
        summary = ScanSummary()

        summary.active_hosts = len(devices)
        summary.total_hosts_scanned = total_scanned or len(devices)
        summary.inactive_hosts = summary.total_hosts_scanned - summary.active_hosts
        summary.scan_duration = scan_duration

        if devices:
            response_times = [d.response_time for d in devices if d.response_time > 0]
            if response_times:
                summary.avg_response_time = sum(response_times) / len(response_times)
                summary.min_response_time = min(response_times)
                summary.max_response_time = max(response_times)

        summary.total_open_ports = sum(len(ports) for ports in self._port_data.values())

        self.scan_history.append(summary)
        if len(self.scan_history) > 20:
            self.scan_history = self.scan_history[-20:]

        return summary

    def get_latency_distribution(self) -> Dict[str, int]:
        """Bucket devices by response time for histogram."""
        buckets = {"< 1ms": 0, "1-5ms": 0, "5-20ms": 0,
                   "20-100ms": 0, "100-500ms": 0, "> 500ms": 0}

        for device in self._current_devices:
            rt = device.response_time
            if rt < 1:
                buckets["< 1ms"] += 1
            elif rt < 5:
                buckets["1-5ms"] += 1
            elif rt < 20:
                buckets["5-20ms"] += 1
            elif rt < 100:
                buckets["20-100ms"] += 1
            elif rt < 500:
                buckets["100-500ms"] += 1
            else:
                buckets["> 500ms"] += 1
        return buckets

    def get_port_service_breakdown(self) -> Dict[str, int]:
        """Count service types found across all hosts."""
        service_counter = Counter()
        for ip, ports in self._port_data.items():
            for port_result in ports:
                if port_result.state == "open":
                    service_counter[port_result.service] += 1
        return dict(service_counter.most_common(15))

    def get_device_response_data(self) -> List[Dict]:
        """Response time per device, sorted."""
        data = []
        for device in sorted(self._current_devices, key=lambda d: d.response_time):
            data.append({
                "ip": device.ip_address,
                "hostname": device.hostname or device.ip_address,
                "latency": round(device.response_time, 2),
                "status": device.status,
            })
        return data

    def get_network_health_score(self) -> float:
        """Simple 0-100 health score based on latency + responsiveness."""
        if not self._current_devices:
            return 0.0

        total = len(self._current_devices)
        low_latency = sum(1 for d in self._current_devices if d.response_time < 50)
        responsive = sum(1 for d in self._current_devices if d.response_time > 0)

        latency_score = (low_latency / total) * 40 if total > 0 else 0
        response_score = (responsive / total) * 40 if total > 0 else 0
        discovery_score = min(total / 10, 1.0) * 20

        return min(latency_score + response_score + discovery_score, 100.0)

    def get_scan_trend(self) -> List[Dict]:
        """Historical data for trend chart."""
        return [
            {
                "timestamp": s.timestamp,
                "active_hosts": s.active_hosts,
                "avg_latency": s.avg_response_time,
                "duration": s.scan_duration,
            }
            for s in self.scan_history
        ]

    def get_dashboard_stats(self) -> Dict:
        """All the numbers the dashboard cards need."""
        devices = self._current_devices
        total_ports = sum(len(p) for p in self._port_data.values())

        stats = {
            "active_devices": len(devices),
            "total_open_ports": total_ports,
            "health_score": round(self.get_network_health_score(), 1),
            "avg_latency": 0.0,
            "fastest_host": None,
            "slowest_host": None,
        }

        if devices:
            response_times = [d.response_time for d in devices if d.response_time > 0]
            if response_times:
                stats["avg_latency"] = round(sum(response_times) / len(response_times), 1)

            fastest = min(devices, key=lambda d: d.response_time if d.response_time > 0 else float('inf'))
            slowest = max(devices, key=lambda d: d.response_time)
            stats["fastest_host"] = fastest.ip_address
            stats["slowest_host"] = slowest.ip_address

        return stats
