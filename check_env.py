"""
Check .env Configuration
========================
ตรวจสอบการอ่านค่าจากไฟล์ .env
"""

import os
import sys
from pathlib import Path

from dotenv import load_dotenv

print("=" * 70)
print("CHECKING .ENV CONFIGURATION")
print("=" * 70)
print()

# Check current directory
current_dir = Path.cwd()
print(f"📁 Current Directory: {current_dir}")
print()

# List all possible .env locations
env_locations = [
    ".env",
    "config/.env",
    "config\\.env",
    "../.env",
    "./.env",
    "./config/.env",
    Path("config") / ".env",
    Path.cwd() / "config" / ".env",
]

print("🔍 Searching for .env file...")
print("-" * 50)

found_env_files = []
for location in env_locations:
    try:
        path = Path(location)
        if path.exists():
            found_env_files.append(str(path))
            print(f"✅ Found: {path}")
            # Check if it's readable
            try:
                with open(path, "r") as f:
                    lines = f.readlines()
                    print(f"   Size: {len(lines)} lines")
            except Exception as e:
                print(f"   ⚠️ Cannot read: {e}")
        else:
            print(f"❌ Not found: {location}")
    except Exception as e:
        print(f"❌ Error checking {location}: {e}")

print()
print("=" * 70)
print()

# Try to load from different locations
print("🔧 Attempting to load .env from different paths...")
print("-" * 50)

# Method 1: Load from config/.env
print("\nMethod 1: load_dotenv('config/.env')")
result1 = load_dotenv("config/.env")
print(f"Result: {result1}")
mt5_login_1 = os.getenv("MT5_LOGIN")
print(f"MT5_LOGIN: {mt5_login_1}")

# Method 2: Load from config\.env (Windows style)
print("\nMethod 2: load_dotenv('config\\.env')")
result2 = load_dotenv("config\\.env")
print(f"Result: {result2}")
mt5_login_2 = os.getenv("MT5_LOGIN")
print(f"MT5_LOGIN: {mt5_login_2}")

# Method 3: Load using Path
print("\nMethod 3: Using Path object")
env_path = Path("config") / ".env"
print(f"Path: {env_path}")
print(f"Exists: {env_path.exists()}")
if env_path.exists():
    result3 = load_dotenv(env_path)
    print(f"Result: {result3}")
    mt5_login_3 = os.getenv("MT5_LOGIN")
    print(f"MT5_LOGIN: {mt5_login_3}")

# Method 4: Absolute path
print("\nMethod 4: Using absolute path")
abs_env_path = Path.cwd() / "config" / ".env"
print(f"Absolute Path: {abs_env_path}")
print(f"Exists: {abs_env_path.exists()}")
if abs_env_path.exists():
    result4 = load_dotenv(abs_env_path)
    print(f"Result: {result4}")
    mt5_login_4 = os.getenv("MT5_LOGIN")
    print(f"MT5_LOGIN: {mt5_login_4}")

print()
print("=" * 70)
print()

# Show all environment variables starting with MT5
print("📋 ALL MT5 ENVIRONMENT VARIABLES:")
print("-" * 50)
mt5_vars = {k: v for k, v in os.environ.items() if k.startswith("MT5")}
if mt5_vars:
    for key, value in mt5_vars.items():
        if "PASSWORD" in key:
            print(f"{key}: {'*' * len(value) if value else 'None'}")
        else:
            print(f"{key}: {value}")
else:
    print("❌ No MT5 variables found in environment")

print()
print("=" * 70)
print()

# Check config directory contents
print("📂 CONFIG DIRECTORY CONTENTS:")
print("-" * 50)
config_dir = Path("config")
if config_dir.exists():
    print(f"Directory exists: {config_dir.absolute()}")
    print("\nFiles in config directory:")
    for file in config_dir.iterdir():
        print(f"  • {file.name} ({file.stat().st_size} bytes)")
        if file.name.startswith(".env"):
            print(f"    → This looks like an env file!")
else:
    print(f"❌ Config directory not found at: {config_dir.absolute()}")

print()
print("=" * 70)
print()

# Try to read .env directly
print("📝 DIRECT READ ATTEMPT:")
print("-" * 50)
env_file_path = Path("config") / ".env"
if env_file_path.exists():
    print(f"Reading from: {env_file_path.absolute()}")
    try:
        with open(env_file_path, "r", encoding="utf-8") as f:
            content = f.read()
            lines = content.split("\n")
            print(f"\nFile has {len(lines)} lines")
            print("\nFirst 5 non-comment lines:")
            non_comment_lines = [
                line
                for line in lines
                if line.strip() and not line.strip().startswith("#")
            ]
            for line in non_comment_lines[:5]:
                if "PASSWORD" in line.upper():
                    key_part = line.split("=")[0] if "=" in line else line
                    print(f"  {key_part}=*****")
                else:
                    print(f"  {line[:50]}...")
    except Exception as e:
        print(f"❌ Error reading file: {e}")
else:
    print(f"❌ File not found at: {env_file_path.absolute()}")

print()
print("=" * 70)
print("RECOMMENDATIONS:")
print("-" * 50)

if not mt5_vars:
    print("⚠️ No MT5 variables loaded. Try:")
    print()
    print("1. Make sure .env file is in the 'config' folder")
    print("2. Check file name is exactly '.env' (not '.env.txt' or 'env')")
    print("3. Make sure no spaces in variable names")
    print("4. Format should be: MT5_LOGIN=12345678")
    print()
    print("Example .env content:")
    print("MT5_LOGIN=12345678")
    print("MT5_PASSWORD=yourpassword")
    print("MT5_SERVER=XMGlobal-Demo 3")
else:
    print("✅ MT5 variables loaded successfully!")
    print()
    if not mt5_vars.get("MT5_LOGIN"):
        print("⚠️ MT5_LOGIN is missing")
    if not mt5_vars.get("MT5_PASSWORD"):
        print("⚠️ MT5_PASSWORD is missing")
    if not mt5_vars.get("MT5_SERVER"):
        print("⚠️ MT5_SERVER is missing")

print()
print("=" * 70)
