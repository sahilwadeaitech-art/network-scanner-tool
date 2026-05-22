"""
Network discovery - finds active hosts on a subnet via ping + TCP fallback.
"""

import socket
import subprocess
import platform
import time
import threading
from concurrent.futures import ThreadPoolExecutor, as_completed
from dataclasses import dataclass, field
from typing import List, Optional, Callable

from src.utils.network_utils import (
    get_local_ip, get_subnet, get_ip_range,
    resolve_hostname, get_mac_address
)
from src.utils.constants import SCAN_TIMEOUT, MAX_THREADS, STATUS_ONLINE, STATUS_OFFLINE


@dataclass
class DeviceInfo:
    """Single discovered device on the network."""
    ip_address: str
    hostname: Optional[str] = None
    mac_address: Optional[str] = None
    status: str = STATUS_OFFLINE
    response_time: float = 0.0
    open_ports: List[int] = field(default_factory=list)
    vendor: Optional[str] = None
    last_seen: Optional[float] = None

    def to_dict(self):
        return {
            "ip": self.ip_address,
            "hostname": self.hostname or "Unknown",
            "mac": self.mac_address or "N/A",
            "status": self.status,
            "response_time": round(self.response_time, 2),
            "open_ports": self.open_ports,
            "last_seen": self.last_seen,
        }


class NetworkScanner:
    """Scans a subnet for live hosts using ping + TCP connect fallback."""

    def __init__(self):
        self.devices: List[DeviceInfo] = []
        self.is_scanning = False
        self.scan_progress = 0.0
        self.total_hosts = 0
        self.scanned_hosts = 0
        self._lock = threading.Lock()
        self._stop_event = threading.Event()

    def scan_network(self, target_subnet=None, callback: Optional[Callable] = None,
                     progress_callback: Optional[Callable] = None):
        """
        Scan the given subnet (or auto-detect local one).
        callback gets called with each DeviceInfo as it's found.
        """
        self.is_scanning = True
        self.devices = []
        self.scan_progress = 0.0
        self.scanned_hosts = 0
        self._stop_event.clear()

        if target_subnet is None:
            target_subnet = get_subnet()

        ip_list = get_ip_range(target_subnet)
        self.total_hosts = len(ip_list)

        if self.total_hosts == 0:
            self.is_scanning = False
            return []

        with ThreadPoolExecutor(max_workers=min(MAX_THREADS, self.total_hosts)) as executor:
            futures = {}
            for ip in ip_list:
                if self._stop_event.is_set():
                    break
                future = executor.submit(self._probe_host, ip)
                futures[future] = ip

            for future in as_completed(futures):
                if self._stop_event.is_set():
                    break

                device = future.result()
                with self._lock:
                    self.scanned_hosts += 1
                    self.scan_progress = self.scanned_hosts / self.total_hosts

                if progress_callback:
                    progress_callback(self.scanned_hosts, self.total_hosts)

                if device and device.status == STATUS_ONLINE:
                    with self._lock:
                        self.devices.append(device)
                    if callback:
                        callback(device)

        self.is_scanning = False
        return self.devices

    def _probe_host(self, ip_address):
        """Check if host is up. Try ping first, fall back to TCP."""
        if self._stop_event.is_set():
            return None

        start_time = time.time()
        is_alive = self._ping_host(ip_address)
        response_time = (time.time() - start_time) * 1000

        if not is_alive:
            # some hosts block ICMP, try common TCP ports
            is_alive = self._tcp_probe(ip_address, [80, 443, 22, 445])
            if is_alive:
                response_time = (time.time() - start_time) * 1000

        if is_alive:
            device = DeviceInfo(
                ip_address=ip_address,
                status=STATUS_ONLINE,
                response_time=response_time,
                last_seen=time.time()
            )
            device.hostname = resolve_hostname(ip_address)
            device.mac_address = get_mac_address(ip_address)
            return device

        return None

    def _ping_host(self, ip_address):
        """Send a single ICMP ping."""
        try:
            system = platform.system().lower()
            if system == "windows":
                cmd = ["ping", "-n", "1", "-w", str(int(SCAN_TIMEOUT * 1000)), ip_address]
            else:
                cmd = ["ping", "-c", "1", "-W", str(int(SCAN_TIMEOUT)), ip_address]

            result = subprocess.run(
                cmd,
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL,
                timeout=SCAN_TIMEOUT + 1
            )
            return result.returncode == 0
        except (subprocess.TimeoutExpired, Exception):
            return False

    def _tcp_probe(self, ip_address, ports):
        """Try TCP connect on a few common ports as ICMP fallback."""
        for port in ports:
            try:
                sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                sock.settimeout(0.5)
                result = sock.connect_ex((ip_address, port))
                sock.close()
                if result == 0:
                    return True
            except (socket.error, OSError):
                continue
        return False

    def stop_scan(self):
        self._stop_event.set()
        self.is_scanning = False

    def get_scan_results(self):
        with self._lock:
            return list(self.devices)

    def get_progress(self):
        return self.scan_progress
