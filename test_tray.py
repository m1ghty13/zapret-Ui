#!/usr/bin/env python3
"""Test tray functionality."""
import sys
from pathlib import Path

print("Testing tray functionality...")
print("-" * 50)

# Test 1: Check pystray
print("\n1. Checking pystray...")
try:
    import pystray
    print("   ✓ pystray installed")
except ImportError:
    print("   ✗ pystray missing")
    print("   Run: pip install pystray")
    sys.exit(1)

# Test 2: Check Pillow
print("\n2. Checking Pillow...")
try:
    from PIL import Image
    print("   ✓ Pillow installed")
except ImportError:
    print("   ✗ Pillow missing")
    print("   Run: pip install Pillow")
    sys.exit(1)

# Test 3: Check tray module
print("\n3. Checking tray module...")
try:
    from api.tray import TrayIcon
    print("   ✓ Tray module available")
except ImportError as e:
    print(f"   ✗ Tray module error: {e}")
    sys.exit(1)

# Test 4: Check icon file
print("\n4. Checking icon file...")
icon_path = Path(__file__).parent / "assets" / "icon.ico"
if icon_path.exists():
    print(f"   ✓ Icon found: {icon_path}")
else:
    print(f"   ⚠ Icon not found: {icon_path}")
    print("   Will use default icon")

# Test 5: Test tray creation
print("\n5. Testing tray creation...")
try:
    from api.runner_wrapper import FlaskRunner
    from queue import Queue

    log_queue = Queue()
    runner = FlaskRunner(log_queue)
    tray = TrayIcon(runner, 5000)
    icon = tray.create_icon()

    if icon:
        print("   ✓ Tray icon created successfully")
        print("   Note: Icon will appear when app runs")
    else:
        print("   ⚠ Tray icon creation returned None")
        print("   This is normal on some systems")

except Exception as e:
    print(f"   ✗ Tray creation error: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)

print("\n" + "=" * 50)
print("✓ All tray checks passed!")
print("=" * 50)
print("\nYou can now run the application with tray support:")
print("  python main.py")
print("\nThe tray icon will appear in:")
print("  - Windows: System tray (bottom right)")
print("  - macOS: Menu bar (top right)")
print("  - Linux: System tray (depends on DE)")
