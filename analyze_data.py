"""
Exploratory Data Analysis (EDA) for Gold Trading Data
======================================================
Analyzes collected XAUUSD data across multiple timeframes.

Features:
- Basic statistics and data quality checks
- Price distribution analysis
- Volatility analysis
- Time series visualization
- Correlation analysis
- Trading session analysis
- Trend detection
"""

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from pathlib import Path
from datetime import datetime
import warnings

warnings.filterwarnings("ignore")

# Set style
plt.style.use("seaborn-v0_8-darkgrid")
sns.set_palette("husl")


class GoldDataAnalyzer:
    """Analyzes gold price data"""

    def __init__(self, data_dir="data/raw", output_dir="results/eda"):
        self.data_dir = Path(data_dir)
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)

        self.data = {}
        self.timeframes = ["M5", "M15", "M30", "H1", "H4", "D1"]

    def load_data(self):
        """Load all timeframe data"""
        print("=" * 70)
        print("📂 LOADING DATA")
        print("=" * 70)
        print()

        for tf in self.timeframes:
            # Find most recent file for this timeframe
            files = list(self.data_dir.glob(f"XAUUSD_{tf}_*.csv"))

            if files:
                # Get most recent file
                latest_file = max(files, key=lambda f: f.stat().st_mtime)

                df = pd.read_csv(latest_file)
                df["timestamp"] = pd.to_datetime(df["timestamp"])
                df = df.sort_values("timestamp")

                self.data[tf] = df

                print(f"✅ {tf:4s}: {len(df):,} bars | {latest_file.name}")
            else:
                print(f"❌ {tf:4s}: No data found")

        print()
        print(f"📊 Loaded {len(self.data)} timeframes")
        print()

    def basic_statistics(self):
        """Print basic statistics for each timeframe"""
        print("=" * 70)
        print("📊 BASIC STATISTICS")
        print("=" * 70)
        print()

        for tf, df in self.data.items():
            print(f"{'─' * 70}")
            print(f"⏱️  {tf} Timeframe")
            print(f"{'─' * 70}")
            print(f"Total bars:       {len(df):,}")
            print(
                f"Date range:       {df['timestamp'].min()} to {df['timestamp'].max()}"
            )
            print(
                f"Duration:         {(df['timestamp'].max() - df['timestamp'].min()).days} days"
            )
            print()

            print("Price Statistics:")
            print(f"  Min:            ${df['low'].min():.2f}")
            print(f"  Max:            ${df['high'].max():.2f}")
            print(f"  Mean:           ${df['close'].mean():.2f}")
            print(f"  Median:         ${df['close'].median():.2f}")
            print(f"  Std Dev:        ${df['close'].std():.2f}")
            print()

            # Calculate returns
            df["returns"] = df["close"].pct_change()

            print("Returns Statistics:")
            print(f"  Mean:           {df['returns'].mean() * 100:.4f}%")
            print(f"  Std Dev:        {df['returns'].std() * 100:.4f}%")
            print(f"  Max Gain:       {df['returns'].max() * 100:.2f}%")
            print(f"  Max Loss:       {df['returns'].min() * 100:.2f}%")
            print()

            print("Volume Statistics:")
            print(f"  Mean Tick Vol:  {df['tick_volume'].mean():.0f}")
            print(f"  Mean Spread:    {df['spread'].mean():.2f}")
            print()

            # Missing values
            missing = df.isnull().sum()
            if missing.any():
                print("⚠️  Missing Values:")
                print(missing[missing > 0])
            else:
                print("✅ No missing values")

            print()

    def volatility_analysis(self):
        """Analyze volatility across timeframes"""
        print("=" * 70)
        print("📈 VOLATILITY ANALYSIS")
        print("=" * 70)
        print()

        volatility_data = []

        for tf, df in self.data.items():
            df["returns"] = df["close"].pct_change()
            df["hl_range"] = (df["high"] - df["low"]) / df["close"] * 100

            vol_daily = df["returns"].std() * np.sqrt(
                len(df) / ((df["timestamp"].max() - df["timestamp"].min()).days)
            )

            volatility_data.append(
                {
                    "Timeframe": tf,
                    "Return Std (%)": df["returns"].std() * 100,
                    "Annualized Vol (%)": vol_daily * 100,
                    "Avg HL Range (%)": df["hl_range"].mean(),
                    "Max HL Range (%)": df["hl_range"].max(),
                }
            )

            print(f"{tf:4s}:")
            print(f"  Period Return Std:    {df['returns'].std() * 100:.4f}%")
            print(f"  Avg HL Range:         {df['hl_range'].mean():.3f}%")
            print(f"  Max HL Range:         {df['hl_range'].max():.3f}%")
            print()

        vol_df = pd.DataFrame(volatility_data)
        print("Volatility Comparison:")
        print(vol_df.to_string(index=False))
        print()

    def price_distribution(self):
        """Analyze price distribution"""
        print("=" * 70)
        print("📊 PRICE DISTRIBUTION ANALYSIS")
        print("=" * 70)
        print()

        # Use daily data for distribution
        if "D1" in self.data:
            df = self.data["D1"].copy()

            print(f"Analyzing D1 (Daily) data: {len(df)} days")
            print()

            # Price statistics
            print("Price Quartiles:")
            print(f"  25th percentile: ${df['close'].quantile(0.25):.2f}")
            print(f"  50th percentile: ${df['close'].quantile(0.50):.2f}")
            print(f"  75th percentile: ${df['close'].quantile(0.75):.2f}")
            print()

            # Returns distribution
            df["returns"] = df["close"].pct_change()

            print("Returns Distribution:")
            print(f"  Skewness:        {df['returns'].skew():.4f}")
            print(f"  Kurtosis:        {df['returns'].kurtosis():.4f}")
            print()

            # Normal distribution test
            if df["returns"].skew() > 0:
                print("  📈 Returns are positively skewed (right tail)")
            else:
                print("  📉 Returns are negatively skewed (left tail)")

            if df["returns"].kurtosis() > 0:
                print("  📊 Returns have fat tails (leptokurtic)")
            else:
                print("  📊 Returns have thin tails (platykurtic)")

            print()

    def trend_analysis(self):
        """Analyze price trends"""
        print("=" * 70)
        print("📈 TREND ANALYSIS")
        print("=" * 70)
        print()

        for tf, df in self.data.items():
            df = df.copy()

            # Calculate moving averages
            if len(df) >= 200:
                df["SMA_50"] = df["close"].rolling(50).mean()
                df["SMA_200"] = df["close"].rolling(200).mean()

                latest = df.iloc[-1]

                print(f"{tf} Timeframe:")
                print(f"  Current Price:   ${latest['close']:.2f}")
                print(f"  SMA 50:          ${latest['SMA_50']:.2f}")
                print(f"  SMA 200:         ${latest['SMA_200']:.2f}")

                # Trend identification
                if pd.notna(latest["SMA_50"]) and pd.notna(latest["SMA_200"]):
                    if latest["SMA_50"] > latest["SMA_200"]:
                        print(f"  Trend:           🟢 Bullish (Golden Cross)")
                    else:
                        print(f"  Trend:           🔴 Bearish (Death Cross)")

                # Price vs SMA
                if pd.notna(latest["SMA_50"]):
                    if latest["close"] > latest["SMA_50"]:
                        print(f"  Position:        Above SMA 50")
                    else:
                        print(f"  Position:        Below SMA 50")

                print()

    def session_analysis(self):
        """Analyze trading sessions"""
        print("=" * 70)
        print("🌏 TRADING SESSION ANALYSIS")
        print("=" * 70)
        print()

        # Use 15-minute data for session analysis
        if "M15" in self.data:
            df = self.data["M15"].copy()

            # Extract hour
            df["hour"] = df["timestamp"].dt.hour
            df["returns"] = df["close"].pct_change()
            df["hl_range"] = (df["high"] - df["low"]) / df["close"] * 100

            # Define sessions (UTC time)
            def get_session(hour):
                if 0 <= hour < 8:
                    return "Asian"
                elif 8 <= hour < 16:
                    return "European"
                elif 16 <= hour < 24:
                    return "US"
                return "Other"

            df["session"] = df["hour"].apply(get_session)

            # Session statistics
            session_stats = df.groupby("session").agg(
                {"returns": ["mean", "std"], "hl_range": "mean", "tick_volume": "mean"}
            )

            print("Session Comparison:")
            print()

            for session in ["Asian", "European", "US"]:
                if session in session_stats.index:
                    stats = session_stats.loc[session]
                    print(f"{session} Session:")
                    print(f"  Avg Return:      {stats['returns']['mean'] * 100:.4f}%")
                    print(f"  Return Std:      {stats['returns']['std'] * 100:.4f}%")
                    print(f"  Avg HL Range:    {stats['hl_range']['mean']:.3f}%")
                    print(f"  Avg Volume:      {stats['tick_volume']['mean']:.0f}")
                    print()

            # Most active hours
            hourly = (
                df.groupby("hour")
                .agg({"tick_volume": "mean", "hl_range": "mean"})
                .sort_values("tick_volume", ascending=False)
            )

            print("Most Active Hours (by volume):")
            for idx, row in hourly.head(5).iterrows():
                print(
                    f"  {idx:02d}:00 - Volume: {row['tick_volume']:.0f}, Range: {row['hl_range']:.3f}%"
                )

            print()

    def create_visualizations(self):
        """Create visualization charts"""
        print("=" * 70)
        print("📊 CREATING VISUALIZATIONS")
        print("=" * 70)
        print()

        # 1. Price Chart (Daily)
        if "D1" in self.data:
            fig, ax = plt.subplots(figsize=(15, 6))
            df = self.data["D1"].copy()

            ax.plot(df["timestamp"], df["close"], label="Close Price", linewidth=2)

            if len(df) >= 50:
                df["SMA_50"] = df["close"].rolling(50).mean()
                ax.plot(df["timestamp"], df["SMA_50"], label="SMA 50", alpha=0.7)

            ax.set_title(
                "Gold (XAUUSD) Price - Daily Chart", fontsize=16, fontweight="bold"
            )
            ax.set_xlabel("Date", fontsize=12)
            ax.set_ylabel("Price (USD)", fontsize=12)
            ax.legend()
            ax.grid(True, alpha=0.3)
            plt.tight_layout()

            filepath = self.output_dir / "price_chart_daily.png"
            plt.savefig(filepath, dpi=300, bbox_inches="tight")
            plt.close()
            print(f"✅ Saved: {filepath}")

        # 2. Returns Distribution
        if "D1" in self.data:
            fig, ax = plt.subplots(figsize=(12, 6))
            df = self.data["D1"].copy()
            df["returns"] = df["close"].pct_change() * 100

            ax.hist(df["returns"].dropna(), bins=50, edgecolor="black", alpha=0.7)
            ax.set_title("Daily Returns Distribution", fontsize=16, fontweight="bold")
            ax.set_xlabel("Returns (%)", fontsize=12)
            ax.set_ylabel("Frequency", fontsize=12)
            ax.axvline(0, color="red", linestyle="--", linewidth=2, alpha=0.7)
            ax.grid(True, alpha=0.3)
            plt.tight_layout()

            filepath = self.output_dir / "returns_distribution.png"
            plt.savefig(filepath, dpi=300, bbox_inches="tight")
            plt.close()
            print(f"✅ Saved: {filepath}")

        # 3. Volatility by Timeframe
        fig, ax = plt.subplots(figsize=(10, 6))

        volatility = []
        labels = []

        for tf in ["M5", "M15", "M30", "H1", "H4", "D1"]:
            if tf in self.data:
                df = self.data[tf].copy()
                df["returns"] = df["close"].pct_change()
                vol = df["returns"].std() * 100
                volatility.append(vol)
                labels.append(tf)

        ax.bar(labels, volatility, color="skyblue", edgecolor="black")
        ax.set_title("Volatility Across Timeframes", fontsize=16, fontweight="bold")
        ax.set_xlabel("Timeframe", fontsize=12)
        ax.set_ylabel("Return Std Dev (%)", fontsize=12)
        ax.grid(True, alpha=0.3, axis="y")
        plt.tight_layout()

        filepath = self.output_dir / "volatility_by_timeframe.png"
        plt.savefig(filepath, dpi=300, bbox_inches="tight")
        plt.close()
        print(f"✅ Saved: {filepath}")

        # 4. Volume Analysis
        if "M15" in self.data:
            fig, ax = plt.subplots(figsize=(12, 6))
            df = self.data["M15"].copy()
            df["hour"] = df["timestamp"].dt.hour

            hourly_vol = df.groupby("hour")["tick_volume"].mean()

            ax.bar(
                hourly_vol.index, hourly_vol.values, color="coral", edgecolor="black"
            )
            ax.set_title("Average Volume by Hour (M15)", fontsize=16, fontweight="bold")
            ax.set_xlabel("Hour (UTC)", fontsize=12)
            ax.set_ylabel("Average Tick Volume", fontsize=12)
            ax.set_xticks(range(0, 24, 2))
            ax.grid(True, alpha=0.3, axis="y")
            plt.tight_layout()

            filepath = self.output_dir / "volume_by_hour.png"
            plt.savefig(filepath, dpi=300, bbox_inches="tight")
            plt.close()
            print(f"✅ Saved: {filepath}")

        print()
        print(f"📁 All charts saved to: {self.output_dir}/")
        print()

    def generate_summary_report(self):
        """Generate text summary report"""
        print("=" * 70)
        print("📝 GENERATING SUMMARY REPORT")
        print("=" * 70)
        print()

        report_path = self.output_dir / "eda_summary_report.txt"

        with open(report_path, "w", encoding="utf-8") as f:
            f.write("=" * 70 + "\n")
            f.write("GOLD (XAUUSD) DATA - EXPLORATORY ANALYSIS REPORT\n")
            f.write("=" * 70 + "\n")
            f.write(f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
            f.write("\n")

            f.write("DATASET SUMMARY\n")
            f.write("-" * 70 + "\n")

            for tf, df in self.data.items():
                f.write(f"\n{tf} Timeframe:\n")
                f.write(f"  Total Bars:  {len(df):,}\n")
                f.write(
                    f"  Date Range:  {df['timestamp'].min()} to {df['timestamp'].max()}\n"
                )
                f.write(f"  Min Price:   ${df['low'].min():.2f}\n")
                f.write(f"  Max Price:   ${df['high'].max():.2f}\n")
                f.write(f"  Mean Price:  ${df['close'].mean():.2f}\n")

            f.write("\n" + "=" * 70 + "\n")
            f.write("KEY FINDINGS\n")
            f.write("=" * 70 + "\n\n")

            # Calculate some key metrics
            if "D1" in self.data:
                df = self.data["D1"].copy()
                df["returns"] = df["close"].pct_change()

                total_return = (
                    (df["close"].iloc[-1] - df["close"].iloc[0]) / df["close"].iloc[0]
                ) * 100

                f.write(f"1. Overall Price Movement:\n")
                f.write(f"   - Total Return: {total_return:+.2f}%\n")
                f.write(
                    f"   - From ${df['close'].iloc[0]:.2f} to ${df['close'].iloc[-1]:.2f}\n\n"
                )

                f.write(f"2. Volatility:\n")
                f.write(f"   - Daily Std Dev: {df['returns'].std() * 100:.4f}%\n")
                f.write(f"   - Max Single Day Gain: {df['returns'].max() * 100:.2f}%\n")
                f.write(
                    f"   - Max Single Day Loss: {df['returns'].min() * 100:.2f}%\n\n"
                )

                f.write(f"3. Trading Statistics:\n")
                positive_days = (df["returns"] > 0).sum()
                negative_days = (df["returns"] < 0).sum()
                f.write(
                    f"   - Positive Days: {positive_days} ({positive_days / len(df) * 100:.1f}%)\n"
                )
                f.write(
                    f"   - Negative Days: {negative_days} ({negative_days / len(df) * 100:.1f}%)\n\n"
                )

            f.write("=" * 70 + "\n")
            f.write("END OF REPORT\n")
            f.write("=" * 70 + "\n")

        print(f"✅ Report saved: {report_path}")
        print()

    def run_full_analysis(self):
        """Run complete EDA"""
        print("\n")
        print("╔" + "═" * 68 + "╗")
        print("║" + " " * 15 + "GOLD TRADING DATA - EDA ANALYSIS" + " " * 21 + "║")
        print("╚" + "═" * 68 + "╝")
        print("\n")

        # Load data
        self.load_data()

        if not self.data:
            print("❌ No data loaded. Please collect data first.")
            print("   Run: python collect_all_timeframes.py")
            return

        # Run analyses
        self.basic_statistics()
        self.volatility_analysis()
        self.price_distribution()
        self.trend_analysis()
        self.session_analysis()

        # Create visualizations
        self.create_visualizations()

        # Generate report
        self.generate_summary_report()

        print("=" * 70)
        print("🎉 EDA COMPLETE!")
        print("=" * 70)
        print()
        print("📊 Results saved to:")
        print(f"   Charts: {self.output_dir}/")
        print(f"   Report: {self.output_dir}/eda_summary_report.txt")
        print()
        print("Next step: Feature Engineering")
        print("   Continue to Step A to build technical indicators!")
        print()


def main():
    """Main function"""
    analyzer = GoldDataAnalyzer(data_dir="data/raw", output_dir="results/eda")

    analyzer.run_full_analysis()


if __name__ == "__main__":
    main()
