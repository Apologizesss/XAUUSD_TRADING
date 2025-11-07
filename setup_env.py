"""
Setup Environment Configuration
================================
สคริปต์สำหรับตั้งค่าไฟล์ .env จาก .env.example
และให้ผู้ใช้กรอกข้อมูล MT5 credentials
"""

import os
import shutil
import sys
from datetime import datetime
from pathlib import Path


def setup_env():
    """Setup .env file with user credentials"""

    print("=" * 70)
    print(" " * 15 + "🔧 SETUP ENVIRONMENT CONFIGURATION")
    print("=" * 70)
    print()

    # Check paths
    config_dir = Path("config")
    env_file = config_dir / ".env"
    env_example = config_dir / ".env.example"

    # Create config directory if not exists
    if not config_dir.exists():
        print("📁 Creating config directory...")
        config_dir.mkdir(parents=True)
        print("✅ Config directory created")
        print()

    # Check if .env.example exists
    if not env_example.exists():
        print("📝 Creating .env.example template...")
        example_content = """# MetaTrader 5 Credentials
MT5_LOGIN=your_demo_account_number
MT5_PASSWORD=your_demo_password
MT5_SERVER=your_broker_server

# News API (optional - get free key from https://newsapi.org)
NEWS_API_KEY=your_newsapi_key_here

# Telegram Bot (optional)
TELEGRAM_BOT_TOKEN=your_telegram_bot_token
TELEGRAM_CHAT_ID=your_telegram_chat_id

# Trading Parameters
INITIAL_CAPITAL=10000.0
MAX_RISK_PER_TRADE=0.02
MAX_DAILY_LOSS=0.05
MAX_DRAWDOWN=0.15

# Database
DATABASE_PATH=data/trading.db

# Logging
LOG_LEVEL=INFO
"""
        with open(env_example, "w", encoding="utf-8") as f:
            f.write(example_content)
        print("✅ Created .env.example")
        print()

    # Check existing .env
    if env_file.exists():
        # Check if it's empty
        file_size = env_file.stat().st_size
        if file_size > 0:
            print("⚠️  Found existing .env file")
            print(f"   Size: {file_size} bytes")
            print()

            response = input("Do you want to overwrite it? (y/n): ").lower()
            if response != "y":
                print("Keeping existing .env file")
                return
        else:
            print("📋 Found empty .env file, will configure it")
            print()

    # Backup existing .env if it exists and has content
    if env_file.exists() and env_file.stat().st_size > 0:
        backup_name = f".env.backup_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        backup_path = config_dir / backup_name
        shutil.copy2(env_file, backup_path)
        print(f"📦 Backed up existing .env to {backup_name}")
        print()

    print("=" * 70)
    print("Please enter your MetaTrader 5 Demo Account credentials:")
    print("-" * 70)
    print()
    print("💡 HOW TO GET THESE:")
    print("1. Open MetaTrader 5")
    print("2. Go to File → Open an Account")
    print("3. Choose a Demo server (e.g., XM, IC Markets, Exness)")
    print("4. You'll receive Login, Password, and Server name")
    print()
    print("-" * 70)
    print()

    # Get MT5 credentials from user
    mt5_login = input("Enter MT5 Login (numbers only, e.g., 12345678): ").strip()

    # Validate login is numeric
    while not mt5_login.isdigit():
        print("❌ Login must be numeric!")
        mt5_login = input("Enter MT5 Login (numbers only): ").strip()

    mt5_password = input("Enter MT5 Password: ").strip()

    print()
    print("Common server names examples:")
    print("  • XMGlobal-Demo 3")
    print("  • ICMarketsSC-Demo")
    print("  • Exness-Trial")
    print("  • Pepperstone-Demo")
    print("  • FBS-Demo")
    print()

    mt5_server = input("Enter MT5 Server name: ").strip()

    # Optional: News API
    print()
    print("-" * 70)
    print("📰 News API (Optional - press Enter to skip)")
    print("Get free key from: https://newsapi.org")
    news_api_key = input("Enter News API Key (or press Enter to skip): ").strip()

    if not news_api_key:
        news_api_key = "your_newsapi_key_here"

    # Optional: Telegram
    print()
    print("-" * 70)
    print("📱 Telegram Bot (Optional - press Enter to skip)")
    telegram_token = input(
        "Enter Telegram Bot Token (or press Enter to skip): "
    ).strip()
    telegram_chat_id = input(
        "Enter Telegram Chat ID (or press Enter to skip): "
    ).strip()

    if not telegram_token:
        telegram_token = "your_telegram_bot_token"
    if not telegram_chat_id:
        telegram_chat_id = "your_telegram_chat_id"

    # Create .env content
    env_content = f"""# MetaTrader 5 Credentials
MT5_LOGIN={mt5_login}
MT5_PASSWORD={mt5_password}
MT5_SERVER={mt5_server}

# News API (optional - get free key from https://newsapi.org)
NEWS_API_KEY={news_api_key}

# Telegram Bot (optional)
TELEGRAM_BOT_TOKEN={telegram_token}
TELEGRAM_CHAT_ID={telegram_chat_id}

# Trading Parameters
INITIAL_CAPITAL=10000.0
MAX_RISK_PER_TRADE=0.02
MAX_DAILY_LOSS=0.05
MAX_DRAWDOWN=0.15

# Database
DATABASE_PATH=data/trading.db

# Logging
LOG_LEVEL=INFO

# Created by setup_env.py on {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}
"""

    # Write .env file
    print()
    print("-" * 70)
    print("💾 Saving configuration...")

    with open(env_file, "w", encoding="utf-8") as f:
        f.write(env_content)

    print(f"✅ Configuration saved to: {env_file}")
    print()

    # Verify the file
    if env_file.exists():
        file_size = env_file.stat().st_size
        print(f"📊 File size: {file_size} bytes")

        # Count lines
        with open(env_file, "r", encoding="utf-8") as f:
            lines = f.readlines()

        non_empty_lines = [line for line in lines if line.strip()]
        print(f"📝 Total lines: {len(non_empty_lines)}")

    print()
    print("=" * 70)
    print("✅ SETUP COMPLETED SUCCESSFULLY!")
    print("=" * 70)
    print()
    print("Your credentials have been saved to config/.env")
    print()
    print("Next steps:")
    print("1. Run: python test_mt5.py")
    print("   To test the MT5 connection")
    print()
    print("2. Run: python daily_update.py")
    print("   To update market data")
    print()
    print("3. Run: python paper_trading.py")
    print("   To start paper trading")
    print()
    print("⚠️ IMPORTANT: Make sure MetaTrader 5 is running!")
    print()


if __name__ == "__main__":
    try:
        setup_env()
    except KeyboardInterrupt:
        print("\n\n❌ Setup cancelled by user")
        sys.exit(1)
    except Exception as e:
        print(f"\n❌ Error: {e}")
        sys.exit(1)
