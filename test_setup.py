#!/usr/bin/env python3
"""Test script to verify the setup."""
import sys
from pathlib import Path

print("Testing Zapret UI setup...")
print("-" * 50)

# Test 1: Check Python dependencies
print("\n1. Checking Python dependencies...")
try:
    import flask
    print("   ✓ flask installed")
except ImportError:
    print("   ✗ flask missing")
    sys.exit(1)

try:
    import flask_cors
    print("   ✓ flask-cors installed")
except ImportError:
    print("   ✗ flask-cors missing")
    sys.exit(1)

try:
    import webview
    print("   ✓ pywebview installed")
except ImportError:
    print("   ✗ pywebview missing")
    sys.exit(1)

# Test 2: Check React build
print("\n2. Checking React build...")
dist_dir = Path(__file__).parent / "dist"
if not dist_dir.exists():
    print("   ✗ dist/ directory not found")
    sys.exit(1)

if not (dist_dir / "index.html").exists():
    print("   ✗ dist/index.html not found")
    sys.exit(1)

print("   ✓ React app built")

# Test 3: Check API modules
print("\n3. Checking API modules...")
try:
    from api.server import app
    print("   ✓ Flask server module")
except ImportError as e:
    print(f"   ✗ Flask server module: {e}")
    sys.exit(1)

try:
    from api.bridge import JSBridge
    print("   ✓ PyWebView bridge")
except ImportError as e:
    print(f"   ✗ PyWebView bridge: {e}")
    sys.exit(1)

try:
    from api.runner_wrapper import FlaskRunner
    print("   ✓ Runner wrapper")
except ImportError as e:
    print(f"   ✗ Runner wrapper: {e}")
    sys.exit(1)

try:
    from api.tester_wrapper import FlaskTester
    print("   ✓ Tester wrapper")
except ImportError as e:
    print(f"   ✗ Tester wrapper: {e}")
    sys.exit(1)

# Test 4: Check core modules
print("\n4. Checking core modules...")
try:
    import core.config as cfg
    import core.strategies as strats
    import core.domains as domains_mod
    print("   ✓ Core modules available")
except ImportError as e:
    print(f"   ✗ Core modules: {e}")
    sys.exit(1)

print("\n" + "=" * 50)
print("✓ All checks passed!")
print("=" * 50)
print("\nYou can now run the application with:")
print("  python main.py")
