"""
Network Scanner Tool - entry point
"""

import sys
import os

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from src.ui.app import NetworkScannerApp


def main():
    app = NetworkScannerApp()
    app.run()


if __name__ == "__main__":
    main()
