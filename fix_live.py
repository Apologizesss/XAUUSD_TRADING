"""Fix all emoji in live_trading.py"""

# Read file
with open("live_trading.py", "r", encoding="utf-8") as f:
    content = f.read()

# Replace emoji with ASCII
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
    "📉": "[Down]",
}

count = 0
for emoji, text in replacements.items():
    if emoji in content:
        n = content.count(emoji)
        content = content.replace(emoji, text)
        count += n
        print(f"Replaced {n}x '{emoji}' -> '{text}'")

# Write back
with open("live_trading.py", "w", encoding="utf-8") as f:
    f.write(content)

print(f"\nTotal: Fixed {count} emoji in live_trading.py")
