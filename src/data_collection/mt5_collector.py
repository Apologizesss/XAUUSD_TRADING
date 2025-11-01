"""
MT5 Data Collector for Gold (XAU/USD)
======================================
Collects historical and real-time price data from MetaTrader 5.

Features:
- Historical OHLCV data collection
- Multiple timeframes support
- Data validation and cleaning
- Automatic retry on connection failures
- Progress tracking
"""

import MetaTrader5 as mt5
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
from pathlib import Path
import os
import sys
from dotenv import load_dotenv
import time
from typing import Optional, List, Tuple

# Add project root to path
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

# Load environment variables
load_dotenv(project_root / "config" / ".env")


class MT5Collector:
    """Collects price data from MetaTrader 5"""

    # Timeframe mappings
    TIMEFRAMES = {
        "M1": mt5.TIMEFRAME_M1,  # 1 minute
        "M5": mt5.TIMEFRAME_M5,  # 5 minutes
        "M15": mt5.TIMEFRAME_M15,  # 15 minutes
        "M30": mt5.TIMEFRAME_M30,  # 30 minutes
        "H1": mt5.TIMEFRAME_H1,  # 1 hour
        "H4": mt5.TIMEFRAME_H4,  # 4 hours
        "D1": mt5.TIMEFRAME_D1,  # 1 day
    }

    def __init__(
        self,
        symbol: str = "XAUUSD",
        timeframe: str = "M15",
        output_dir: str = "data/raw",
    ):
        """
        Initialize MT5 Collector

        Args:
            symbol: Trading symbol (default: XAUUSD)
            timeframe: Timeframe for data collection (M1, M5, M15, M30, H1, H4, D1)
            output_dir: Directory to save collected data
        """
        self.symbol = symbol
        self.timeframe_str = timeframe
        self.timeframe = self.TIMEFRAMES.get(timeframe, mt5.TIMEFRAME_M15)
        self.output_dir = Path(project_root) / output_dir
        self.output_dir.mkdir(parents=True, exist_ok=True)

        self.connected = False
        self.symbol_info = None

    def initialize(self) -> bool:
        """
        Initialize connection to MT5

        Returns:
            bool: True if successful, False otherwise
        """
        print("Initializing MT5 connection...")

        # Get credentials from environment
        login = os.getenv("MT5_LOGIN")
        password = os.getenv("MT5_PASSWORD")
        server = os.getenv("MT5_SERVER")

        if not all([login, password, server]):
            print("❌ Missing MT5 credentials in .env file")
            return False

        try:
            login_int = int(login)
        except ValueError:
            print(f"❌ MT5_LOGIN must be numeric, got: {login}")
            return False

        # Try to initialize MT5 with login credentials
        terminal_path = r"C:\Program Files\MetaTrader 5\terminal64.exe"

        if os.path.exists(terminal_path):
            result = mt5.initialize(
                path=terminal_path, login=login_int, password=password, server=server
            )
        else:
            result = mt5.initialize(login=login_int, password=password, server=server)

        if not result:
            error = mt5.last_error()
            print(f"❌ MT5 initialization failed: {error}")
            return False

        # Verify account info
        account = mt5.account_info()
        if not account:
            print("❌ Could not get account info")
            mt5.shutdown()
            return False

        print(f"✅ Connected to MT5")
        print(f"   Account: {account.login}")
        print(f"   Server: {account.server}")
        print(f"   Balance: {account.balance} {account.currency}")

        self.connected = True
        return True

    def check_symbol(self) -> bool:
        """
        Check if symbol is available and enable it if needed

        Returns:
            bool: True if symbol is available, False otherwise
        """
        if not self.connected:
            print("❌ Not connected to MT5")
            return False

        # Try to get symbol info
        self.symbol_info = mt5.symbol_info(self.symbol)

        if self.symbol_info is None:
            print(f"❌ Symbol {self.symbol} not found")
            return False

        # Enable symbol if not visible
        if not self.symbol_info.visible:
            print(f"Enabling symbol {self.symbol}...")
            if not mt5.symbol_select(self.symbol, True):
                print(f"❌ Failed to enable {self.symbol}")
                return False
            self.symbol_info = mt5.symbol_info(self.symbol)

        print(f"✅ Symbol {self.symbol} is available")
        print(f"   Bid: {self.symbol_info.bid}")
        print(f"   Ask: {self.symbol_info.ask}")
        print(f"   Spread: {self.symbol_info.spread}")

        return True

    def collect_historical_data(
        self,
        days: int = 90,
        date_from: Optional[datetime] = None,
        date_to: Optional[datetime] = None,
    ) -> Optional[pd.DataFrame]:
        """
        Collect historical OHLCV data

        Args:
            days: Number of days to collect (if date_from/date_to not specified)
            date_from: Start date (optional)
            date_to: End date (optional)

        Returns:
            pd.DataFrame: Historical data or None if failed
        """
        if not self.connected:
            print("❌ Not connected to MT5. Call initialize() first.")
            return None

        if not self.symbol_info:
            if not self.check_symbol():
                return None

        # Set date range
        if date_to is None:
            date_to = datetime.now()
        if date_from is None:
            date_from = date_to - timedelta(days=days)

        print(f"\n📊 Collecting {self.symbol} data...")
        print(f"   Timeframe: {self.timeframe_str}")
        print(f"   From: {date_from.strftime('%Y-%m-%d %H:%M:%S')}")
        print(f"   To: {date_to.strftime('%Y-%m-%d %H:%M:%S')}")

        # Get rates
        rates = mt5.copy_rates_range(self.symbol, self.timeframe, date_from, date_to)

        if rates is None or len(rates) == 0:
            error = mt5.last_error()
            print(f"❌ Failed to get rates: {error}")
            return None

        # Convert to DataFrame
        df = pd.DataFrame(rates)

        # Convert timestamp to datetime
        df["time"] = pd.to_datetime(df["time"], unit="s")

        # Rename columns
        df.columns = [
            "timestamp",
            "open",
            "high",
            "low",
            "close",
            "tick_volume",
            "spread",
            "real_volume",
        ]

        # Add symbol and timeframe
        df["symbol"] = self.symbol
        df["timeframe"] = self.timeframe_str

        # Reorder columns
        df = df[
            [
                "timestamp",
                "symbol",
                "timeframe",
                "open",
                "high",
                "low",
                "close",
                "tick_volume",
                "real_volume",
                "spread",
            ]
        ]

        print(f"✅ Collected {len(df)} bars")
        print(f"   First: {df['timestamp'].iloc[0]}")
        print(f"   Last: {df['timestamp'].iloc[-1]}")

        return df

    def collect_recent_data(self, bars: int = 1000) -> Optional[pd.DataFrame]:
        """
        Collect most recent N bars

        Args:
            bars: Number of bars to collect

        Returns:
            pd.DataFrame: Recent data or None if failed
        """
        if not self.connected:
            print("❌ Not connected to MT5. Call initialize() first.")
            return None

        if not self.symbol_info:
            if not self.check_symbol():
                return None

        print(f"\n📊 Collecting {bars} recent bars for {self.symbol}...")

        # Get rates
        rates = mt5.copy_rates_from_pos(self.symbol, self.timeframe, 0, bars)

        if rates is None or len(rates) == 0:
            error = mt5.last_error()
            print(f"❌ Failed to get rates: {error}")
            return None

        # Convert to DataFrame
        df = pd.DataFrame(rates)
        df["time"] = pd.to_datetime(df["time"], unit="s")
        df.columns = [
            "timestamp",
            "open",
            "high",
            "low",
            "close",
            "tick_volume",
            "spread",
            "real_volume",
        ]
        df["symbol"] = self.symbol
        df["timeframe"] = self.timeframe_str

        df = df[
            [
                "timestamp",
                "symbol",
                "timeframe",
                "open",
                "high",
                "low",
                "close",
                "tick_volume",
                "real_volume",
                "spread",
            ]
        ]

        print(f"✅ Collected {len(df)} bars")

        return df

    def save_data(self, df: pd.DataFrame, filename: Optional[str] = None) -> str:
        """
        Save collected data to CSV

        Args:
            df: DataFrame to save
            filename: Custom filename (optional)

        Returns:
            str: Path to saved file
        """
        if filename is None:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"{self.symbol}_{self.timeframe_str}_{timestamp}.csv"

        filepath = self.output_dir / filename

        df.to_csv(filepath, index=False)
        print(f"💾 Saved to: {filepath}")

        return str(filepath)

    def validate_data(self, df: pd.DataFrame) -> Tuple[bool, List[str]]:
        """
        Validate collected data

        Args:
            df: DataFrame to validate

        Returns:
            Tuple[bool, List[str]]: (is_valid, list of issues)
        """
        issues = []

        # Check for missing values
        missing = df.isnull().sum()
        if missing.any():
            issues.append(f"Missing values found: {missing[missing > 0].to_dict()}")

        # Check for duplicates
        duplicates = df.duplicated(subset=["timestamp"]).sum()
        if duplicates > 0:
            issues.append(f"Found {duplicates} duplicate timestamps")

        # Check price consistency (high >= low, etc.)
        invalid_hl = (df["high"] < df["low"]).sum()
        if invalid_hl > 0:
            issues.append(f"Found {invalid_hl} bars where high < low")

        invalid_oc = ((df["open"] > df["high"]) | (df["open"] < df["low"])).sum()
        if invalid_oc > 0:
            issues.append(
                f"Found {invalid_oc} bars where open is outside high/low range"
            )

        invalid_cc = ((df["close"] > df["high"]) | (df["close"] < df["low"])).sum()
        if invalid_cc > 0:
            issues.append(
                f"Found {invalid_cc} bars where close is outside high/low range"
            )

        # Check for zero or negative prices
        zero_prices = (
            (df["open"] <= 0)
            | (df["high"] <= 0)
            | (df["low"] <= 0)
            | (df["close"] <= 0)
        ).sum()
        if zero_prices > 0:
            issues.append(f"Found {zero_prices} bars with zero or negative prices")

        # Check for extreme price jumps (possible data errors)
        df_sorted = df.sort_values("timestamp")
        price_change = df_sorted["close"].pct_change().abs()
        extreme_changes = (price_change > 0.1).sum()  # >10% change
        if extreme_changes > 0:
            issues.append(f"Warning: {extreme_changes} bars with >10% price change")

        is_valid = len(issues) == 0

        if is_valid:
            print("✅ Data validation passed")
        else:
            print("⚠️  Data validation issues found:")
            for issue in issues:
                print(f"   - {issue}")

        return is_valid, issues

    def get_data_summary(self, df: pd.DataFrame) -> dict:
        """
        Get summary statistics of collected data

        Args:
            df: DataFrame to summarize

        Returns:
            dict: Summary statistics
        """
        summary = {
            "total_bars": len(df),
            "date_range": f"{df['timestamp'].min()} to {df['timestamp'].max()}",
            "price_range": {
                "min": df["low"].min(),
                "max": df["high"].max(),
                "mean": df["close"].mean(),
                "std": df["close"].std(),
            },
            "volume": {
                "total_tick_volume": df["tick_volume"].sum(),
                "mean_tick_volume": df["tick_volume"].mean(),
                "total_real_volume": df["real_volume"].sum(),
                "mean_real_volume": df["real_volume"].mean(),
            },
            "spread": {
                "mean": df["spread"].mean(),
                "min": df["spread"].min(),
                "max": df["spread"].max(),
            },
        }

        return summary

    def shutdown(self):
        """Shutdown MT5 connection"""
        if self.connected:
            mt5.shutdown()
            print("🔌 MT5 connection closed")
            self.connected = False


