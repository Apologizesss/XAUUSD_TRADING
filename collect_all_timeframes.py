"""
Collect Multiple Timeframes Data
=================================
Collects historical gold price data across multiple timeframes.

This script will collect:
- M5 (5 minutes)
- M15 (15 minutes)
- M30 (30 minutes)
- H1 (1 hour)
- H4 (4 hours)
- D1 (1 day)

For the past 90 days (or more depending on timeframe availability)
"""

import sys
from pathlib import Path
from datetime import datetime, timedelta
import time

# Add project root to path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

from src.data_collection.mt5_collector import MT5Collector


def collect_timeframe(timeframe: str, days: int = 90):
    """
    Collect data for a specific timeframe

    Args:
        timeframe: Timeframe code (M5, M15, M30, H1, H4, D1)
        days: Number of days to collect
    """
    print("\n" + "=" * 70)
    print(f"📊 COLLECTING {timeframe} DATA")
    print("=" * 70)

    # Initialize collector
    collector = MT5Collector(
        symbol="XAUUSD", timeframe=timeframe, output_dir="data/raw"
    )

    # Connect to MT5
    if not collector.initialize():
        print(f"❌ Failed to initialize MT5 for {timeframe}")
        return None

    try:
        # Check symbol
        if not collector.check_symbol():
            print(f"❌ Symbol not available for {timeframe}")
            return None

        # Collect data
        df = collector.collect_historical_data(days=days)

        if df is None:
            print(f"❌ Failed to collect data for {timeframe}")
            return None

        # Validate data
        is_valid, issues = collector.validate_data(df)

        if not is_valid:
            print(f"⚠️  Data validation issues for {timeframe}")

        # Get summary
        summary = collector.get_data_summary(df)
        print(f"\n📈 {timeframe} Summary:")
        print(f"   Total bars: {summary['total_bars']:,}")
        print(f"   Date range: {summary['date_range']}")
        print(
            f"   Price range: ${summary['price_range']['min']:.2f} - ${summary['price_range']['max']:.2f}"
        )

        # Save data
        filename = f"XAUUSD_{timeframe}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv"
        filepath = collector.save_data(df, filename)

        print(f"✅ {timeframe} data saved: {len(df):,} bars")

        return {
            "timeframe": timeframe,
            "bars": len(df),
            "filepath": filepath,
            "summary": summary,
        }

    except Exception as e:
        print(f"❌ Error collecting {timeframe}: {e}")
        import traceback

        traceback.print_exc()
        return None

    finally:
        collector.shutdown()
        time.sleep(2)  # Wait before next connection


def main():
    """Collect data for all timeframes"""
    print("=" * 70)
    print("🚀 MULTI-TIMEFRAME DATA COLLECTION")
    print("=" * 70)
    print()
    print("This will collect XAUUSD data for the following timeframes:")
    print("  • M5  (5 minutes)   - 90 days")
    print("  • M15 (15 minutes)  - 90 days")
    print("  • M30 (30 minutes)  - 90 days")
    print("  • H1  (1 hour)      - 180 days")
    print("  • H4  (4 hours)     - 365 days")
    print("  • D1  (1 day)       - 730 days")
    print()
    print("Estimated time: 2-3 minutes")
    print()

    input("Press ENTER to start collection...")
    print()

    # Define timeframes and their collection periods
    timeframes = [
        ("M5", 90),  # 5 minutes - 3 months
        ("M15", 90),  # 15 minutes - 3 months
        ("M30", 90),  # 30 minutes - 3 months
        ("H1", 180),  # 1 hour - 6 months
        ("H4", 365),  # 4 hours - 1 year
        ("D1", 730),  # 1 day - 2 years
    ]

    results = []
    start_time = time.time()

    for timeframe, days in timeframes:
        result = collect_timeframe(timeframe, days)
        if result:
            results.append(result)

        # Small delay between collections
        time.sleep(1)

    # Print summary
    elapsed_time = time.time() - start_time

    print("\n" + "=" * 70)
    print("📊 COLLECTION SUMMARY")
    print("=" * 70)
    print()

    if results:
        print(f"✅ Successfully collected {len(results)}/{len(timeframes)} timeframes")
        print()

        total_bars = 0
        for result in results:
            tf = result["timeframe"]
            bars = result["bars"]
            total_bars += bars
            print(f"   {tf:4s} : {bars:,} bars")

        print()
        print(f"📈 Total bars collected: {total_bars:,}")
        print(f"⏱️  Time elapsed: {elapsed_time:.1f} seconds")
        print()
        print(f"💾 Files saved in: data/raw/")
        print()

        # Detailed summary
        print("📋 Detailed Information:")
        print()
        for result in results:
            summary = result["summary"]
            print(f"   {result['timeframe']}:")
            print(f"      Bars: {summary['total_bars']:,}")
            print(f"      Range: {summary['date_range']}")
            print(
                f"      Price: ${summary['price_range']['min']:.2f} - ${summary['price_range']['max']:.2f}"
            )
            print()

        print("=" * 70)
        print("🎉 DATA COLLECTION COMPLETE!")
        print("=" * 70)
        print()
        print("Next step: Run exploratory data analysis (EDA)")
        print("  python analyze_data.py")
        print()

    else:
        print("❌ No data was collected successfully")
        print()
        print("Troubleshooting:")
        print("  1. Check MT5 is running and logged in")
        print("  2. Check Algo Trading is enabled (green)")
        print("  3. Check internet connection")
        print("  4. Run: python test_mt5_simple.py")
        print()


if __name__ == "__main__":
    main()
