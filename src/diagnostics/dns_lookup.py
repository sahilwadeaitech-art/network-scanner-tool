"""
DNS lookup - forward and reverse resolution with nslookup fallback.
"""

import socket
import subprocess
import platform
import re
from dataclasses import dataclass, field
from typing import List, Optional


@dataclass
class DNSRecord:
    query: str
    record_type: str
    value: str
    ttl: Optional[int] = None


@dataclass
class DNSResult:
    query: str
    resolved_ips: List[str] = field(default_factory=list)
    hostname: Optional[str] = None
    aliases: List[str] = field(default_factory=list)
    records: List[DNSRecord] = field(default_factory=list)
    nameserver: Optional[str] = None
    lookup_time: float = 0.0
    error: Optional[str] = None
    success: bool = True

    def to_dict(self):
        return {
            "query": self.query,
            "ips": self.resolved_ips,
            "hostname": self.hostname,
            "aliases": self.aliases,
            "lookup_time": round(self.lookup_time, 2),
            "error": self.error,
            "success": self.success,
        }


class DNSLookup:
    """Handles forward and reverse DNS lookups."""

    def __init__(self):
        self._system = platform.system().lower()

    def lookup(self, query: str) -> DNSResult:
        """Auto-detect whether to do forward or reverse lookup."""
        import time
        start = time.time()

        is_ip = self._is_ip_address(query)
        result = DNSResult(query=query)

        try:
            if is_ip:
                result = self._reverse_lookup(query)
            else:
                result = self._forward_lookup(query)

            # also run nslookup for extra info
            ns_data = self._nslookup(query)
            if ns_data:
                result.nameserver = ns_data.get("nameserver")
                for ip in ns_data.get("ips", []):
                    if ip not in result.resolved_ips:
                        result.resolved_ips.append(ip)

        except Exception as e:
            result.error = str(e)
            result.success = False

        result.lookup_time = (time.time() - start) * 1000
        return result

    def _forward_lookup(self, hostname: str) -> DNSResult:
        result = DNSResult(query=hostname)
        try:
            host_info = socket.gethostbyname_ex(hostname)
            result.hostname = host_info[0]
            result.aliases = host_info[1]
            result.resolved_ips = host_info[2]

            for ip in result.resolved_ips:
                result.records.append(DNSRecord(query=hostname, record_type="A", value=ip))
            for alias in result.aliases:
                result.records.append(DNSRecord(query=hostname, record_type="CNAME", value=alias))

        except socket.gaierror as e:
            result.error = f"DNS resolution failed: {e}"
            result.success = False
        except socket.herror as e:
            result.error = f"Host error: {e}"
            result.success = False
        return result

    def _reverse_lookup(self, ip_address: str) -> DNSResult:
        result = DNSResult(query=ip_address, resolved_ips=[ip_address])
        try:
            host_info = socket.gethostbyaddr(ip_address)
            result.hostname = host_info[0]
            result.aliases = host_info[1]
            result.records.append(DNSRecord(query=ip_address, record_type="PTR", value=host_info[0]))
        except socket.herror as e:
            result.error = f"Reverse lookup failed: {e}"
            result.success = False
        except socket.gaierror as e:
            result.error = f"Address error: {e}"
            result.success = False
        return result

    def _nslookup(self, query: str) -> Optional[dict]:
        """Run nslookup to get nameserver info."""
        try:
            result = subprocess.run(
                ["nslookup", query],
                capture_output=True, text=True, timeout=5
            )
            output = result.stdout
            data = {"ips": [], "nameserver": None}

            ns_match = re.search(r'Server:\s*(.+)', output)
            if ns_match:
                data["nameserver"] = ns_match.group(1).strip()

            in_answer = False
            for line in output.split('\n'):
                if 'Name:' in line or 'name =' in line.lower():
                    in_answer = True
                elif in_answer and 'Address' in line:
                    addr_match = re.search(r'Address[:\s]+(.+)', line)
                    if addr_match:
                        addr = addr_match.group(1).strip()
                        if self._is_ip_address(addr) and addr not in data["ips"]:
                            data["ips"].append(addr)
            return data

        except (subprocess.TimeoutExpired, FileNotFoundError):
            return None

    def _is_ip_address(self, string: str) -> bool:
        pattern = r'^(\d{1,3}\.){3}\d{1,3}$'
        return bool(re.match(pattern, string))

    def get_system_dns(self) -> Optional[str]:
        """Get configured DNS server."""
        try:
            result = subprocess.run(
                ["nslookup", "localhost"],
                capture_output=True, text=True, timeout=3
            )
            match = re.search(r'Server:\s*(.+)', result.stdout)
            if match:
                return match.group(1).strip()
        except (subprocess.TimeoutExpired, FileNotFoundError):
            pass
        return None
