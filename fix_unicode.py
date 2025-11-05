"""
Fix Unicode/Emoji Issues in Python Files
Replace emoji with ASCII text for Windows compatibility
"""

import re
from pathlib import Path

# Define emoji replacements
EMOJI_REPLACEMENTS = {
    "🔧": "[Feature Engineering]",
    "✅": "[OK]",
    "📊": "[Stats]",
    "⏰": "[Time]",
    "1️⃣": "[1]",
    "2️⃣": "[2]",
    "3️⃣": "[3]",
    "📈": "[Chart]",
    "🔍": "[Search]",
    "⚠️": "[Warning]",
    "❌": "[Error]",
    "🎯": "[Target]",
    "💾": "[Save]",
    "📝": "[Note]",
    "🚀": "[Launch]",
    "✓": "[OK]",
    "❗": "[!]",
    "⚙️": "[Config]",
    "🎉": "[Success]",
    "📉": "[Down]",
    "🔄": "[Reload]",
    "💡": "[Tip]",
    "🛑": "[Stop]",
    "🆘": "[Help]",
}


def fix_unicode_in_file(file_path):
    """Remove emoji from a Python file"""
    print(f"\nProcessing: {file_path}")

    try:
        # Read file
        with open(file_path, "r", encoding="utf-8") as f:
            content = f.read()

        original_content = content
        changes = 0

        # Replace each emoji
        for emoji, replacement in EMOJI_REPLACEMENTS.items():
            if emoji in content:
                count = content.count(emoji)
                content = content.replace(emoji, replacement)
                changes += count
                print(f"  Replaced {count}x '{emoji}' with '{replacement}'")

        # Write back if changes were made
        if changes > 0:
            with open(file_path, "w", encoding="utf-8") as f:
                f.write(content)
            print(f"  ✓ Saved {changes} changes")
            return True
        else:
            print(f"  No emoji found")
            return False

    except Exception as e:
        print(f"  ERROR: {e}")
        return False


def main():
    print("=" * 70)
    print("UNICODE/EMOJI FIX UTILITY")
    print("=" * 70)

    # Files to fix
    files_to_fix = [
        "src/features/feature_pipeline.py",
        "src/features/technical_indicators.py",
        "collect_more_data.py",
        "daily_update.py",
        "train_simple.py",
        "train_no_stop.py",
        "train_advanced.py",
        "process_all_timeframes.py",
        "src/models/data_preprocessor.py",
        "src/models/ensemble.py",
        "src/models/train_lstm.py",
        "src/models/train_random_forest.py",
        "src/models/train_xgboost.py",
        "train_to_70_percent.py",
    ]

    fixed_count = 0
    for file_path in files_to_fix:
        path = Path(file_path)
        if path.exists():
            if fix_unicode_in_file(path):
                fixed_count += 1
        else:
            print(f"\nSkipping (not found): {file_path}")

    print("\n" + "=" * 70)
    print(f"COMPLETE: Fixed {fixed_count} files")
    print("=" * 70)


if __name__ == "__main__":
    main()
