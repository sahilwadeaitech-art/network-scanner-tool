"""
Network helper functions - IP validation, subnet math, hostname resolution, etc.
"""

import socket
import struct
import re
import psutil


def get_local_ip():
    """Get our local IP. Uses the UDP socket trick (no actual traffic sent)."""
    try:
        sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        sock.settimeout(0.1)
        sock.connect(("8.8.8.8", 80))
        local_ip = sock.getsockname()[0]
        sock.close()
        return local_ip
    except (socket.error, OSError):
        return "127.0.0.1"


def get_subnet(ip_address=None):
    """Figure out our subnet in CIDR notation from the active interface."""
    if ip_address is None:
        ip_address = get_local_ip()

    for iface_name, addrs in psutil.net_if_addrs().items():
        for addr in addrs:
            if addr.family == socket.AF_INET and addr.address == ip_address:
                netmask = addr.netmask
                if netmask:
                    ip_int = struct.unpack('!I', socket.inet_aton(ip_address))[0]
                    mask_int = struct.unpack('!I', socket.inet_aton(netmask))[0]
                    network_int = ip_int & mask_int
                    network_addr = socket.inet_ntoa(struct.pack('!I', network_int))
                    cidr = bin(mask_int).count('1')
                    return f"{network_addr}/{cidr}"

    # fallback to /24
    parts = ip_address.split('.')
    return f"{parts[0]}.{parts[1]}.{parts[2]}.0/24"


def validate_ip(ip_string):
    """Basic IPv4 validation."""
    pattern = r'^(\d{1,3}\.){3}\d{1,3}$'
    if not re.match(pattern, ip_string):
        return False
    octets = ip_string.split('.')
    return all(0 <= int(octet) <= 255 for octet in octets)


def validate_ip_range(ip_range):
    """Validate CIDR (192.168.1.0/24) or range (192.168.1.1-254) format."""
    if '/' in ip_range:
        parts = ip_range.split('/')
        if not validate_ip(parts[0]):
            return False
        try:
            cidr = int(parts[1])
            return 0 <= cidr <= 32
        except ValueError:
            return False

    if '-' in ip_range:
        base_and_range = ip_range.rsplit('-', 1)
        base_ip = base_and_range[0]

        if validate_ip(base_and_range[1]):
            return validate_ip(base_ip)

        if validate_ip(base_ip):
            try:
                end = int(base_and_range[1])
                return 0 <= end <= 255
            except ValueError:
                return False

    return validate_ip(ip_range)


def get_ip_range(subnet):
    """Generate list of host IPs from CIDR subnet string."""
    if '/' not in subnet:
        return [subnet] if validate_ip(subnet) else []

    parts = subnet.split('/')
    base_ip = parts[0]
    cidr = int(parts[1])

    ip_int = struct.unpack('!I', socket.inet_aton(base_ip))[0]
    mask_int = (0xFFFFFFFF << (32 - cidr)) & 0xFFFFFFFF
    network_int = ip_int & mask_int
    broadcast_int = network_int | (~mask_int & 0xFFFFFFFF)

    addresses = []
    for host_int in range(network_int + 1, broadcast_int):
        addresses.append(socket.inet_ntoa(struct.pack('!I', host_int)))
    return addresses


def resolve_hostname(ip_address):
    """Reverse DNS lookup. Returns None if it fails."""
    try:
        return socket.gethostbyaddr(ip_address)[0]
    except (socket.herror, socket.gaierror, socket.timeout):
        return None


def get_mac_address(ip_address):
    """Try to get MAC from the ARP table. Platform-dependent."""
    try:
        import subprocess
        import platform

        if platform.system() == "Windows":
            result = subprocess.run(
                ["arp", "-a", ip_address],
                capture_output=True, text=True, timeout=5
            )
            for line in result.stdout.split('\n'):
                if ip_address in line:
                    parts = line.split()
                    for part in parts:
                        if re.match(r'([0-9a-f]{2}[:-]){5}[0-9a-f]{2}', part, re.I):
                            return part.upper()
        else:
            result = subprocess.run(
                ["arp", "-n", ip_address],
                capture_output=True, text=True, timeout=5
            )
            for line in result.stdout.split('\n'):
                if ip_address in line:
                    match = re.search(r'([0-9a-f]{2}[:-]){5}[0-9a-f]{2}', line, re.I)
                    if match:
                        return match.group(0).upper()
    except (subprocess.TimeoutExpired, FileNotFoundError, Exception):
        pass
    return None
