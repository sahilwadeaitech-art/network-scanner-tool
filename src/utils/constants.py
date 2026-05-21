"""
Application constants and configuration values.
Centralized here to keep things manageable as the project grows.
"""

APP_VERSION = "1.0.0"
APP_NAME = "Network Scanner Tool"
AUTHOR = "Sahil Wade"

# Default scan timeout in seconds
SCAN_TIMEOUT = 1.5

# Thread pool size for concurrent scanning
MAX_THREADS = 100

# Common ports to scan by default
# Organized by typical service categories
COMMON_PORTS = {
    # Web Services
    80: "HTTP",
    443: "HTTPS",
    8080: "HTTP-Alt",
    8443: "HTTPS-Alt",

    # File Transfer
    20: "FTP-Data",
    21: "FTP",
    22: "SSH",
    69: "TFTP",

    # Email
    25: "SMTP",
    110: "POP3",
    143: "IMAP",
    465: "SMTPS",
    587: "SMTP-Sub",
    993: "IMAPS",
    995: "POP3S",

    # Remote Access
    23: "Telnet",
    3389: "RDP",
    5900: "VNC",

    # Database
    3306: "MySQL",
    5432: "PostgreSQL",
    1433: "MSSQL",
    27017: "MongoDB",
    6379: "Redis",

    # DNS & Directory
    53: "DNS",
    389: "LDAP",
    636: "LDAPS",

    # Network Services
    67: "DHCP-S",
    68: "DHCP-C",
    161: "SNMP",
    162: "SNMP-Trap",

    # Other
    135: "RPC",
    139: "NetBIOS",
    445: "SMB",
    514: "Syslog",
    1080: "SOCKS",
    3128: "Proxy",
    5060: "SIP",
    8888: "Alt-HTTP",
}

# Port ranges for quick scan profiles
QUICK_SCAN_PORTS = [21, 22, 23, 25, 53, 80, 110, 135, 139, 143, 443, 445, 3306, 3389, 5432, 8080]
FULL_SCAN_RANGE = (1, 1024)

# Device status indicators
STATUS_ONLINE = "Online"
STATUS_OFFLINE = "Offline"
STATUS_UNKNOWN = "Unknown"

# UI Theme - Cyber Grid
THEME = {
    "bg_deep": "#020617",
    "bg_surface": "#0F172A",
    "primary": "#2563EB",
    "secondary": "#06B6D4",
    "highlight": "#14B8A6",
    "warning": "#F59E0B",
    "error": "#EF4444",
    "success": "#22C55E",
    "text": "#F8FAFC",
    "text_muted": "#94A3B8",
    "border": "#1E293B",
    "card_bg": "#1E293B",
    "hover": "#334155",
}
