"""
Data Collection Module
======================
Collects market data from various sources for the AI Gold Trading Bot.

Available collectors:
- MT5Collector: Collects price data from MetaTrader 5
- NewsCollector: Collects news and sentiment data (coming soon)
- EconomicDataCollector: Collects economic indicators (coming soon)
"""

from .mt5_collector import MT5Collector

__all__ = ["MT5Collector"]

__version__ = "0.1.0"
