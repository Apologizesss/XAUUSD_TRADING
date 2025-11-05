"""
Production-Ready Inference Pipeline
====================================
Real-time prediction and signal generation for live trading.

Features:
- Load trained model and scaler
- Fetch live data from MT5
- Generate advanced features
- Make predictions with confidence filtering
- Generate trading signals with entry/exit levels
- Risk management integration
- Logging and monitoring
"""

import sys
from pathlib import Path
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import warnings

warnings.filterwarnings("ignore")

# Add project root to path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

import joblib
import json
from typing import Dict, Optional, Tuple

# Import FeaturePipeline for consistent feature engineering
from src.features.feature_pipeline import FeaturePipeline


class TradingInference:
    """
    Production inference pipeline for trading signals
    """

    def __init__(
        self,
        model_path: str = "results/xgboost/xgboost_model.pkl",
        scaler_path: str = "results/xgboost/xgboost_scaler.pkl",
        confidence_threshold: float = 0.70,
        symbol: str = "XAUUSD",
        timeframe: str = "M5",
    ):
        """
        Initialize inference pipeline

        Args:
            model_path: Path to trained model
            scaler_path: Path to feature scaler
            confidence_threshold: Minimum confidence for signals (0.70 recommended)
            symbol: Trading symbol
            timeframe: Timeframe (H1, M15, etc.)
        """
        print("=" * 70)
        print("TRADING INFERENCE PIPELINE")
        print("=" * 70)
        print()

        self.model_path = model_path
        self.scaler_path = scaler_path
        self.confidence_threshold = confidence_threshold
        self.symbol = symbol
        self.timeframe = timeframe

        print(f"Symbol: {symbol}")
        print(f"Timeframe: {timeframe}")
        print(f"Confidence Threshold: {confidence_threshold:.2f}")
        print()

        # Load model and scaler
        print("Loading model and scaler...")
        self.model = joblib.load(model_path)
        self.scaler = joblib.load(scaler_path)
        print("  [OK] Model loaded")
        print("  [OK] Scaler loaded")

        # Load feature names used during training
        feature_names_path = Path(model_path).parent / "feature_names.txt"
        if feature_names_path.exists():
            with open(feature_names_path, "r") as f:
                self.training_features = [line.strip() for line in f if line.strip()]
            print(f"  [OK] Loaded {len(self.training_features)} training feature names")
        else:
            print(
                "  [WARNING] No feature_names.txt found - will use all numeric features"
            )
            self.training_features = None
        print()

        # Initialize feature pipeline for consistent features
        self.feature_pipeline = FeaturePipeline()

    def fetch_live_data(self, bars: int = 300) -> Optional[pd.DataFrame]:
        """
        Fetch live data from MT5

        Args:
            bars: Number of historical bars to fetch

        Returns:
            DataFrame with OHLCV data
        """
        try:
            import MetaTrader5 as mt5

            # Initialize MT5
            if not mt5.initialize():
                print(f"MT5 initialization failed: {mt5.last_error()}")
                return None

            # Get rates - use timeframe from initialization
            timeframe_map = {
                "M1": mt5.TIMEFRAME_M1,
                "M5": mt5.TIMEFRAME_M5,
                "M15": mt5.TIMEFRAME_M15,
                "M30": mt5.TIMEFRAME_M30,
                "H1": mt5.TIMEFRAME_H1,
                "H4": mt5.TIMEFRAME_H4,
                "D1": mt5.TIMEFRAME_D1,
            }
            mt5_timeframe = timeframe_map.get(self.timeframe, mt5.TIMEFRAME_M5)
            rates = mt5.copy_rates_from_pos(self.symbol, mt5_timeframe, 0, bars)

            if rates is None or len(rates) == 0:
                print(f"Failed to get rates: {mt5.last_error()}")
                mt5.shutdown()
                return None

            # Convert to DataFrame
            df = pd.DataFrame(rates)
            df["time"] = pd.to_datetime(df["time"], unit="s")

            mt5.shutdown()

            print(f"[OK] Fetched {len(df)} bars from MT5")
            print(f"  Latest: {df.iloc[-1]['time']}")
            return df

        except ImportError:
            print("ERROR: MetaTrader5 not installed!")
            print("Install with: pip install MetaTrader5")
            return None
        except Exception as e:
            print(f"ERROR fetching live data: {e}")
            return None

    def calculate_technical_indicators(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Calculate all features using FeaturePipeline (same as training)

        Args:
            df: DataFrame with OHLCV data

        Returns:
            DataFrame with added features
        """
        print("Calculating technical indicators...")

        # Make a copy
        df = df.copy()

        # Rename columns to match expected format
        if "time" in df.columns:
            df["timestamp"] = df["time"]

        # Ensure required columns exist
        required_cols = ["open", "high", "low", "close"]
        for col in required_cols:
            if col not in df.columns:
                print(f"ERROR: Missing required column: {col}")
                return None

        # Add volume if missing
        if "tick_volume" in df.columns:
            df["real_volume"] = df["tick_volume"]
        elif "real_volume" not in df.columns:
            df["real_volume"] = 0

        if "spread" not in df.columns:
            df["spread"] = 0

        # Use FeaturePipeline to generate all features (same as training)
        try:
            df_featured = self.feature_pipeline.add_features(df)
            df_featured = self.feature_pipeline.handle_missing_values(df_featured)

            num_features = len(
                [
                    col
                    for col in df_featured.columns
                    if col not in ["timestamp", "time", "symbol", "timeframe"]
                ]
            )
            print(f"  [OK] Calculated {num_features} features using FeaturePipeline")

            return df_featured
        except Exception as e:
            print(f"ERROR in feature calculation: {e}")
            import traceback

            traceback.print_exc()
            return None

    def prepare_features_for_prediction(self, df: pd.DataFrame) -> Optional[np.ndarray]:
        """
        Prepare features for model prediction

        Args:
            df: DataFrame with calculated features

        Returns:
            Feature array ready for prediction (latest bar only)
        """
        # Get all numeric columns except metadata and target
        # Keep OHLCV columns as they were used in training
        # Must match exactly 138 features from training data

        # First, get the expected training features
        training_file = Path(
            "data/processed/XAUUSD_M5_features_complete_target_trend_5.csv"
        )
        if training_file.exists():
            # Load training columns to match exactly
            # Now select features to match training
            if self.training_features is not None:
                # Use exact features from training
                feature_cols = self.training_features

                # Check for missing columns
                available_cols = [c for c in feature_cols if c in df.columns]
                missing_cols = [c for c in feature_cols if c not in df.columns]

                if missing_cols:
                    print(f"  WARNING: Missing {len(missing_cols)} training columns")
                    print(f"  First 5 missing: {missing_cols[:5]}")
                    # Fill missing columns with 0
                    for col in missing_cols:
                        df[col] = 0
                    available_cols = feature_cols

                feature_cols = available_cols
            else:
                # Fallback: exclude known metadata columns
                exclude_cols = [
                    "target",
                    "time",  # MT5 timestamp (numeric but not a feature)
                ]
                numeric_cols = df.select_dtypes(include=[np.number]).columns.tolist()
                feature_cols = [col for col in numeric_cols if col not in exclude_cols]

        if len(feature_cols) == 0:
            print("ERROR: No feature columns found!")
            return None

        # Get latest bar with exact features
        latest_row = df.iloc[-1]

        # Ensure features are in the same order as training
        try:
            features = latest_row[feature_cols].values
        except KeyError as e:
            print(f"  ERROR: Missing columns in data: {e}")
            return None

        # Handle NaN and inf
        features = np.nan_to_num(features, nan=0, posinf=0, neginf=0)

        print(f"  [OK] Extracted {len(features)} features")
        return features.reshape(1, -1)

    def make_prediction(self, features: np.ndarray) -> Tuple[float, int]:
        """
        Make prediction using trained model

        Args:
            features: Feature array

        Returns:
            (probability_up, predicted_class)
        """
        # Scale features
        features_scaled = self.scaler.transform(features)

        # Predict
        prob_up = self.model.predict_proba(features_scaled)[0][1]
        predicted_class = 1 if prob_up > 0.5 else 0

        return prob_up, predicted_class

    def generate_signal(
        self, df: pd.DataFrame, prob_up: float, atr_multiplier: float = 1.0
    ) -> Dict:
        """
        Generate trading signal with entry/exit levels

        Args:
            df: DataFrame with price data and features
            prob_up: Predicted probability of UP move
            atr_multiplier: ATR multiplier for SL/TP (1.0 = 50 pips, 2.0 = 100 pips)

        Returns:
            Signal dictionary
        """
        latest = df.iloc[-1]
        current_price = latest["close"]

        # Handle column name case variations (atr_14 vs ATR_14)
        atr = latest.get("ATR_14", latest.get("atr_14", 0.001))
        support = latest.get("support", current_price * 0.99)
        resistance = latest.get("resistance", current_price * 1.01)

        # Calculate distances to S/R
        dist_to_support = abs(current_price - support) / current_price * 100
        dist_to_resistance = abs(current_price - resistance) / current_price * 100

        # DEBUG: Print signal evaluation
        print(f"\n  🔍 Signal Evaluation:")
        print(f"    Prob UP: {prob_up:.4f} ({prob_up * 100:.2f}%)")
        print(f"    Prob DOWN: {1 - prob_up:.4f} ({(1 - prob_up) * 100:.2f}%)")
        print(f"    Threshold: {self.confidence_threshold:.2f}")
        print(f"    Current Price: {current_price:.2f}")

        # Default: No signal
        signal = {
            "timestamp": datetime.now().isoformat(),
            "symbol": self.symbol,
            "timeframe": self.timeframe,
            "current_price": float(current_price),
            "probability_up": float(prob_up),
            "direction": "NEUTRAL",
            "confidence": "NONE",
            "signal_strength": 0,
            "should_trade": False,
            "entry_price": None,
            "stop_loss": None,
            "take_profit": None,
            "risk_reward_ratio": None,
            "position_size_lots": None,
            "reason": "",
        }

        # LONG signal conditions - Simplified (model prediction only)
        if prob_up > self.confidence_threshold:
            print(
                f"    ✅ LONG Signal: {prob_up:.2%} > {self.confidence_threshold:.2%}"
            )
            signal["direction"] = "LONG"
            signal["should_trade"] = True
            signal["entry_price"] = float(current_price)
            signal["stop_loss"] = float(current_price - atr * atr_multiplier)
            signal["take_profit"] = float(current_price + atr * atr_multiplier * 2.0)
            signal["risk_reward_ratio"] = 2.0

            if prob_up > 0.80:
                signal["confidence"] = "VERY HIGH"
                signal["signal_strength"] = 5
            elif prob_up > 0.75:
                signal["confidence"] = "HIGH"
                signal["signal_strength"] = 4
            else:
                signal["confidence"] = "MEDIUM"
                signal["signal_strength"] = 3

            signal["reason"] = (
                f"Model prediction UP ({prob_up:.2%}), Support at {dist_to_support:.2f}%"
            )

        # SHORT signal conditions - Simplified (model prediction only)
        elif prob_up < (1 - self.confidence_threshold):
            print(
                f"    ✅ SHORT Signal: {prob_up:.2%} < {1 - self.confidence_threshold:.2%}"
            )
            signal["direction"] = "SHORT"
            signal["should_trade"] = True
            signal["entry_price"] = float(current_price)
            signal["stop_loss"] = float(current_price + atr * atr_multiplier)
            signal["take_profit"] = float(current_price - atr * atr_multiplier * 2.0)
            signal["risk_reward_ratio"] = 2.0

            if prob_up < 0.20:
                signal["confidence"] = "VERY HIGH"
                signal["signal_strength"] = 5
            elif prob_up < 0.25:
                signal["confidence"] = "HIGH"
                signal["signal_strength"] = 4
            else:
                signal["confidence"] = "MEDIUM"
                signal["signal_strength"] = 3

            signal["reason"] = (
                f"Model prediction DOWN ({1 - prob_up:.2%}), Resistance at {dist_to_resistance:.2f}%"
            )
        else:
            print(
                f"    ⚪ NO SIGNAL: {prob_up:.2%} is between {1 - self.confidence_threshold:.2%} and {self.confidence_threshold:.2%}"
            )

        # Add additional context
        signal["support_level"] = float(support)
        signal["resistance_level"] = float(resistance)
        signal["atr"] = float(atr)
        signal["dist_to_support_pct"] = float(dist_to_support)
        signal["dist_to_resistance_pct"] = float(dist_to_resistance)

        return signal

    def run_inference(
        self, use_live_data: bool = False, csv_path: Optional[str] = None
    ) -> Dict:
        """
        Run complete inference pipeline

        Args:
            use_live_data: If True, fetch live data from MT5
            csv_path: Path to CSV file if not using live data

        Returns:
            Complete signal dictionary
        """
        print("=" * 70)
        print("RUNNING INFERENCE")
        print("=" * 70)
        print()

        # Get data
        if use_live_data:
            print("Fetching live data from MT5...")
            df = self.fetch_live_data(bars=300)
        elif csv_path:
            print(f"Loading data from: {csv_path}")
            df = pd.read_csv(csv_path)
            if "timestamp" in df.columns:
                df["time"] = pd.to_datetime(df["timestamp"])
            else:
                df["time"] = pd.to_datetime(df["time"])
        else:
            print("ERROR: Must specify either use_live_data=True or csv_path")
            return None

        if df is None or len(df) == 0:
            print("ERROR: No data available")
            return None

        print()

        # Calculate features
        df = self.calculate_technical_indicators(df)
        if df is None:
            return None
        print()

        # Prepare features
        print("Preparing features for prediction...")
        features = self.prepare_features_for_prediction(df)
        if features is None:
            return None
        print("  [OK] Features ready")
        print()

        # Make prediction
        print("Making prediction...")
        prob_up, predicted_class = self.make_prediction(features)
        print(f"  Probability UP: {prob_up:.4f} ({prob_up * 100:.2f}%)")
        print(f"  Predicted: {'UP' if predicted_class == 1 else 'DOWN'}")
        print()

        # Generate signal
        print("Generating trading signal...")
        signal = self.generate_signal(df, prob_up)
        print()

        # Display signal
        self.display_signal(signal)

        return signal

    def display_signal(self, signal: Dict):
        """Display signal in readable format"""
        print("=" * 70)
        print("TRADING SIGNAL")
        print("=" * 70)
        print()

        print(f"Symbol:     {signal['symbol']}")
        print(f"Timeframe:  {signal['timeframe']}")
        print(f"Time:       {signal['timestamp']}")
        print(f"Price:      {signal['current_price']:.2f}")
        print()

        print(f"Probability UP:  {signal['probability_up']:.2%}")
        print(f"Direction:       {signal['direction']}")
        print(f"Confidence:      {signal['confidence']}")
        print(
            f"Signal Strength: {'★' * signal['signal_strength']}{'☆' * (5 - signal['signal_strength'])}"
        )
        print()

        if signal["should_trade"]:
            print("[OK] TRADE RECOMMENDATION:")
            print("-" * 70)
            print(f"Entry:       {signal['entry_price']:.2f}")
            print(f"Stop Loss:   {signal['stop_loss']:.2f}")
            print(f"Take Profit: {signal['take_profit']:.2f}")
            print(f"Risk/Reward: {signal['risk_reward_ratio']:.1f}:1")
            print()
            print(f"Reason: {signal['reason']}")
        else:
            print("[X] NO TRADE - Conditions not met")
            print(
                f"  Support: {signal['support_level']:.2f} ({signal['dist_to_support_pct']:.2f}% away)"
            )
            print(
                f"  Resistance: {signal['resistance_level']:.2f} ({signal['dist_to_resistance_pct']:.2f}% away)"
            )

        print()
        print("=" * 70)

    def save_signal(
        self, signal: Dict, output_path: str = "signals/latest_signal.json"
    ):
        """Save signal to file"""
        output_path = Path(output_path)
        output_path.parent.mkdir(parents=True, exist_ok=True)

        with open(output_path, "w") as f:
            json.dump(signal, f, indent=2)

        print(f"Signal saved to: {output_path}")


def main():
    """Run inference from command line"""
    import argparse

    parser = argparse.ArgumentParser(description="Run trading inference")
    parser.add_argument("--live", action="store_true", help="Use live MT5 data")
    parser.add_argument("--csv", type=str, help="Path to CSV file")
    parser.add_argument(
        "--model", type=str, default="results/xgboost/xgboost_model.pkl"
    )
    parser.add_argument(
        "--scaler", type=str, default="results/xgboost/xgboost_scaler.pkl"
    )
    parser.add_argument(
        "--confidence", type=float, default=0.70, help="Confidence threshold"
    )
    parser.add_argument("--symbol", type=str, default="XAUUSD")
    parser.add_argument("--timeframe", type=str, default="H1")
    parser.add_argument("--save", action="store_true", help="Save signal to file")

    args = parser.parse_args()

    # Create inference pipeline
    pipeline = TradingInference(
        model_path=args.model,
        scaler_path=args.scaler,
        confidence_threshold=args.confidence,
        symbol=args.symbol,
        timeframe=args.timeframe,
    )

    # Run inference
    signal = pipeline.run_inference(use_live_data=args.live, csv_path=args.csv)

    if signal and args.save:
        pipeline.save_signal(signal)


if __name__ == "__main__":
    main()
