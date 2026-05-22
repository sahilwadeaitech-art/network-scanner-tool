"""
App-wide constants and config.
"""

APP_VERSION = "1.2.0"
APP_NAME = "Network Scanner Tool"
AUTHOR = "Sahil Wade"

# scan settings
SCAN_TIMEOUT = 1.5  # seconds per host/port
MAX_THREADS = 100

# well-known ports we check during quick scans
COMMON_PORTS = {
    20: "FTP-Data",
    21: "FTP",
    22: "SSH",
    23: "Telnet",
    25: "SMTP",
    53: "DNS",
    67: "DHCP-S",
    68: "DHCP-C",
    69: "TFTP",
    80: "HTTP",
    110: "POP3",
    135: "RPC",
    139: "NetBIOS",
    143: "IMAP",
    161: "SNMP",
    162: "SNMP-Trap",
    389: "LDAP",
    443: "HTTPS",
    445: "SMB",
    465: "SMTPS",
    514: "Syslog",
    587: "SMTP-Sub",
    636: "LDAPS",
    993: "IMAPS",
    995: "POP3S",
    1080: "SOCKS",
    1433: "MSSQL",
    3128: "Proxy",
    3306: "MySQL",
    3389: "RDP",
    5060: "SIP",
    5432: "PostgreSQL",
    5900: "VNC",
    6379: "Redis",
    8080: "HTTP-Alt",
    8443: "HTTPS-Alt",
    8888: "Alt-HTTP",
    27017: "MongoDB",
}

# subset for quick scans (the most common stuff)
QUICK_SCAN_PORTS = [21, 22, 23, 25, 53, 80, 110, 135, 139, 143, 443, 445, 3306, 3389, 5432, 8080]
FULL_SCAN_RANGE = (1, 1024)

STATUS_ONLINE = "Online"
STATUS_OFFLINE = "Offline"
STATUS_UNKNOWN = "Unknown"

# color palette for the UI
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
