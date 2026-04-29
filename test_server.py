#!/usr/bin/env python3
"""Quick test to verify Flask server starts."""
import sys
import time
import threading

print("Testing Flask server startup...")

try:
    from api.server import start_server

    # Start server in background
    port = start_server()
    print(f"✓ Flask server started on port {port}")

    # Test a simple endpoint
    import urllib.request
    time.sleep(1)

    try:
        response = urllib.request.urlopen(f"http://127.0.0.1:{port}/api/status", timeout=5)
        data = response.read()
        print(f"✓ API endpoint responding: {data[:100]}...")
        print("\n✓ Server test passed!")
    except Exception as e:
        print(f"✗ API endpoint test failed: {e}")
        sys.exit(1)

except Exception as e:
    print(f"✗ Server startup failed: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)
