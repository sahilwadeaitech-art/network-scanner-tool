"""
TCP port scanner with service detection and basic banner grabbing.
"""

import socket
import time
import threading
from concurrent.futures import ThreadPoolExecutor, as_completed
from dataclasses import dataclass
from typing import List, Optional, Callable, Tuple

from src.utils.constants import COMMON_PORTS, SCAN_TIMEOUT, MAX_THREADS, QUICK_SCAN_PORTS


@dataclass
class PortResult:
    """Result from scanning a single port."""
    port: int
    state: str  # open, closed, filtered
    service: str = "unknown"
    banner: Optional[str] = None
    response_time: float = 0.0

    def to_dict(self):
        return {
            "port": self.port,
            "state": self.state,
            "service": self.service,
            "banner": self.banner,
            "response_time": round(self.response_time, 2),
        }


class PortScanner:
    """TCP connect() scanner. Checks ports concurrently with thread pool."""

    def __init__(self):
        self.results: List[PortResult] = []
        self.is_scanning = False
        self.scan_progress = 0.0
        self.total_ports = 0
        self.scanned_ports = 0
        self._lock = threading.Lock()
        self._stop_event = threading.Event()

    def scan_ports(self, target_ip: str, ports: Optional[List[int]] = None,
                   port_range: Optional[Tuple[int, int]] = None,
                   callback: Optional[Callable] = None,
                   progress_callback: Optional[Callable] = None) -> List[PortResult]:
        """
        Scan ports on target. Pass either a list of ports or a (start, end) range.
        Defaults to QUICK_SCAN_PORTS if neither specified.
        """
        self.is_scanning = True
        self.results = []
        self.scanned_ports = 0
        self._stop_event.clear()

        if port_range:
            port_list = list(range(port_range[0], port_range[1] + 1))
        elif ports:
            port_list = ports
        else:
            port_list = QUICK_SCAN_PORTS

        self.total_ports = len(port_list)

        thread_count = min(MAX_THREADS, self.total_ports)
        with ThreadPoolExecutor(max_workers=thread_count) as executor:
            futures = {}
            for port in port_list:
                if self._stop_event.is_set():
                    break
                future = executor.submit(self._check_port, target_ip, port)
                futures[future] = port

            for future in as_completed(futures):
                if self._stop_event.is_set():
                    break

                result = future.result()
                with self._lock:
                    self.scanned_ports += 1
                    self.scan_progress = self.scanned_ports / self.total_ports

                if progress_callback:
                    progress_callback(self.scanned_ports, self.total_ports)

                if result and result.state == "open":
                    with self._lock:
                        self.results.append(result)
                    if callback:
                        callback(result)

        self.is_scanning = False
        self.results.sort(key=lambda r: r.port)
        return self.results

    def quick_scan(self, target_ip: str, callback=None, progress_callback=None):
        """Scan just the common ports."""
        return self.scan_ports(target_ip, ports=QUICK_SCAN_PORTS,
                              callback=callback, progress_callback=progress_callback)

    def full_scan(self, target_ip: str, callback=None, progress_callback=None):
        """Scan 1-1024."""
        return self.scan_ports(target_ip, port_range=(1, 1024),
                              callback=callback, progress_callback=progress_callback)

    def _check_port(self, ip: str, port: int) -> Optional[PortResult]:
        """Try to connect to a single port."""
        if self._stop_event.is_set():
            return None

        start_time = time.time()
        try:
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.settimeout(SCAN_TIMEOUT)
            result = sock.connect_ex((ip, port))
            response_time = (time.time() - start_time) * 1000

            if result == 0:
                service = self._identify_service(port)
                banner = self._grab_banner(sock, ip, port)
                sock.close()
                return PortResult(
                    port=port, state="open", service=service,
                    banner=banner, response_time=response_time
                )
            else:
                sock.close()
                return PortResult(port=port, state="closed", response_time=response_time)

        except socket.timeout:
            return PortResult(port=port, state="filtered")
        except (socket.error, OSError):
            return None

    def _identify_service(self, port: int) -> str:
        """Look up service name for a port."""
        if port in COMMON_PORTS:
            return COMMON_PORTS[port]
        try:
            return socket.getservbyport(port, 'tcp')
        except (OSError, socket.error):
            return "unknown"

    def _grab_banner(self, sock, ip: str, port: int) -> Optional[str]:
        """Try to read a banner from the open port."""
        try:
            sock.settimeout(1.0)
            banner = sock.recv(1024)
            if banner:
                return banner.decode('utf-8', errors='ignore').strip()[:200]
        except (socket.timeout, socket.error, UnicodeDecodeError):
            pass

        # for HTTP ports, send a HEAD request
        if port in (80, 8080, 8443, 8888):
            try:
                probe_sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                probe_sock.settimeout(1.0)
                probe_sock.connect((ip, port))
                probe_sock.send(b"HEAD / HTTP/1.0\r\n\r\n")
                response = probe_sock.recv(512)
                probe_sock.close()
                if response:
                    first_line = response.decode('utf-8', errors='ignore').split('\n')[0]
                    return first_line.strip()[:200]
            except (socket.error, OSError):
                pass

        return None

    def stop_scan(self):
        self._stop_event.set()
        self.is_scanning = False

    def get_open_ports(self) -> List[PortResult]:
        with self._lock:
            return [r for r in self.results if r.state == "open"]

    def get_progress(self) -> float:
        return self.scan_progress
