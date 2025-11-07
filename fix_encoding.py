"""Fix encoding for Windows console"""

import io
import sys

# Force UTF-8 encoding for Windows console
if sys.platform == "win32":
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding="utf-8", errors="replace")

print("✅ UTF-8 encoding enabled")
print("📰 Testing emoji support...")
print("🤖 Robot emoji")
print("⚠️ Warning emoji")
