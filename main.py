"""
Network Scanner Tool
====================
A modern network diagnostics and scanning utility.
Provides host discovery, port scanning, and quick diagnostic tools.

Author: Sahil Wade
License: MIT
"""

import sys
import os

# Ensure the project root is in the path for module imports
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from src.ui.app import NetworkScannerApp


def main():
    """Launch the Network Scanner Tool application."""
    app = NetworkScannerApp()
    app.run()


if __name__ == "__main__":
    main()
