"""
Time-Based Features Module
===========================
Extracts time-based features for trading analysis.

Features include:
- Hour of day, day of week, month, quarter
- Trading sessions (Asian, European, US)
- Market opening/closing times
- Weekend/holiday indicators
- Time cyclical encoding (sin/cos transformations)

Usage:
    from src.features.time_features import TimeFeatures

    tf = TimeFeatures()
    df = tf.add_all_time_features(df)
"""

import pandas as pd
import numpy as np
from datetime import datetime
from typing import Optional
import warnings

warnings.filterwarnings("ignore")


class TimeFeatures:
    """Extracts time-based features from timestamp"""

    def __init__(self):
        """Initialize Time Features extractor"""
        self.required_columns = ["timestamp"]

        # Define trading sessions (UTC time)
        self.sessions = {
            "sydney": (21, 6),  # 21:00 - 06:00 UTC
            "tokyo": (0, 9),  # 00:00 - 09:00 UTC
            "london": (8, 16),  # 08:00 - 16:00 UTC
            "newyork": (13, 22),  # 13:00 - 22:00 UTC
        }

        # Major market overlaps (high liquidity)
        self.overlaps = {
            "london_newyork": (13, 16),  # 13:00 - 16:00 UTC
            "tokyo_london": (8, 9),  # 08:00 - 09:00 UTC
        }

    def validate_data(self, df: pd.DataFrame) -> bool:
        """
        Validate that DataFrame has required columns

        Args:
            df: Input DataFrame

        Returns:
            bool: True if valid, False otherwise
        """
        if "timestamp" not in df.columns:
            print("❌ Missing 'timestamp' column")
            return False

        return True

    def ensure_datetime(self, df: pd.DataFrame) -> pd.DataFrame:
        """Convert timestamp to datetime if needed"""
        if not pd.api.types.is_datetime64_any_dtype(df["timestamp"]):
            df["timestamp"] = pd.to_datetime(df["timestamp"])
        return df

    # ========================================================================
    # BASIC TIME FEATURES
    # ========================================================================

    def add_basic_time_features(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Add basic time features

        Features:
        - hour, day_of_week, day_of_month, month, quarter, year
        - is_weekend, is_month_start, is_month_end, is_quarter_start, is_quarter_end
        """
        print("  ├─ Basic Time Features...")

        df = self.ensure_datetime(df)

        # Extract components
        df["hour"] = df["timestamp"].dt.hour
        df["day_of_week"] = df["timestamp"].dt.dayofweek  # Monday=0, Sunday=6
        df["day_of_month"] = df["timestamp"].dt.day
        df["week_of_year"] = df["timestamp"].dt.isocalendar().week
        df["month"] = df["timestamp"].dt.month
        df["quarter"] = df["timestamp"].dt.quarter
        df["year"] = df["timestamp"].dt.year

        # Boolean indicators
        df["is_weekend"] = (df["day_of_week"] >= 5).astype(int)  # Saturday=5, Sunday=6
        df["is_monday"] = (df["day_of_week"] == 0).astype(int)
        df["is_friday"] = (df["day_of_week"] == 4).astype(int)

        # Month/Quarter boundaries
        df["is_month_start"] = df["timestamp"].dt.is_month_start.astype(int)
        df["is_month_end"] = df["timestamp"].dt.is_month_end.astype(int)
        df["is_quarter_start"] = df["timestamp"].dt.is_quarter_start.astype(int)
        df["is_quarter_end"] = df["timestamp"].dt.is_quarter_end.astype(int)

        return df

    # ========================================================================
    # TRADING SESSIONS
    # ========================================================================

    def add_trading_sessions(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Add trading session indicators

        Sessions (UTC):
        - Sydney: 21:00 - 06:00
        - Tokyo/Asian: 00:00 - 09:00
        - London/European: 08:00 - 16:00
        - New York/US: 13:00 - 22:00
        """
        print("  ├─ Trading Sessions...")

        df = self.ensure_datetime(df)

        if "hour" not in df.columns:
            df["hour"] = df["timestamp"].dt.hour

        # Sydney session
        df["session_sydney"] = ((df["hour"] >= 21) | (df["hour"] < 6)).astype(int)

        # Tokyo/Asian session
        df["session_tokyo"] = ((df["hour"] >= 0) & (df["hour"] < 9)).astype(int)

        # London/European session
        df["session_london"] = ((df["hour"] >= 8) & (df["hour"] < 16)).astype(int)

        # New York/US session
        df["session_newyork"] = ((df["hour"] >= 13) & (df["hour"] < 22)).astype(int)

        # Market overlaps (high liquidity periods)
        df["overlap_london_newyork"] = ((df["hour"] >= 13) & (df["hour"] < 16)).astype(
            int
        )

        df["overlap_tokyo_london"] = ((df["hour"] >= 8) & (df["hour"] < 9)).astype(int)

        # Categorize main session
        def get_main_session(hour):
            if 0 <= hour < 8:
                return 1  # Asian
            elif 8 <= hour < 13:
                return 2  # European
            elif 13 <= hour < 22:
                return 3  # US
            else:
                return 4  # After-hours

        df["main_session"] = df["hour"].apply(get_main_session)

        return df

    # ========================================================================
    # MARKET HOURS
    # ========================================================================

    def add_market_hours(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Add market hours indicators

        Features:
        - Market open/close times
        - Pre-market, regular hours, after-hours
        - Time until/since major events
        """
        print("  ├─ Market Hours...")

        df = self.ensure_datetime(df)

        if "hour" not in df.columns:
            df["hour"] = df["timestamp"].dt.hour

        # Trading hours activity
        df["is_liquid_hours"] = ((df["hour"] >= 8) & (df["hour"] < 22)).astype(int)

        df["is_low_liquidity"] = ((df["hour"] >= 22) | (df["hour"] < 8)).astype(int)

        # Peak trading hours (London-NY overlap)
        df["is_peak_hours"] = ((df["hour"] >= 13) & (df["hour"] < 16)).astype(int)

        # Market open/close proximity
        # London open: 08:00
        df["hours_since_london_open"] = df["hour"].apply(
            lambda h: h - 8 if h >= 8 else h + 16
        )

        # NY open: 13:00
        df["hours_since_ny_open"] = df["hour"].apply(
            lambda h: h - 13 if h >= 13 else h + 11
        )

        return df

    # ========================================================================
    # CYCLICAL ENCODING
    # ========================================================================

    def add_cyclical_features(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Add cyclical encoding using sine/cosine transformations

        This preserves the cyclical nature of time (e.g., hour 23 is close to hour 0)
        """
        print("  ├─ Cyclical Encoding...")

        df = self.ensure_datetime(df)

        # Hour (24-hour cycle)
        if "hour" not in df.columns:
            df["hour"] = df["timestamp"].dt.hour

        df["hour_sin"] = np.sin(2 * np.pi * df["hour"] / 24)
        df["hour_cos"] = np.cos(2 * np.pi * df["hour"] / 24)

        # Day of week (7-day cycle)
        if "day_of_week" not in df.columns:
            df["day_of_week"] = df["timestamp"].dt.dayofweek

        df["day_sin"] = np.sin(2 * np.pi * df["day_of_week"] / 7)
        df["day_cos"] = np.cos(2 * np.pi * df["day_of_week"] / 7)

        # Day of month (30-day cycle - approximate)
        if "day_of_month" not in df.columns:
            df["day_of_month"] = df["timestamp"].dt.day

        df["dom_sin"] = np.sin(2 * np.pi * df["day_of_month"] / 30)
        df["dom_cos"] = np.cos(2 * np.pi * df["day_of_month"] / 30)

        # Month (12-month cycle)
        if "month" not in df.columns:
            df["month"] = df["timestamp"].dt.month

        df["month_sin"] = np.sin(2 * np.pi * df["month"] / 12)
        df["month_cos"] = np.cos(2 * np.pi * df["month"] / 12)

        return df

    # ========================================================================
    # TIME SINCE EVENTS
    # ========================================================================

    def add_time_since_events(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Add time since specific events

        Features:
        - Minutes/hours since session start
        - Time to next session
        - Time since weekend
        """
        print("  ├─ Time Since Events...")

        df = self.ensure_datetime(df)

        # Minutes since midnight (start of day)
        df["minutes_since_midnight"] = (
            df["timestamp"].dt.hour * 60 + df["timestamp"].dt.minute
        )

        # Normalize to 0-1
        df["time_of_day_normalized"] = df["minutes_since_midnight"] / (24 * 60)

        # Days since start of month
        df["days_since_month_start"] = df["timestamp"].dt.day - 1

        # Days until end of month
        df["days_to_month_end"] = (
            df["timestamp"].dt.days_in_month - df["timestamp"].dt.day
        )

        return df

    # ========================================================================
    # SPECIAL PERIODS
    # ========================================================================

    def add_special_periods(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Add indicators for special trading periods

        Features:
        - First/Last hour of trading day
        - First/Last day of week/month
        - Holiday proximity (simplified)
        """
        print("  ├─ Special Periods...")

        df = self.ensure_datetime(df)

        if "hour" not in df.columns:
            df["hour"] = df["timestamp"].dt.hour
        if "day_of_week" not in df.columns:
            df["day_of_week"] = df["timestamp"].dt.dayofweek
        if "day_of_month" not in df.columns:
            df["day_of_month"] = df["timestamp"].dt.day

        # First/Last hour of active trading
        df["is_first_hour_london"] = (df["hour"] == 8).astype(int)
        df["is_last_hour_ny"] = (df["hour"] == 21).astype(int)

        # First/Last day of week
        df["is_first_day_of_week"] = (df["day_of_week"] == 0).astype(int)
        df["is_last_day_of_week"] = (df["day_of_week"] == 4).astype(int)

        # First/Last 5 days of month
        df["is_first_5_days"] = (df["day_of_month"] <= 5).astype(int)
        df["is_last_5_days"] = (
            df["day_of_month"] >= (df["timestamp"].dt.days_in_month - 5)
        ).astype(int)

        # Week number in month (1-5)
        df["week_of_month"] = ((df["day_of_month"] - 1) // 7) + 1

        return df

    # ========================================================================
    # MAIN FUNCTION
    # ========================================================================

    def add_all_time_features(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Add all time-based features to DataFrame

        Args:
            df: Input DataFrame with timestamp column

        Returns:
            DataFrame with added time features
        """
        print("\n⏰ Adding Time-Based Features...")
        print("=" * 70)

        # Validate data
        if not self.validate_data(df):
            return df

        # Make a copy
        df = df.copy()

        # Add all feature groups
        try:
            df = self.add_basic_time_features(df)
            df = self.add_trading_sessions(df)
            df = self.add_market_hours(df)
            df = self.add_cyclical_features(df)
            df = self.add_time_since_events(df)
            df = self.add_special_periods(df)

            print("  └─ ✅ All time features added!")

            # Count features
            time_feature_cols = [
                col
                for col in df.columns
                if col
                not in [
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

            # Count only time features (those we just added)
            original_cols = [
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
            new_time_features = [col for col in df.columns if col not in original_cols]

            print(f"\n⏰ Total time features created: {len(new_time_features)}")

        except Exception as e:
            print(f"\n❌ Error adding time features: {e}")
            import traceback

            traceback.print_exc()

        return df

    def get_feature_list(self, df: pd.DataFrame) -> list:
        """
        Get list of time feature names

        Returns:
            list: Time feature column names
        """
        time_keywords = [
            "hour",
            "day",
            "week",
            "month",
            "quarter",
            "year",
            "session",
            "overlap",
            "liquid",
            "peak",
            "sin",
            "cos",
            "since",
            "until",
            "normalized",
            "is_weekend",
            "is_monday",
            "is_friday",
            "main_session",
            "minutes_since",
        ]

        time_features = [
            col
            for col in df.columns
            if any(keyword in col.lower() for keyword in time_keywords)
        ]

        return time_features


def main():
    """Example usage"""
    print("=" * 70)
    print("TIME FEATURES - TEST")
    print("=" * 70)

    # Load sample data
    from pathlib import Path

    data_file = Path("data/raw/XAUUSD_M15_20251101_172509.csv")

    if not data_file.exists():
        print(f"❌ Data file not found: {data_file}")
        print("Please run: python collect_all_timeframes.py")
        return

    # Load data
    print(f"\n📂 Loading data from: {data_file}")
    df = pd.read_csv(data_file)
    print(f"✅ Loaded {len(df)} bars")

    # Add time features
    tf = TimeFeatures()
    df_with_time = tf.add_all_time_features(df)

    # Show results
    print("\n" + "=" * 70)
    print("📊 RESULTS")
    print("=" * 70)
    print(f"Original columns: {len(df.columns)}")
    print(f"With time features: {len(df_with_time.columns)}")
    print(f"New features: {len(df_with_time.columns) - len(df.columns)}")

    # Show feature list
    time_features = tf.get_feature_list(df_with_time)
    print(f"\n⏰ Time Features ({len(time_features)}):")
    for i, feat in enumerate(time_features, 1):
        print(f"  {i:2d}. {feat}")

    # Save processed data
    output_dir = Path("data/processed")
    output_dir.mkdir(parents=True, exist_ok=True)

    output_file = output_dir / "XAUUSD_M15_with_time_features.csv"
    df_with_time.to_csv(output_file, index=False)

    print(f"\n💾 Saved to: {output_file}")
    print(f"   Rows: {len(df_with_time)}")
    print(f"   Columns: {len(df_with_time.columns)}")

    # Show sample
    print("\n📊 Sample data (last 5 rows, selected columns):")
    sample_cols = [
        "timestamp",
        "hour",
        "day_of_week",
        "session_london",
        "session_newyork",
        "is_peak_hours",
        "main_session",
    ]
    if all(col in df_with_time.columns for col in sample_cols):
        print(df_with_time[sample_cols].tail())

    print("\n✅ Time Features module ready!")


if __name__ == "__main__":
    main()