def main():
    """Example usage"""
    print("=" * 70)
    print("MT5 DATA COLLECTOR - GOLD (XAU/USD)")
    print("=" * 70)
    print()

    # Initialize collector
    collector = MT5Collector(symbol="XAUUSD", timeframe="M15", output_dir="data/raw")

    # Connect to MT5
    if not collector.initialize():
        print("Failed to initialize MT5")
        return

    try:
        # Check symbol availability
        if not collector.check_symbol():
            print("Symbol not available")
            return

        # Collect 90 days of historical data
        df = collector.collect_historical_data(days=90)

        if df is not None:
            # Validate data
            is_valid, issues = collector.validate_data(df)

            # Get summary
            summary = collector.get_data_summary(df)
            print("\n📈 Data Summary:")
            print(f"   Total bars: {summary['total_bars']}")
            print(f"   Date range: {summary['date_range']}")
            print(
                f"   Price range: ${summary['price_range']['min']:.2f} - ${summary['price_range']['max']:.2f}"
            )
            print(f"   Mean price: ${summary['price_range']['mean']:.2f}")
            print(f"   Mean spread: {summary['spread']['mean']:.2f}")

            # Save data
            filepath = collector.save_data(df)

            print("\n✅ Data collection completed successfully!")
            print(f"   File: {filepath}")
            print(f"   Rows: {len(df)}")
            print(f"   Columns: {len(df.columns)}")

    except Exception as e:
        print(f"\n❌ Error during data collection: {e}")
        import traceback

        traceback.print_exc()

    finally:
        # Always shutdown
        collector.shutdown()


if __name__ == "__main__":
    main()
