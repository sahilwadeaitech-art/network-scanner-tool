"""
Network utility functions used across the application.
Handles IP validation, subnet detection, and local network info.
"""

import socket
import struct
import re
import psutil


def get_local_ip():
    """
    Get the primary local IP address of this machine.
    Uses a UDP socket trick - doesn't actually send anything.
    """
    try:
        sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        sock.settimeout(0.1)
        # Connect to an external address to determine our local IP
        sock.connect(("8.8.8.8", 80))
        local_ip = sock.getsockname()[0]
        sock.close()
        return local_ip
    except (socket.error, OSError):
        return "127.0.0.1"


def get_subnet(ip_address=None):
    """
    Determine the subnet range (CIDR notation) for the given IP.
    Returns something like '192.168.1.0/24' for typical home networks.
    """
    if ip_address is None:
        ip_address = get_local_ip()

    # Find the matching network interface
    for iface_name, addrs in psutil.net_if_addrs().items():
        for addr in addrs:
            if addr.family == socket.AF_INET and addr.address == ip_address:
                netmask = addr.netmask
                if netmask:
                    # Calculate network address from IP and netmask
                    ip_int = struct.unpack('!I', socket.inet_aton(ip_address))[0]
                    mask_int = struct.unpack('!I', socket.inet_aton(netmask))[0]
                    network_int = ip_int & mask_int

                    network_addr = socket.inet_ntoa(struct.pack('!I', network_int))
                    cidr = bin(mask_int).count('1')

                    return f"{network_addr}/{cidr}"

    # Fallback: assume /24 subnet
    parts = ip_address.split('.')
    return f"{parts[0]}.{parts[1]}.{parts[2]}.0/24"


def validate_ip(ip_string):
    """Check if a string is a valid IPv4 address."""
    pattern = r'^(\d{1,3}\.){3}\d{1,3}$'
    if not re.match(pattern, ip_string):
        return False
    octets = ip_string.split('.')
    return all(0 <= int(octet) <= 255 for octet in octets)


def validate_ip_range(ip_range):
    """
    Validate an IP range string.
    Accepts formats like: 192.168.1.1-254 or 192.168.1.0/24
    """
    # CIDR notation
    if '/' in ip_range:
        parts = ip_range.split('/')
        if not validate_ip(parts[0]):
            return False
        try:
            cidr = int(parts[1])
            return 0 <= cidr <= 32
        except ValueError:
            return False

    # Range notation (e.g., 192.168.1.1-254)
    if '-' in ip_range:
        base_and_range = ip_range.rsplit('-', 1)
        base_ip = base_and_range[0]

        # Handle full IP range like 192.168.1.1-192.168.1.254
        if validate_ip(base_and_range[1]):
            return validate_ip(base_ip)

        # Handle short range like 192.168.1.1-254
        if validate_ip(base_ip):
            try:
                end = int(base_and_range[1])
                return 0 <= end <= 255
            except ValueError:
                return False

    # Single IP
    return validate_ip(ip_range)


def get_ip_range(subnet):
    """
    Generate a list of IP addresses from a subnet string.
    Supports CIDR notation (192.168.1.0/24).
    """
    if '/' not in subnet:
        return [subnet] if validate_ip(subnet) else []

    parts = subnet.split('/')
    base_ip = parts[0]
    cidr = int(parts[1])

    ip_int = struct.unpack('!I', socket.inet_aton(base_ip))[0]
    mask_int = (0xFFFFFFFF << (32 - cidr)) & 0xFFFFFFFF
    network_int = ip_int & mask_int
    broadcast_int = network_int | (~mask_int & 0xFFFFFFFF)

    # Generate all host addresses (exclude network and broadcast)
    addresses = []
    for host_int in range(network_int + 1, broadcast_int):
        addresses.append(socket.inet_ntoa(struct.pack('!I', host_int)))

    return addresses


def resolve_hostname(ip_address):
    """Try to resolve an IP address to a hostname."""
    try:
        hostname = socket.gethostbyaddr(ip_address)[0]
        return hostname
    except (socket.herror, socket.gaierror, socket.timeout):
        return None


def get_mac_address(ip_address):
    """
    Attempt to get MAC address for an IP via ARP table.
    Falls back to scapy if available.
    """
    try:
        # Try reading from system ARP table first (faster, no privileges needed)
        import subprocess
        import platform

        if platform.system() == "Windows":
            result = subprocess.run(
                ["arp", "-a", ip_address],
                capture_output=True, text=True, timeout=5
            )
            # Parse Windows ARP output
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
