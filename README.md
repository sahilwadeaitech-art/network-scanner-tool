# Network Scanner Tool

A modern network diagnostics and scanning utility built with Python. Provides host discovery, port scanning, and quick diagnostic tools through a clean desktop interface.

![Python](https://img.shields.io/badge/Python-3.9%2B-blue)
![License](https://img.shields.io/badge/License-MIT-green)
![Platform](https://img.shields.io/badge/Platform-Windows%20%7C%20Linux%20%7C%20macOS-lightgrey)

---

## Overview

Network Scanner Tool is a lightweight desktop application for network reconnaissance and diagnostics. It combines host discovery, TCP port scanning, and common network diagnostic utilities (ping, DNS lookup, traceroute) into a single unified interface.

Built for network administrators, security enthusiasts, and developers who need quick visibility into their local network without spinning up heavy enterprise tools.

---

## Features

- **Network Discovery** — Scan your local subnet to find active devices with hostname resolution and MAC address detection
- **Port Scanner** — TCP port scanning with service identification and banner grabbing (quick scan, full range, or custom)
- **Ping Tool** — ICMP ping with packet loss statistics and round-trip time analysis
- **DNS Lookup** — Forward and reverse DNS resolution with record details
- **Traceroute** — Hop-by-hop network path mapping with latency per hop
- **Live Dashboard** — Real-time scan progress, device count, and activity logging
- **Export Reports** — Generate structured TXT reports of scan results
- **Analytics** — Network health scoring, latency distribution, and scan history

---

## Screenshots

> Screenshots will be added after initial release.

| Dashboard | Network Scan | Port Scanner | Diagnostics |
|-----------|-------------|--------------|-------------|
| *coming soon* | *coming soon* | *coming soon* | *coming soon* |

---

## Technologies Used

| Component | Technology |
|-----------|-----------|
| Language | Python 3.9+ |
| UI Framework | CustomTkinter |
| Network Scanning | socket, subprocess |
| Packet Crafting | scapy |
| System Info | psutil |
| Concurrency | threading, concurrent.futures |
| Visualization | matplotlib (optional) |

---

## Installation

### Prerequisites

- Python 3.9 or higher
- pip package manager

### Setup

```bash
# Clone the repository
git clone https://github.com/sahilwadeaitech-art/network-scanner-tool.git
cd network-scanner-tool

# Create virtual environment (recommended)
python -m venv venv
source venv/bin/activate  # Linux/macOS
# or
venv\Scripts\activate     # Windows

# Install dependencies
pip install -r requirements.txt
```

### Run

```bash
python main.py
```

> **Note:** Some features (ARP-based MAC detection, ICMP scanning) may require elevated privileges. Run with `sudo` on Linux or as Administrator on Windows for full functionality.

---

## Usage

### Network Discovery

1. Open the **Network Scan** panel from the sidebar
2. The target subnet is auto-detected from your active interface
3. Click **Scan Network** to begin host discovery
4. Discovered devices appear in real-time with IP, hostname, and latency

### Port Scanning

1. Navigate to the **Port Scanner** panel
2. Enter a target IP address
3. Select scan mode:
   - **Quick** — Common ports only (fast)
   - **Full** — Ports 1-1024
   - **Custom** — Specify your own range
4. Open ports are listed with service names and response times

### Diagnostics

1. Open the **Diagnostics** panel
2. Choose a tool tab (Ping, DNS Lookup, or Traceroute)
3. Enter the target and run the diagnostic
4. Results are displayed in a structured log format

---

## Project Structure

```
network-scanner-tool/
├── main.py                  # Application entry point
├── requirements.txt         # Python dependencies
├── LICENSE
│
├── src/
│   ├── ui/                  # UI panels and components
│   │   ├── app.py           # Main application window
│   │   ├── theme.py         # Cyber Grid theme system
│   │   ├── components.py    # Reusable UI widgets
│   │   ├── dashboard_panel.py
│   │   ├── scanner_panel.py
│   │   ├── port_panel.py
│   │   └── diagnostics_panel.py
│   │
│   ├── scanner/             # Core scanning logic
│   │   ├── network_scanner.py   # Host discovery (ping + TCP probe)
│   │   └── port_scanner.py      # TCP port scanning
│   │
│   ├── diagnostics/         # Diagnostic tools
│   │   ├── ping.py
│   │   ├── dns_lookup.py
│   │   └── traceroute.py
│   │
│   ├── analytics/           # Data processing and stats
│   │   └── network_stats.py
│   │
│   ├── services/            # Orchestration layer
│   │   ├── scan_service.py
│   │   └── report_generator.py
│   │
│   └── utils/               # Shared utilities
│       ├── constants.py
│       └── network_utils.py
│
├── reports/                 # Generated scan reports
├── assets/                  # Icons, themes, screenshots
└── docs/                    # Documentation
```

---

## Building Executable

To create a standalone executable using PyInstaller:

```bash
pip install pyinstaller

# Build single-file executable
pyinstaller --onefile --windowed --name "NetworkScanner" main.py

# Output will be in dist/NetworkScanner.exe (Windows)
```

---

## Future Improvements

- [ ] Advanced network topology visualization
- [ ] Vulnerability scanning (CVE lookup for detected services)
- [ ] Live packet analytics and traffic monitoring
- [ ] AI-based anomaly detection for unusual network activity
- [ ] Remote monitoring with web dashboard
- [ ] Network heatmap visualization
- [ ] SNMP device querying
- [ ] Scheduled automated scans
- [ ] PDF report generation with charts

---

## Contributing

Contributions are welcome. Please open an issue first to discuss proposed changes.

---

## License

This project is licensed under the MIT License. See [LICENSE](LICENSE) for details.

---

Built by **Sahil Wade**
