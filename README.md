# Network Scanner Tool

A desktop network scanner and diagnostics tool. Scans local networks for active devices, checks open ports, and runs basic diagnostics (ping, DNS, traceroute) — all from one interface.

Built with Python and CustomTkinter. Dark theme UI.

## What it does

- **Network discovery** — finds active devices on your subnet (IP, hostname, MAC, response time)
- **Port scanning** — TCP connect scan with service detection and banner grabbing
- **Ping** — parsed ping output with min/avg/max stats
- **DNS lookup** — forward and reverse resolution
- **Traceroute** — hop-by-hop path with latency
- **Report export** — saves scan results to structured .txt files

## Screenshots

*Coming soon — need to take some clean ones on Windows*

## Setup

```bash
git clone https://github.com/sahilwadeaitech-art/network-scanner-tool.git
cd network-scanner-tool

python -m venv venv
source venv/bin/activate   # or venv\Scripts\activate on Windows

pip install -r requirements.txt
python main.py
```

Needs Python 3.9+. Some features (like ARP MAC detection) need admin/root.

## How to use

The sidebar has four panels:

1. **Dashboard** — overview with quick actions and activity log
2. **Network Scan** — auto-detects your subnet, scans for hosts
3. **Port Scanner** — enter an IP, pick quick/full/custom range
4. **Diagnostics** — ping, nslookup, traceroute in tabs

Scan results show up in real-time. You can export reports from the sidebar.

## Stack

- Python 3.9+
- CustomTkinter (UI)
- socket / subprocess (scanning)
- psutil (network interface detection)
- threading + concurrent.futures (parallel scans)
- scapy (optional, for advanced packet stuff later)

## Project layout

```
src/
├── ui/            # all the panels and widgets
├── scanner/       # network discovery + port scanner
├── diagnostics/   # ping, dns, traceroute wrappers
├── analytics/     # stats calculations for dashboard
├── services/      # scan orchestration, report generation
└── utils/         # constants, network helpers
```

## Building an exe

```bash
pip install pyinstaller
pyinstaller --onefile --windowed --name "NetworkScanner" main.py
```

## TODO / roadmap

- [ ] topology visualization (networkx graph)
- [ ] better service fingerprinting
- [ ] scheduled/repeated scans
- [ ] PDF reports
- [ ] save scan history between sessions
- [ ] SNMP queries for managed switches

## License

MIT
