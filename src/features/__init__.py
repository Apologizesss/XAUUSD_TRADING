"""
Feature Engineering Module
===========================
Feature engineering components for the AI Gold Trading Bot.

This module provides tools for extracting and engineering features from
raw market data for machine learning models.

Available Components:
- TechnicalIndicators: 88+ technical indicators (SMA, RSI, MACD, BB, etc.)
- TimeFeatures: 45+ time-based features (sessions, cyclical encoding, etc.)
- FeaturePipeline: Complete pipeline combining all feature modules

Usage:
    from src.features import FeaturePipeline

    pipeline = FeaturePipeline()
    df_processed = pipeline.process_file('data/raw/XAUUSD_M15.csv')

Feature Categories:
- Trend Indicators: Moving averages, MACD, ADX, Parabolic SAR
- Momentum Indicators: RSI, Stochastic, Williams %R, ROC, CCI
- Volatility Indicators: Bollinger Bands, ATR, Keltner, Donchian
- Volume Indicators: OBV, MFI, VWAP, Volume ratios
- Candlestick Patterns: Doji, Hammer, Engulfing, etc.
- Price Action: Body size, shadows, support/resistance
- Time Features: Hour, day, sessions, cyclical encoding
- Statistical Features: Returns, volatility, skewness, kurtosis
"""

from .technical_indicators import TechnicalIndicators
from .time_features import TimeFeatures
from .feature_pipeline import FeaturePipeline

__all__ = [
    "TechnicalIndicators",
    "TimeFeatures",
    "FeaturePipeline",
]

__version__ = "1.0.0"
__author__ = "AI Gold Trading Bot Team"
