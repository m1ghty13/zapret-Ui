"""Download zapret Windows binaries from the latest GitHub release."""
import sys
import json
import urllib.request
import zipfile
import io
from pathlib import Path

ROOT = Path(__file__).parent.parent
BIN = ROOT / "bin"
BIN.mkdir(exist_ok=True)

NEEDED = {"winws.exe", "WinDivert.dll", "WinDivert64.sys", "cygwin1.dll"}
ARCH_DIR = "windows-x86_64"

API = "https://api.github.com/repos/bol-van/zapret/releases/latest"

def main():
    already = {f.name for f in BIN.iterdir() if f.is_file() and f.name in NEEDED}
    if already >= NEEDED:
        print("  Binaries already present, skipping download.")
        sys.exit(0)

    print("  Fetching latest zapret release info...")
    req = urllib.request.Request(API, headers={"User-Agent": "zapret-ui-builder"})
    with urllib.request.urlopen(req, timeout=30) as r:
        release = json.loads(r.read())

    tag = release["tag_name"]
    zip_url = next(
        a["browser_download_url"]
        for a in release["assets"]
        if a["name"].endswith(".zip")
    )
    print(f"  Downloading {tag}...")

    with urllib.request.urlopen(zip_url, timeout=120) as r:
        data = r.read()

    print("  Extracting binaries...")
    with zipfile.ZipFile(io.BytesIO(data)) as z:
        for entry in z.namelist():
            parts = entry.replace("\\", "/").split("/")
            if ARCH_DIR in parts:
                name = parts[-1]
                if name in NEEDED:
                    dest = BIN / name
                    dest.write_bytes(z.read(entry))
                    print(f"  Extracted: {name}")

    missing = NEEDED - {f.name for f in BIN.iterdir() if f.is_file()}
    if missing:
        print(f"  ERROR: missing after extraction: {missing}", file=sys.stderr)
        sys.exit(1)

    print("  Done.")

if __name__ == "__main__":
    main()
