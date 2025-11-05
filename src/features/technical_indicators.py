"""
Technical Indicators Module
============================
Calculates 40+ technical indicators using TA-Lib.

Categories:
- Trend Indicators (SMA, EMA, MACD, ADX, etc.)
- Momentum Indicators (RSI, Stochastic, Williams %R, etc.)
- Volatility Indicators (Bollinger Bands, ATR, Keltner, etc.)
- Volume Indicators (OBV, MFI, VWAP, etc.)

Usage:
    from src.features.technical_indicators import TechnicalIndicators

    ti = TechnicalIndicators()
    df = ti.add_all_indicators(df)
"""

import pandas as pd
import numpy as np
import talib
from typing import Optional
import warnings

warnings.filterwarnings("ignore")


class TechnicalIndicators:
    """Calculates technical indicators for trading"""

    def __init__(self):
        """Initialize Technical Indicators calculator"""
        self.required_columns = ["open", "high", "low", "close", "tick_volume"]

    def validate_data(self, df: pd.DataFrame) -> bool:
        """
        Validate that DataFrame has required columns

        Args:
            df: Input DataFrame

        Returns:
            bool: True if valid, False otherwise
        """
        missing = [col for col in self.required_columns if col not in df.columns]

        if missing:
            print(f"[Error] Missing required columns: {missing}")
            return False

        return True

    # ========================================================================
    # TREND INDICATORS
    # ========================================================================

    def add_moving_averages(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Add Simple and Exponential Moving Averages

        Periods: 5, 10, 20, 50, 100, 200
        """
        print("  ├─ Moving Averages (SMA, EMA)...")

        periods = [5, 10, 20, 50, 100, 200]

        for period in periods:
            # Simple Moving Average
            df[f"SMA_{period}"] = talib.SMA(df["close"], timeperiod=period)

            # Exponential Moving Average
            df[f"EMA_{period}"] = talib.EMA(df["close"], timeperiod=period)

        # Weighted Moving Average (shorter periods)
        for period in [10, 20, 50]:
            df[f"WMA_{period}"] = talib.WMA(df["close"], timeperiod=period)

        return df

    def add_macd(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Add MACD (Moving Average Convergence Divergence)

        Returns: MACD line, Signal line, Histogram
        """
        print("  ├─ MACD...")

        macd, signal, hist = talib.MACD(
            df["close"], fastperiod=12, slowperiod=26, signalperiod=9
        )

        df["MACD"] = macd
        df["MACD_signal"] = signal
        df["MACD_hist"] = hist

        return df

    def add_adx(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Add ADX (Average Directional Index)

        Measures trend strength
        """
        print("  ├─ ADX...")

        df["ADX"] = talib.ADX(df["high"], df["low"], df["close"], timeperiod=14)
        df["ADX_plus"] = talib.PLUS_DI(
            df["high"], df["low"], df["close"], timeperiod=14
        )
        df["ADX_minus"] = talib.MINUS_DI(
            df["high"], df["low"], df["close"], timeperiod=14
        )

        return df

    def add_parabolic_sar(self, df: pd.DataFrame) -> pd.DataFrame:
        """Add Parabolic SAR (Stop and Reverse)"""
        print("  ├─ Parabolic SAR...")

        df["SAR"] = talib.SAR(df["high"], df["low"], acceleration=0.02, maximum=0.2)

        return df

    # ========================================================================
    # MOMENTUM INDICATORS
    # ========================================================================

    def add_rsi(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Add RSI (Relative Strength Index)

        Periods: 14, 21, 28
        """
        print("  ├─ RSI...")

        periods = [14, 21, 28]

        for period in periods:
            df[f"RSI_{period}"] = talib.RSI(df["close"], timeperiod=period)

        return df

    def add_stochastic(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Add Stochastic Oscillator

        Returns: %K and %D lines
        """
        print("  ├─ Stochastic...")

        slowk, slowd = talib.STOCH(
            df["high"],
            df["low"],
            df["close"],
            fastk_period=14,
            slowk_period=3,
            slowk_matype=0,
            slowd_period=3,
            slowd_matype=0,
        )

        df["STOCH_K"] = slowk
        df["STOCH_D"] = slowd

        return df

    def add_williams_r(self, df: pd.DataFrame) -> pd.DataFrame:
        """Add Williams %R"""
        print("  ├─ Williams %R...")

        df["WILLR"] = talib.WILLR(df["high"], df["low"], df["close"], timeperiod=14)

        return df

    def add_roc(self, df: pd.DataFrame) -> pd.DataFrame:
        """Add Rate of Change (ROC)"""
        print("  ├─ ROC...")

        periods = [10, 20, 50]

        for period in periods:
            df[f"ROC_{period}"] = talib.ROC(df["close"], timeperiod=period)

        return df

    def add_momentum(self, df: pd.DataFrame) -> pd.DataFrame:
        """Add Momentum indicator"""
        print("  ├─ Momentum...")

        df["MOM"] = talib.MOM(df["close"], timeperiod=10)

        return df

    def add_cci(self, df: pd.DataFrame) -> pd.DataFrame:
        """Add Commodity Channel Index (CCI)"""
        print("  ├─ CCI...")

        df["CCI"] = talib.CCI(df["high"], df["low"], df["close"], timeperiod=14)

        return df

    # ========================================================================
    # VOLATILITY INDICATORS
    # ========================================================================

    def add_bollinger_bands(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Add Bollinger Bands

        Returns: Upper, Middle, Lower bands + %B and Bandwidth
        """
        print("  ├─ Bollinger Bands...")

        upper, middle, lower = talib.BBANDS(
            df["close"], timeperiod=20, nbdevup=2, nbdevdn=2, matype=0
        )

        df["BB_upper"] = upper
        df["BB_middle"] = middle
        df["BB_lower"] = lower

        # Bollinger Band %B (position within bands)
        df["BB_pct_b"] = (df["close"] - lower) / (upper - lower)

        # Bollinger Band Width (volatility measure)
        df["BB_width"] = (upper - lower) / middle

        return df

    def add_atr(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Add ATR (Average True Range)

        Periods: 14, 21
        """
        print("  ├─ ATR...")

        periods = [14, 21]

        for period in periods:
            df[f"ATR_{period}"] = talib.ATR(
                df["high"], df["low"], df["close"], timeperiod=period
            )

        # Normalized ATR (as % of price)
        df["ATR_pct"] = df["ATR_14"] / df["close"] * 100

        return df

    def add_keltner_channels(self, df: pd.DataFrame) -> pd.DataFrame:
        """Add Keltner Channels (EMA ± ATR)"""
        print("  ├─ Keltner Channels...")

        ema_20 = talib.EMA(df["close"], timeperiod=20)
        atr_10 = talib.ATR(df["high"], df["low"], df["close"], timeperiod=10)

        df["KELT_upper"] = ema_20 + (2 * atr_10)
        df["KELT_middle"] = ema_20
        df["KELT_lower"] = ema_20 - (2 * atr_10)

        return df

    def add_donchian_channels(self, df: pd.DataFrame) -> pd.DataFrame:
        """Add Donchian Channels (Highest high, Lowest low)"""
        print("  ├─ Donchian Channels...")

        period = 20

        df["DONCH_upper"] = df["high"].rolling(window=period).max()
        df["DONCH_lower"] = df["low"].rolling(window=period).min()
        df["DONCH_middle"] = (df["DONCH_upper"] + df["DONCH_lower"]) / 2

        return df

    # ========================================================================
    # VOLUME INDICATORS
    # ========================================================================

    def add_volume_indicators(self, df: pd.DataFrame) -> pd.DataFrame:
        """Add volume-based indicators"""
        print("  ├─ Volume Indicators...")

        # Volume Moving Averages
        df["VOL_SMA_10"] = df["tick_volume"].rolling(window=10).mean()
        df["VOL_SMA_20"] = df["tick_volume"].rolling(window=20).mean()
        df["VOL_SMA_50"] = df["tick_volume"].rolling(window=50).mean()

        # Volume Ratio (current vs average)
        df["VOL_ratio"] = df["tick_volume"] / df["VOL_SMA_20"]

        return df

    def add_obv(self, df: pd.DataFrame) -> pd.DataFrame:
        """Add On-Balance Volume (OBV)"""
        print("  ├─ OBV...")

        df["OBV"] = talib.OBV(df["close"], df["tick_volume"])

        # OBV Moving Average
        df["OBV_SMA"] = df["OBV"].rolling(window=20).mean()

        return df

    def add_mfi(self, df: pd.DataFrame) -> pd.DataFrame:
        """Add Money Flow Index (MFI)"""
        print("  ├─ MFI...")

        df["MFI"] = talib.MFI(
            df["high"], df["low"], df["close"], df["tick_volume"], timeperiod=14
        )

        return df

    def add_vwap(self, df: pd.DataFrame) -> pd.DataFrame:
        """Add Volume Weighted Average Price (VWAP)"""
        print("  ├─ VWAP...")

        typical_price = (df["high"] + df["low"] + df["close"]) / 3

        # VWAP for each day
        if "timestamp" in df.columns:
            df["date"] = pd.to_datetime(df["timestamp"]).dt.date
            df["VWAP"] = (
                df.groupby("date")
                .apply(
                    lambda x: (
                        x["tick_volume"] * (x["high"] + x["low"] + x["close"]) / 3
                    ).cumsum()
                    / x["tick_volume"].cumsum()
                )
                .reset_index(level=0, drop=True)
            )
            df.drop("date", axis=1, inplace=True)
        else:
            # Simple VWAP without date grouping
            df["VWAP"] = (df["tick_volume"] * typical_price).cumsum() / df[
                "tick_volume"
            ].cumsum()

        return df

    # ========================================================================
    # PATTERN RECOGNITION
    # ========================================================================

    def add_candlestick_patterns(self, df: pd.DataFrame) -> pd.DataFrame:
        """Add candlestick pattern recognition"""
        print("  ├─ Candlestick Patterns...")

        patterns = {
            "DOJI": talib.CDLDOJI,
            "HAMMER": talib.CDLHAMMER,
            "INVERTED_HAMMER": talib.CDLINVERTEDHAMMER,
            "SHOOTING_STAR": talib.CDLSHOOTINGSTAR,
            "ENGULFING": talib.CDLENGULFING,
            "HARAMI": talib.CDLHARAMI,
            "MORNING_STAR": talib.CDLMORNINGSTAR,
            "EVENING_STAR": talib.CDLEVENINGSTAR,
            "THREE_WHITE_SOLDIERS": talib.CDL3WHITESOLDIERS,
            "THREE_BLACK_CROWS": talib.CDL3BLACKCROWS,
        }

        for name, func in patterns.items():
            df[f"PATTERN_{name}"] = func(df["open"], df["high"], df["low"], df["close"])

        return df

    # ========================================================================
    # PRICE ACTION
    # ========================================================================

    def add_price_action(self, df: pd.DataFrame) -> pd.DataFrame:
        """Add price action indicators"""
        print("  ├─ Price Action...")

        # High-Low Range
        df["HL_range"] = df["high"] - df["low"]
        df["HL_range_pct"] = (df["HL_range"] / df["close"]) * 100

        # Body size (open-close)
        df["body_size"] = abs(df["close"] - df["open"])
        df["body_size_pct"] = (df["body_size"] / df["close"]) * 100

        # Upper/Lower shadows
        df["upper_shadow"] = df["high"] - df[["open", "close"]].max(axis=1)
        df["lower_shadow"] = df[["open", "close"]].min(axis=1) - df["low"]

        # Bullish/Bearish candle
        df["is_bullish"] = (df["close"] > df["open"]).astype(int)

        return df

    # ========================================================================
    # SUPPORT & RESISTANCE
    # ========================================================================

    def add_support_resistance(
        self, df: pd.DataFrame, window: int = 20
    ) -> pd.DataFrame:
        """Add support and resistance levels"""
        print("  ├─ Support & Resistance...")

        # Rolling high/low (resistance/support)
        df["resistance"] = df["high"].rolling(window=window).max()
        df["support"] = df["low"].rolling(window=window).min()

        # Distance to support/resistance
        df["dist_to_resistance"] = (df["resistance"] - df["close"]) / df["close"] * 100
        df["dist_to_support"] = (df["close"] - df["support"]) / df["close"] * 100

        return df

    # ========================================================================
    # STATISTICAL INDICATORS
    # ========================================================================

    def add_statistical_indicators(self, df: pd.DataFrame) -> pd.DataFrame:
        """Add statistical indicators"""
        print("  ├─ Statistical Indicators...")

        # Returns
        df["returns"] = df["close"].pct_change()
        df["log_returns"] = np.log(df["close"] / df["close"].shift(1))

        # Rolling statistics
        for window in [10, 20, 50]:
            df[f"volatility_{window}"] = df["returns"].rolling(window=window).std()
            df[f"skew_{window}"] = df["returns"].rolling(window=window).skew()
            df[f"kurt_{window}"] = df["returns"].rolling(window=window).kurt()

        # Z-score (price deviation from mean)
        df["zscore_20"] = (df["close"] - df["close"].rolling(20).mean()) / df[
            "close"
        ].rolling(20).std()

        return df

    # ========================================================================
    # MAIN FUNCTION
    # ========================================================================

    def add_all_indicators(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Add all technical indicators to DataFrame

        Args:
            df: Input DataFrame with OHLCV data

        Returns:
            DataFrame with added indicators
        """
        print("\n[Stats] Adding Technical Indicators...")
        print("=" * 70)

        # Validate data
        if not self.validate_data(df):
            return df

        # Make a copy
        df = df.copy()

        # Add all indicator groups
        try:
            # Trend
            df = self.add_moving_averages(df)
            df = self.add_macd(df)
            df = self.add_adx(df)
            df = self.add_parabolic_sar(df)

            # Momentum
            df = self.add_rsi(df)
            df = self.add_stochastic(df)
            df = self.add_williams_r(df)
            df = self.add_roc(df)
            df = self.add_momentum(df)
            df = self.add_cci(df)

            # Volatility
            df = self.add_bollinger_bands(df)
            df = self.add_atr(df)
            df = self.add_keltner_channels(df)
            df = self.add_donchian_channels(df)

            # Volume
            df = self.add_volume_indicators(df)
            df = self.add_obv(df)
            df = self.add_mfi(df)
            df = self.add_vwap(df)

            # Patterns
            df = self.add_candlestick_patterns(df)

            # Price Action
            df = self.add_price_action(df)
            df = self.add_support_resistance(df)

            # Statistical
            df = self.add_statistical_indicators(df)

            print("  └─ [OK] All indicators added!")

            # Count features
            feature_cols = [
                col
                for col in df.columns
                if col
                not in self.required_columns
                + ["timestamp", "symbol", "timeframe", "spread", "real_volume"]
            ]
            print(f"\n[Chart] Total features created: {len(feature_cols)}")

        except Exception as e:
            print(f"\n[Error] Error adding indicators: {e}")
            import traceback

            traceback.print_exc()

        return df

    def get_feature_groups(self, df: pd.DataFrame) -> dict:
        """
        Get features organized by category

        Returns:
            dict: Feature names organized by category
        """
        features = {
            "trend": [
                col
                for col in df.columns
                if any(x in col for x in ["SMA", "EMA", "WMA", "MACD", "ADX", "SAR"])
            ],
            "momentum": [
                col
                for col in df.columns
                if any(x in col for x in ["RSI", "STOCH", "WILLR", "ROC", "MOM", "CCI"])
            ],
            "volatility": [
                col
                for col in df.columns
                if any(x in col for x in ["BB_", "ATR", "KELT", "DONCH", "volatility"])
            ],
            "volume": [
                col
                for col in df.columns
                if any(x in col for x in ["VOL_", "OBV", "MFI", "VWAP"])
            ],
            "patterns": [col for col in df.columns if "PATTERN_" in col],
            "price_action": [
                col
                for col in df.columns
                if any(
                    x in col
                    for x in [
                        "HL_range",
                        "body_size",
                        "shadow",
                        "is_bullish",
                        "resistance",
                        "support",
                        "dist_to",
                    ]
                )
            ],
            "statistical": [
                col
                for col in df.columns
                if any(x in col for x in ["returns", "skew", "kurt", "zscore"])
            ],
        }

        return features


def main():
    """Example usage"""
    print("=" * 70)
    print("TECHNICAL INDICATORS - TEST")
    print("=" * 70)

    # Load sample data
    import sys
    from pathlib import Path

    data_file = Path("data/raw/XAUUSD_M15_20251101_172509.csv")

    if not data_file.exists():
        print(f"[Error] Data file not found: {data_file}")
        print("Please run: python collect_all_timeframes.py")
        return

    # Load data
    print(f"\n📂 Loading data from: {data_file}")
    df = pd.read_csv(data_file)
    print(f"[OK] Loaded {len(df)} bars")

    # Add indicators
    ti = TechnicalIndicators()
    df_features = ti.add_all_indicators(df)

    # Show results
    print("\n" + "=" * 70)
    print("[Stats] RESULTS")
    print("=" * 70)
    print(f"Original columns: {len(df.columns)}")
    print(f"With features: {len(df_features.columns)}")
    print(f"New features: {len(df_features.columns) - len(df.columns)}")

    # Show feature groups
    print("\n📋 Feature Groups:")
    feature_groups = ti.get_feature_groups(df_features)
    for group, features in feature_groups.items():
        print(f"  {group.title():15s}: {len(features)} features")

    # Save processed data
    output_dir = Path("data/processed")
    output_dir.mkdir(parents=True, exist_ok=True)

    output_file = output_dir / "XAUUSD_M15_with_features.csv"
    df_features.to_csv(output_file, index=False)

    print(f"\n[Save] Saved to: {output_file}")
    print(f"   Rows: {len(df_features)}")
    print(f"   Columns: {len(df_features.columns)}")

    # Show sample
    print("\n[Stats] Sample data (last 5 rows, selected columns):")
    sample_cols = ["timestamp", "close", "RSI_14", "MACD", "BB_pct_b", "ATR_14"]
    print(df_features[sample_cols].tail())

    print("\n[OK] Technical Indicators module ready!")


if __name__ == "__main__":
    main()
