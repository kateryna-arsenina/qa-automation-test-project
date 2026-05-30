#!/usr/bin/env python3
"""
Print the report path and open it in the default browser.
"""
import os
import subprocess
import sys

path = os.path.abspath(sys.argv[1])

print(f"\n  Report: {path}")

try:
    subprocess.run(["open", path], check=True)
    print("  Opened in browser.\n")
except Exception:
    print(f"  To open manually: open \"{path}\"\n")
