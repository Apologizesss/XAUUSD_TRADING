"""Remove all non-ASCII characters from live_trading.py"""

import re

# Read file
with open("live_trading.py", "r", encoding="utf-8") as f:
    content = f.read()

print("Original length:", len(content))

# Count non-ASCII
non_ascii = re.findall(r"[^\x00-\x7F]", content)
print(f"Found {len(non_ascii)} non-ASCII characters")

# Replace specific emoji first (for better readability)
replacements = {
    "⚠️": "[WARNING]",
    "✓": "[OK]",
    "❌": "[ERROR]",
    "🔄": "[Processing]",
    "🔍": "[Info]",
    "🚀": "[Launch]",
    "💰": "[Money]",
    "📊": "[Stats]",
    "🔴": "[REAL]",
    "🔮": "[Predict]",
    "⏰": "[Time]",
    "📝": "[Note]",
    "💡": "[Tip]",
    "🛑": "[Stop]",
}

for emoji, text in replacements.items():
    if emoji in content:
        count = content.count(emoji)
        content = content.replace(emoji, text)
        print(f"Replaced {count}x '{emoji}' with '{text}'")

# Remove any remaining non-ASCII
before = len(content)
content = re.sub(r"[^\x00-\x7F]+", "", content)
after = len(content)

if before != after:
    print(f"Removed {before - after} remaining non-ASCII bytes")

# Write back
with open("live_trading.py", "w", encoding="utf-8") as f:
    f.write(content)

print("\nDone! Fixed live_trading.py")
print("Final length:", len(content))
