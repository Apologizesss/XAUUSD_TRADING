"""
MT5 Connection Test Script
==========================
ทดสอบการเชื่อมต่อกับ MetaTrader 5
"""

import os
import sys
from datetime import datetime

import MetaTrader5 as mt5
from dotenv import load_dotenv

# Load environment variables
load_dotenv("config/.env")

# Get credentials from .env
login = os.getenv("MT5_LOGIN", "")
password = os.getenv("MT5_PASSWORD", "")
server = os.getenv("MT5_SERVER", "")

print("=" * 70)
print(" " * 20 + "MT5 CONNECTION TEST")
print("=" * 70)
print()
print(f"📅 Date: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
print()

# Check if credentials exist
if not login or not password or not server:
    print("❌ ERROR: MT5 credentials not found in config/.env")
    print()
    print("Please edit config/.env and add:")
    print("  MT5_LOGIN=your_login_number")
    print("  MT5_PASSWORD=your_password")
    print("  MT5_SERVER=your_server_name")
    print()
    print("Example:")
    print("  MT5_LOGIN=12345678")
    print("  MT5_PASSWORD=mypassword123")
    print("  MT5_SERVER=XMGlobal-Demo 3")
    sys.exit(1)

# Check if credentials are still placeholders
if "YOUR_MT5" in login or "YOUR_MT5" in password or "YOUR_MT5" in server:
    print("❌ ERROR: You need to replace the placeholder values in config/.env")
    print()
    print("Please edit the file: config/.env")
    print()
    print("Replace these lines with your actual MT5 credentials:")
    print("  MT5_LOGIN=YOUR_MT5_LOGIN_NUMBER_HERE  ← Replace with your login number")
    print("  MT5_PASSWORD=YOUR_MT5_PASSWORD_HERE   ← Replace with your password")
    print("  MT5_SERVER=YOUR_MT5_SERVER_NAME_HERE  ← Replace with your server name")
    print()
    print("Example:")
    print("  MT5_LOGIN=50123456")
    print("  MT5_PASSWORD=MyPassword123")
    print("  MT5_SERVER=XMGlobal-Demo 3")
    print()
    print("Common server names:")
    print("  • XMGlobal-Demo 3")
    print("  • ICMarketsSC-Demo")
    print("  • Exness-Trial")
    print("  • Pepperstone-Demo")
    print("  • FBS-Demo")
    sys.exit(1)

print("📋 CREDENTIALS CHECK:")
print("-" * 50)
print(f"  Login:    {login}")
print(f"  Password: {'*' * len(password)}")
print(f"  Server:   {server}")
print()

# Initialize MT5
print("🔄 CONNECTING TO MT5...")
print("-" * 50)

if not mt5.initialize():
    print("❌ Failed to initialize MT5")
    print()
    error = mt5.last_error()
    if error:
        print(f"Error Code: {error[0]}")
        print(f"Error Message: {error[1]}")
    print()
    print("💡 SOLUTIONS:")
    print("  1. Make sure MetaTrader 5 is installed")
    print("  2. Open MetaTrader 5 application")
    print("  3. Check if MT5 is running")
    sys.exit(1)

print("✅ MT5 initialized successfully")
print()

# Get terminal info
terminal_info = mt5.terminal_info()
if terminal_info:
    print("💻 TERMINAL INFO:")
    print("-" * 50)
    # Some attributes might not exist in all versions
    if hasattr(terminal_info, "build"):
        print(f"  MT5 Build:       {terminal_info.build}")
    print(f"  Company:         {terminal_info.company}")
    print(f"  Language:        {terminal_info.language}")
    print(f"  Connected:       {'Yes' if terminal_info.connected else 'No'}")
    print(f"  Trade Allowed:   {'Yes' if terminal_info.trade_allowed else 'No'}")
    print()

# Login to account
print("🔐 LOGGING IN...")
print("-" * 50)

try:
    login_number = int(login)
    authorized = mt5.login(login_number, password, server)

    if not authorized:
        print("❌ Failed to login to account")
        error = mt5.last_error()
        if error:
            print(f"Error Code: {error[0]}")
            print(f"Error Message: {error[1]}")
        print()
        print("💡 SOLUTIONS:")
        print("  1. Check login credentials in config/.env")
        print("  2. Make sure it's a Demo account")
        print("  3. Check server name spelling")
        print("  4. Try logging in manually in MT5 first")
        mt5.shutdown()
        sys.exit(1)

except ValueError:
    print("❌ Invalid login number (must be numeric)")
    mt5.shutdown()
    sys.exit(1)

print("✅ Login successful!")
print()

# Get account info
account_info = mt5.account_info()
if account_info:
    print("💰 ACCOUNT INFO:")
    print("-" * 50)
    print(f"  Account:         {account_info.login}")
    print(f"  Server:          {account_info.server}")
    print(f"  Name:            {account_info.name}")
    print(f"  Company:         {account_info.company}")
    print(f"  Balance:         ${account_info.balance:,.2f}")
    print(f"  Equity:          ${account_info.equity:,.2f}")
    print(f"  Margin:          ${account_info.margin:,.2f}")
    print(f"  Free Margin:     ${account_info.margin_free:,.2f}")
    print(f"  Leverage:        1:{account_info.leverage}")
    print(f"  Trade Mode:      {'DEMO' if account_info.trade_mode == 0 else 'REAL'}")
    print(f"  Trade Allowed:   {'Yes' if account_info.trade_allowed else 'No'}")
    print()

# Check XAUUSD symbol
print("📊 CHECKING GOLD SYMBOL...")
print("-" * 50)

# Try different symbol names
gold_symbols = ["XAUUSD", "GOLD", "XAUUSDm", "XAUUSD.", "Gold"]
found_symbol = None

for symbol in gold_symbols:
    symbol_info = mt5.symbol_info(symbol)
    if symbol_info is not None and symbol_info.visible:
        found_symbol = symbol
        break

if not found_symbol:
    print("⚠️  Gold symbol not found")
    print()
    print("Available symbols containing 'GOLD' or 'XAU':")
    symbols = mt5.symbols_get()
    gold_related = [
        s.name for s in symbols if "GOLD" in s.name.upper() or "XAU" in s.name.upper()
    ]

    if gold_related:
        for s in gold_related[:10]:  # Show max 10 symbols
            print(f"  • {s}")
    else:
        print("  No gold-related symbols found")
        print()
        print("💡 Try checking Market Watch in MT5")
else:
    print(f"✅ Found gold symbol: {found_symbol}")

    # Get symbol info
    symbol_info = mt5.symbol_info(found_symbol)
    if symbol_info:
        print()
        print(f"  Description:     {symbol_info.description}")
        print(f"  Digits:          {symbol_info.digits}")
        print(f"  Point Size:      {symbol_info.point}")
        print(f"  Min Volume:      {symbol_info.volume_min}")
        print(f"  Max Volume:      {symbol_info.volume_max}")
        print(f"  Volume Step:     {symbol_info.volume_step}")
        print(f"  Contract Size:   {symbol_info.trade_contract_size}")
        print()

        # Get current price
        tick = mt5.symbol_info_tick(found_symbol)
        if tick:
            print(f"  Current Prices:")
            print(f"    Bid:         {tick.bid:.2f}")
            print(f"    Ask:         {tick.ask:.2f}")
            print(f"    Spread:      {(tick.ask - tick.bid) * 100:.1f} points")
            print(f"    Time:        {datetime.fromtimestamp(tick.time)}")

# Get recent bars
print()
print("📈 RECENT DATA TEST...")
print("-" * 50)

if found_symbol:
    # Try to get last 10 bars
    from datetime import timedelta

    rates = mt5.copy_rates_from_pos(found_symbol, mt5.TIMEFRAME_M5, 0, 10)

    if rates is not None and len(rates) > 0:
        print(f"✅ Successfully retrieved {len(rates)} bars")
        print()
        print("  Last 3 bars (M5):")
        for i, rate in enumerate(rates[-3:]):
            time_str = datetime.fromtimestamp(rate["time"]).strftime("%Y-%m-%d %H:%M")
            print(
                f"    {time_str} | O:{rate['open']:.2f} H:{rate['high']:.2f} L:{rate['low']:.2f} C:{rate['close']:.2f}"
            )
    else:
        print("⚠️  Could not retrieve price data")
        print("  Market might be closed")
else:
    print("⚠️  Cannot test data retrieval without valid symbol")

# Cleanup
mt5.shutdown()

print()
print("=" * 70)
print("✅ TEST COMPLETED SUCCESSFULLY!")
print("=" * 70)
print()
print("Your MT5 connection is working properly!")
print()
print("Next steps:")
print("  1. Run: python daily_update.py")
print("  2. Run: python paper_trading.py")
print()
