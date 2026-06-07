#!/usr/bin/env python3
"""Quick smoke test — exercises all 5 tools directly without the MCP transport layer."""

import os
import sys
import tempfile
import shutil
from pathlib import Path

# Make sure we're running from the project root so .env is found
os.chdir(Path(__file__).parent)

from dotenv import load_dotenv
load_dotenv()

EXIFTOOL_PATH = os.environ.get("EXIFTOOL_PATH", "exiftool")
print(f"Using ExifTool: {EXIFTOOL_PATH}\n")

import exiftool

sys.path.insert(0, str(Path(__file__).parent))
import server  # noqa: E402

PASS = "\033[92mPASS\033[0m"
FAIL = "\033[91mFAIL\033[0m"

def run(label, fn):
    try:
        result = fn()
        print(f"[{PASS}] {label}")
        if result:
            print(f"       {result}")
        return True
    except Exception as e:
        print(f"[{FAIL}] {label}")
        print(f"       {e}")
        return False

# ------------------------------------------------------------------
# Locate a real image to test with — grab the first JPEG in C:\Tools
# or create a minimal valid JPEG if none found
# ------------------------------------------------------------------
def find_test_image():
    for root, _, files in os.walk("C:\\Tools"):
        for f in files:
            if f.lower().endswith((".jpg", ".jpeg")):
                return Path(root) / f
    return None

src = find_test_image()
if src:
    print(f"Test image: {src}\n")
    # work on a temp copy so we never modify the original
    tmp_dir = Path(tempfile.mkdtemp())
    test_img = tmp_dir / src.name
    shutil.copy2(src, test_img)
else:
    print("No JPEG found under C:\\Tools — creating a minimal test JPEG\n")
    # 1×1 white JPEG (smallest valid JPEG)
    tmp_dir = Path(tempfile.mkdtemp())
    test_img = tmp_dir / "test.jpg"
    test_img.write_bytes(
        b"\xff\xd8\xff\xe0\x00\x10JFIF\x00\x01\x01\x00\x00\x01\x00\x01\x00\x00"
        b"\xff\xdb\x00C\x00\x08\x06\x06\x07\x06\x05\x08\x07\x07\x07\t\t"
        b"\x08\n\x0c\x14\r\x0c\x0b\x0b\x0c\x19\x12\x13\x0f\x14\x1d\x1a"
        b"\x1f\x1e\x1d\x1a\x1c\x1c $.' \",#\x1c\x1c(7),01444\x1f'9=82<.342\x1e"
        b"\xff\xc0\x00\x0b\x08\x00\x01\x00\x01\x01\x01\x11\x00"
        b"\xff\xc4\x00\x1f\x00\x00\x01\x05\x01\x01\x01\x01\x01\x01\x00\x00"
        b"\x00\x00\x00\x00\x00\x00\x01\x02\x03\x04\x05\x06\x07\x08\t\n\x0b"
        b"\xff\xc4\x00\xb5\x10\x00\x02\x01\x03\x03\x02\x04\x03\x05\x05\x04"
        b"\x04\x00\x00\x01}\x01\x02\x03\x00\x04\x11\x05\x12!1A\x06\x13Qa"
        b"\x07\"q\x142\x81\x91\xa1\x08#B\xb1\xc1\x15R\xd1\xf0$3br"
        b"\x82\t\n\x16\x17\x18\x19\x1a%&'()*456789:CDEFGHIJ"
        b"STUVWXYZ\xff\xda\x00\x08\x01\x01\x00\x00?\x00\xfb"
        b"\xff\xd9"
    )

results = []

# 1. version
results.append(run(
    "exiftool_version()",
    lambda: str(server.exiftool_version())
))

# Helper that calls server functions directly
# 2. read_metadata (all tags)
results.append(run(
    "read_metadata(test_img)",
    lambda: f"{len(server.read_metadata(str(test_img)))} tags returned"
))

# 3. write_metadata
results.append(run(
    "write_metadata(test_img, {'EXIF:Artist': 'MCP Test'})",
    lambda: server.write_metadata(str(test_img), {"EXIF:Artist": "MCP Test"})
))

# 4. verify write stuck
def check_write():
    meta = server.read_metadata(str(test_img), tags=["EXIF:Artist"])
    artist = meta.get("EXIF:Artist", "")
    assert artist == "MCP Test", f"Expected 'MCP Test', got '{artist}'"
    return f"Artist = '{artist}'"
results.append(run("verify written tag", check_write))

# 5. copy_metadata
test_img2 = tmp_dir / ("copy_" + test_img.name)
shutil.copy2(test_img, test_img2)
results.append(run(
    "copy_metadata(src -> copy)",
    lambda: server.copy_metadata(str(test_img), str(test_img2))
))

# 6. strip_metadata
results.append(run(
    "strip_metadata(copy)",
    lambda: server.strip_metadata(str(test_img2))
))

# 7. verify strip worked
def check_strip():
    meta = server.read_metadata(str(test_img2), tags=["EXIF:Artist"])
    assert "EXIF:Artist" not in meta, f"Tag still present after strip: {meta}"
    return "No EXIF:Artist tag — strip confirmed"
results.append(run("verify strip removed tags", check_strip))

# Cleanup
shutil.rmtree(tmp_dir, ignore_errors=True)

print(f"\n{'='*40}")
passed = sum(results)
total = len(results)
status = PASS if passed == total else FAIL
print(f"[{status}] {passed}/{total} tests passed")
sys.exit(0 if passed == total else 1)
