"""
Test Package Installation
========================
ทดสอบว่าติดตั้ง packages ที่จำเป็นครบแล้วหรือไม่
"""

import sys

print("=" * 70)
print("TESTING PACKAGE INSTALLATION")
print("=" * 70)
print(f"Python Version: {sys.version}")
print("=" * 70)
print()

# Track results
success_count = 0
fail_count = 0
warning_count = 0


def test_import(module_name, alias=None, package_name=None):
    """Test importing a module"""
    global success_count, fail_count, warning_count

    display_name = package_name or module_name
    try:
        if alias:
            exec(f"import {module_name} as {alias}")
            # Try to get version
            try:
                version = eval(f"{alias}.__version__")
                print(f"✅ {display_name:<20} {version}")
            except:
                print(f"✅ {display_name:<20} (no version info)")
        else:
            exec(f"import {module_name}")
            # Try to get version
            try:
                version = eval(f"{module_name}.__version__")
                print(f"✅ {display_name:<20} {version}")
            except:
                print(f"✅ {display_name:<20} (no version info)")
        success_count += 1
        return True
    except ImportError as e:
        if "optional" in str(e).lower():
            print(f"⚠️  {display_name:<20} (optional - not installed)")
            warning_count += 1
        else:
            print(f"❌ {display_name:<20} FAILED - {str(e)[:50]}")
            fail_count += 1
        return False
    except Exception as e:
        print(f"❌ {display_name:<20} ERROR - {str(e)[:50]}")
        fail_count += 1
        return False


print("CORE PACKAGES:")
print("-" * 50)
test_import("MetaTrader5", "mt5")
test_import("pandas", "pd")
test_import("numpy", "np")
test_import("sklearn", package_name="scikit-learn")
test_import("xgboost", "xgb")
test_import("tensorflow", "tf")
test_import("torch")
test_import("transformers")

print("\nTECHNICAL ANALYSIS:")
print("-" * 50)
test_import("talib", package_name="TA-Lib")
test_import("pandas_ta")

print("\nDATA COLLECTION:")
print("-" * 50)
test_import("requests")
test_import("beautifulsoup4", "bs4", "BeautifulSoup4")
test_import("yfinance", "yf")
test_import("newsapi", package_name="newsapi-python")

print("\nVISUALIZATION:")
print("-" * 50)
test_import("matplotlib", "plt")
test_import("seaborn", "sns")
test_import("plotly")
test_import("mplfinance")

print("\nMACHINE LEARNING:")
print("-" * 50)
test_import("lightgbm", "lgb")
test_import("statsmodels")
test_import("scipy")

print("\nNLP & SENTIMENT:")
print("-" * 50)
test_import("nltk")
test_import("textblob")

print("\nUTILITIES:")
print("-" * 50)
test_import("dotenv", package_name="python-dotenv")
test_import("telegram", package_name="python-telegram-bot")
test_import("schedule")
test_import("sqlalchemy")
test_import("tqdm")
test_import("loguru")
test_import("joblib")

print("\nOTHER DEPENDENCIES:")
print("-" * 50)
test_import("pytz")
test_import("numba")
test_import("PIL", package_name="Pillow")

print("\n" + "=" * 70)
print("SUMMARY:")
print("-" * 50)
print(f"✅ Success: {success_count} packages")
print(f"❌ Failed:  {fail_count} packages")
print(f"⚠️  Warning: {warning_count} packages (optional)")
print("=" * 70)

if fail_count == 0:
    print("\n🎉 ALL REQUIRED PACKAGES INSTALLED SUCCESSFULLY!")
    print("\nYou can now run:")
    print("  python daily_update.py    - To update data")
    print("  python paper_trading.py   - To start paper trading")
else:
    print(f"\n⚠️  {fail_count} packages need to be installed.")
    print("\nTo install missing packages, run:")
    print("  python -m pip install [package_name]")

print("\n" + "=" * 70)

# Test MT5 connection
print("\nTESTING MT5 CONNECTION:")
print("-" * 50)
try:
    import MetaTrader5 as mt5

    if mt5.initialize():
        info = mt5.terminal_info()
        if info:
            print(f"✅ MT5 Terminal Connected")
            print(f"   Version: {info.version}")
            print(f"   Path: {info.path}")
        mt5.shutdown()
    else:
        print("⚠️  MT5 Terminal not running or not configured")
        print("   Make sure MetaTrader 5 is installed and running")
except Exception as e:
    print(f"⚠️  Could not test MT5: {e}")

print("=" * 70)
