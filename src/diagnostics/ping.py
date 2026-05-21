"""
Ping Diagnostic Tool
Performs ICMP echo requests with detailed statistics reporting.
Supports continuous ping and single-shot modes.
"""

import subprocess
import platform
import re
import time
from dataclasses import dataclass
from typing import List, Optional, Callable


@dataclass
class PingResult:
    """Single ping response data."""
    sequence: int
    response_time: float  # milliseconds
    ttl: int = 0
    success: bool = True
    error: Optional[str] = None


@dataclass
class PingStats:
    """Aggregate statistics for a ping session."""
    target: str
    resolved_ip: Optional[str] = None
    packets_sent: int = 0
    packets_received: int = 0
    packet_loss: float = 0.0
    min_time: float = 0.0
    avg_time: float = 0.0
    max_time: float = 0.0
    results: List[PingResult] = None

    def __post_init__(self):
        if self.results is None:
            self.results = []

    @property
    def loss_percentage(self):
        if self.packets_sent == 0:
            return 0.0
        return ((self.packets_sent - self.packets_received) / self.packets_sent) * 100

    def to_dict(self):
        return {
            "target": self.target,
            "resolved_ip": self.resolved_ip,
            "packets_sent": self.packets_sent,
            "packets_received": self.packets_received,
            "packet_loss": round(self.loss_percentage, 1),
            "min_ms": round(self.min_time, 2),
            "avg_ms": round(self.avg_time, 2),
            "max_ms": round(self.max_time, 2),
        }


class PingTool:
    """
    Wrapper around system ping with parsed results.
    Provides structured output for the UI.
    """

    def __init__(self):
        self.is_running = False
        self._system = platform.system().lower()

    def ping(self, target: str, count: int = 4, timeout: float = 2.0,
             callback: Optional[Callable] = None) -> PingStats:
        """
        Ping a target host with the specified number of attempts.
        
        Args:
            target: Hostname or IP to ping
            count: Number of pings to send
            timeout: Timeout per request in seconds
            callback: Called with each PingResult as it comes in
        """
        self.is_running = True
        stats = PingStats(target=target)

        try:
            cmd = self._build_command(target, count, timeout)
            process = subprocess.Popen(
                cmd,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True
            )

            sequence = 0
            for line in iter(process.stdout.readline, ''):
                if not self.is_running:
                    process.terminate()
                    break

                line = line.strip()
                if not line:
                    continue

                # Try to extract response time from the line
                result = self._parse_ping_line(line, sequence)
                if result:
                    sequence += 1
                    stats.results.append(result)
                    stats.packets_sent += 1
                    if result.success:
                        stats.packets_received += 1
                    if callback:
                        callback(result)

                # Check if we can extract the resolved IP
                if stats.resolved_ip is None:
                    ip_match = re.search(r'\(?([\d.]+)\)?', line)
                    if ip_match and target != ip_match.group(1):
                        stats.resolved_ip = ip_match.group(1)

            process.wait(timeout=5)

            # If we didn't capture individual results, parse the full output
            if not stats.results:
                stderr_output = process.stderr.read()
                if "could not find host" in stderr_output.lower() or \
                   "unknown host" in stderr_output.lower():
                    stats.packets_sent = count
                    stats.packets_received = 0

        except subprocess.TimeoutExpired:
            pass
        except FileNotFoundError:
            stats.results.append(PingResult(0, 0, success=False, error="Ping command not found"))
        except Exception as e:
            stats.results.append(PingResult(0, 0, success=False, error=str(e)))

        # Calculate statistics
        self._calculate_stats(stats)
        self.is_running = False
        return stats

    def _build_command(self, target: str, count: int, timeout: float) -> list:
        """Build the platform-appropriate ping command."""
        if self._system == "windows":
            return ["ping", "-n", str(count), "-w", str(int(timeout * 1000)), target]
        else:
            return ["ping", "-c", str(count), "-W", str(int(timeout)), target]

    def _parse_ping_line(self, line: str, sequence: int) -> Optional[PingResult]:
        """Parse a single line of ping output for timing data."""
        # Match typical ping response patterns
        # Linux: 64 bytes from 192.168.1.1: icmp_seq=1 ttl=64 time=2.34 ms
        # Windows: Reply from 192.168.1.1: bytes=32 time=2ms TTL=64
        time_match = re.search(r'time[=<](\d+\.?\d*)\s*ms', line, re.I)
        ttl_match = re.search(r'ttl[=](\d+)', line, re.I)

        if time_match:
            response_time = float(time_match.group(1))
            ttl = int(ttl_match.group(1)) if ttl_match else 0
            return PingResult(sequence=sequence, response_time=response_time, ttl=ttl)

        # Check for timeout or unreachable
        if "timed out" in line.lower() or "unreachable" in line.lower():
            return PingResult(sequence=sequence, response_time=0, success=False,
                           error="Request timed out")

        return None

    def _calculate_stats(self, stats: PingStats):
        """Calculate min/avg/max from individual results."""
        successful = [r for r in stats.results if r.success]
        if successful:
            times = [r.response_time for r in successful]
            stats.min_time = min(times)
            stats.max_time = max(times)
            stats.avg_time = sum(times) / len(times)

        # Ensure packet counts are correct
        if stats.packets_sent == 0:
            stats.packets_sent = len(stats.results)
            stats.packets_received = len(successful)

    def stop(self):
        """Stop an ongoing ping operation."""
        self.is_running = False
