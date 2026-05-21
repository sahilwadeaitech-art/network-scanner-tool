"""
Traceroute Diagnostic Tool
Maps the network path between the local machine and a target host.
Provides hop-by-hop latency and routing information.
"""

import subprocess
import platform
import re
import time
from dataclasses import dataclass, field
from typing import List, Optional, Callable


@dataclass
class TracerouteHop:
    """Represents a single hop in the route."""
    hop_number: int
    ip_address: Optional[str] = None
    hostname: Optional[str] = None
    rtt_times: List[float] = field(default_factory=list)  # milliseconds
    is_timeout: bool = False

    @property
    def avg_rtt(self) -> float:
        if not self.rtt_times:
            return 0.0
        return sum(self.rtt_times) / len(self.rtt_times)

    def to_dict(self):
        return {
            "hop": self.hop_number,
            "ip": self.ip_address or "*",
            "hostname": self.hostname or "",
            "rtt_ms": [round(t, 2) for t in self.rtt_times],
            "avg_rtt": round(self.avg_rtt, 2),
            "timeout": self.is_timeout,
        }


@dataclass
class TracerouteResult:
    """Complete traceroute result."""
    target: str
    resolved_ip: Optional[str] = None
    hops: List[TracerouteHop] = field(default_factory=list)
    total_time: float = 0.0
    completed: bool = False
    error: Optional[str] = None

    def to_dict(self):
        return {
            "target": self.target,
            "resolved_ip": self.resolved_ip,
            "hops": [h.to_dict() for h in self.hops],
            "total_time": round(self.total_time, 2),
            "completed": self.completed,
            "error": self.error,
        }


class TracerouteTool:
    """
    Network path tracer.
    Uses system traceroute/tracert to map the route to a target.
    """

    def __init__(self):
        self.is_running = False
        self._system = platform.system().lower()

    def trace(self, target: str, max_hops: int = 30,
              timeout: float = 3.0,
              callback: Optional[Callable] = None) -> TracerouteResult:
        """
        Run a traceroute to the specified target.
        
        Args:
            target: Hostname or IP to trace
            max_hops: Maximum number of hops
            timeout: Timeout per hop in seconds
            callback: Called with each TracerouteHop as it's discovered
        """
        self.is_running = True
        result = TracerouteResult(target=target)
        start_time = time.time()

        try:
            cmd = self._build_command(target, max_hops, timeout)
            process = subprocess.Popen(
                cmd,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True
            )

            for line in iter(process.stdout.readline, ''):
                if not self.is_running:
                    process.terminate()
                    break

                line = line.strip()
                if not line:
                    continue

                # Try to extract resolved IP from the first line
                if result.resolved_ip is None:
                    ip_match = re.search(r'\[([\d.]+)\]|to\s+([\d.]+)', line)
                    if ip_match:
                        result.resolved_ip = ip_match.group(1) or ip_match.group(2)

                # Parse hop data
                hop = self._parse_hop_line(line)
                if hop:
                    result.hops.append(hop)
                    if callback:
                        callback(hop)

                    # Check if we've reached the destination
                    if hop.ip_address and result.resolved_ip:
                        if hop.ip_address == result.resolved_ip:
                            result.completed = True

            process.wait(timeout=max_hops * timeout)
            
            # If we got hops but didn't detect completion, check the last hop
            if result.hops and not result.completed:
                last_hop = result.hops[-1]
                if last_hop.ip_address == result.resolved_ip:
                    result.completed = True

        except subprocess.TimeoutExpired:
            result.error = "Traceroute timed out"
        except FileNotFoundError:
            result.error = "Traceroute command not available"
        except Exception as e:
            result.error = str(e)

        result.total_time = (time.time() - start_time) * 1000
        self.is_running = False
        return result

    def _build_command(self, target: str, max_hops: int, timeout: float) -> list:
        """Build the platform-specific traceroute command."""
        if self._system == "windows":
            return ["tracert", "-d", "-h", str(max_hops), "-w", str(int(timeout * 1000)), target]
        else:
            return ["traceroute", "-n", "-m", str(max_hops), "-w", str(int(timeout)), target]

    def _parse_hop_line(self, line: str) -> Optional[TracerouteHop]:
        """
        Parse a traceroute output line into a TracerouteHop.
        Handles both Linux and Windows output formats.
        """
        # Match hop number at the start of line
        hop_match = re.match(r'\s*(\d+)\s+', line)
        if not hop_match:
            return None

        hop_number = int(hop_match.group(1))
        remaining = line[hop_match.end():]

        # Check for timeout line (all asterisks)
        if re.match(r'^[\s*]+$', remaining) or '* * *' in remaining:
            return TracerouteHop(hop_number=hop_number, is_timeout=True)

        hop = TracerouteHop(hop_number=hop_number)

        # Extract IP address
        ip_match = re.search(r'(\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3})', remaining)
        if ip_match:
            hop.ip_address = ip_match.group(1)

        # Extract hostname (if different from IP)
        # Format: hostname (ip) or just ip
        host_match = re.search(r'(\S+)\s+\([\d.]+\)', remaining)
        if host_match and host_match.group(1) != hop.ip_address:
            hop.hostname = host_match.group(1)

        # Extract round-trip times
        rtt_matches = re.findall(r'([\d.]+)\s*ms', remaining)
        hop.rtt_times = [float(t) for t in rtt_matches]

        # If we found timing data but no IP, it's still a valid hop
        if hop.rtt_times or hop.ip_address:
            return hop

        return None

    def stop(self):
        """Stop the traceroute operation."""
        self.is_running = False
