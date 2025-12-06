#!/usr/bin/env python3
"""
Run jury deliberation simulation
"""
import asyncio
import sys
import os

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from app.cli.deliberation_interface import main

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\n\nDeliberation terminated by user.")
        sys.exit(0)