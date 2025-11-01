"""
Feature Engineering Pipeline
=============================
Complete pipeline that combines all feature engineering modules.

This pipeline:
1. Loads raw OHLCV data
2. Adds technical indicators (88 features)
3. Adds time-based features (45 features)
4. Handles missing values
5. Validates data quality
6. Saves processed features

Usage:
    from src.features.feature_pipeline import FeaturePipeline

    pipeline = FeaturePipeline()
    df_processed = pipeline.process_file('data/raw/XAUUSD_M15.csv')
"""

import pandas as pd
import numpy as np
from pathlib import Path
from datetime import datetime
import warnings
from typing import Optional, Tuple, List

warnings.filterwarnings("ignore")

# Import feature modules
from .technical_indicators import TechnicalIndicators
from .time_features import TimeFeatures


class FeaturePipeline:
    """Complete feature engineering pipeline"""

    def __init__(self, output_dir: str = "data/processed"):
        """
        Initialize Feature Pipeline

        Args:
            output_dir: Directory to save processed data
        """
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)

        # Initialize feature modules
        self.tech_indicators = TechnicalIndicators()
        self.time_features = TimeFeatures()

        # Track statistics
        self.stats = {
            "original_rows": 0,
            "processed_rows": 0,
            "original_features": 0,
            "total_features": 0,
            "technical_features": 0,
            "time_features": 0,
            "missing_values_before": 0,
            "missing_values_after": 0,
        }

    def load_data(self, filepath: str) -> pd.DataFrame:
        """
        Load data from CSV file

        Args:
            filepath: Path to CSV file

        Returns:
            DataFrame with loaded data
        """
        print("\n📂 Loading Data")
        print("=" * 70)

        filepath = Path(filepath)

        if not filepath.exists():
            raise FileNotFoundError(f"File not found: {filepath}")

        df = pd.read_csv(filepath)

        print(f"✅ Loaded: {filepath.name}")
        print(f"   Rows: {len(df):,}")
        print(f"   Columns: {len(df.columns)}")

        # Validate required columns
        required = ["timestamp", "open", "high", "low", "close", "tick_volume"]
        missing = [col for col in required if col not in df.columns]

        if missing:
            raise ValueError(f"Missing required columns: {missing}")

        # Convert timestamp
        df["timestamp"] = pd.to_datetime(df["timestamp"])
        df = df.sort_values("timestamp").reset_index(drop=True)

        self.stats["original_rows"] = len(df)
        self.stats["original_features"] = len(df.columns)

        return df

    def add_features(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Add all features to DataFrame

        Args:
            df: Input DataFrame with OHLCV data

        Returns:
            DataFrame with all features added
        """
        print("\n🔧 Feature Engineering")
        print("=" * 70)

        original_cols = len(df.columns)

        # Add technical indicators
        print("\n1️⃣  Technical Indicators")
        df = self.tech_indicators.add_all_indicators(df)
        tech_cols = len(df.columns)
        self.stats["technical_features"] = tech_cols - original_cols

        # Add time features
        print("\n2️⃣  Time-Based Features")
        df = self.time_features.add_all_time_features(df)
        time_cols = len(df.columns)
        self.stats["time_features"] = time_cols - tech_cols

        self.stats["total_features"] = len(df.columns)

        print("\n✅ Feature Engineering Complete!")
        print(f"   Original features: {original_cols}")
        print(f"   Technical features: {self.stats['technical_features']}")
        print(f"   Time features: {self.stats['time_features']}")
        print(f"   Total features: {self.stats['total_features']}")

        return df

    def handle_missing_values(
        self, df: pd.DataFrame, method: str = "forward_fill"
    ) -> pd.DataFrame:
        """
        Handle missing values in DataFrame

        Args:
            df: Input DataFrame
            method: Method to handle missing values
                   - 'forward_fill': Forward fill
                   - 'backward_fill': Backward fill
                   - 'drop': Drop rows with missing values
                   - 'mean': Fill with mean (numeric columns only)

        Returns:
            DataFrame with missing values handled
        """
        print("\n🔍 Handling Missing Values")
        print("=" * 70)

        # Count missing values before
        missing_before = df.isnull().sum().sum()
        self.stats["missing_values_before"] = missing_before

        if missing_before == 0:
            print("✅ No missing values found!")
            return df

        print(f"⚠️  Found {missing_before:,} missing values")

        # Show columns with missing values
        missing_by_col = df.isnull().sum()
        missing_cols = missing_by_col[missing_by_col > 0].sort_values(ascending=False)

        if len(missing_cols) > 0:
            print("\nColumns with missing values:")
            for col, count in missing_cols.head(10).items():
                pct = (count / len(df)) * 100
                print(f"  {col:30s}: {count:5,} ({pct:5.2f}%)")

        # Apply method
        if method == "forward_fill":
            print("\n📝 Using forward fill...")
            df = df.fillna(method="ffill")
            # Fill remaining with backward fill
            df = df.fillna(method="bfill")

        elif method == "backward_fill":
            print("\n📝 Using backward fill...")
            df = df.fillna(method="bfill")
            # Fill remaining with forward fill
            df = df.fillna(method="ffill")

        elif method == "drop":
            print("\n📝 Dropping rows with missing values...")
            df = df.dropna()

        elif method == "mean":
            print("\n📝 Filling with mean (numeric columns only)...")
            numeric_cols = df.select_dtypes(include=[np.number]).columns
            df[numeric_cols] = df[numeric_cols].fillna(df[numeric_cols].mean())

        # Count missing values after
        missing_after = df.isnull().sum().sum()
        self.stats["missing_values_after"] = missing_after

        if missing_after > 0:
            print(f"\n⚠️  Still {missing_after:,} missing values remaining")
            print("   Filling remaining with 0...")
            df = df.fillna(0)
            missing_after = 0

        self.stats["processed_rows"] = len(df)

        print(f"\n✅ Missing values handled")
        print(f"   Before: {missing_before:,}")
        print(f"   After: {missing_after:,}")
        print(f"   Rows remaining: {len(df):,}")

        return df

    def validate_data(self, df: pd.DataFrame) -> Tuple[bool, List[str]]:
        """
        Validate processed data quality

        Args:
            df: Processed DataFrame

        Returns:
            Tuple of (is_valid, list of issues)
        """
        print("\n✔️  Data Validation")
        print("=" * 70)

        issues = []

        # Check for infinite values
        inf_count = np.isinf(df.select_dtypes(include=[np.number])).sum().sum()
        if inf_count > 0:
            issues.append(f"Found {inf_count} infinite values")

        # Check for missing values
        missing_count = df.isnull().sum().sum()
        if missing_count > 0:
            issues.append(f"Found {missing_count} missing values")

        # Check for duplicate timestamps
        dup_count = df.duplicated(subset=["timestamp"]).sum()
        if dup_count > 0:
            issues.append(f"Found {dup_count} duplicate timestamps")

        # Check data range
        if len(df) < 100:
            issues.append(f"Warning: Only {len(df)} rows (minimum 100 recommended)")

        # Check for constant columns (no variance)
        numeric_cols = df.select_dtypes(include=[np.number]).columns
        constant_cols = [col for col in numeric_cols if df[col].std() == 0]
        if constant_cols:
            issues.append(
                f"Found {len(constant_cols)} constant columns: {constant_cols[:5]}"
            )

        is_valid = len(issues) == 0

        if is_valid:
            print("✅ All validation checks passed!")
            print(f"   Rows: {len(df):,}")
            print(f"   Features: {len(df.columns)}")
            print(f"   Date range: {df['timestamp'].min()} to {df['timestamp'].max()}")
        else:
            print("⚠️  Validation issues found:")
            for issue in issues:
                print(f"   - {issue}")

        return is_valid, issues

    def save_processed_data(
        self, df: pd.DataFrame, filename: Optional[str] = None
    ) -> str:
        """
        Save processed data to CSV

        Args:
            df: Processed DataFrame
            filename: Output filename (optional)

        Returns:
            Path to saved file
        """
        print("\n💾 Saving Processed Data")
        print("=" * 70)

        if filename is None:
            # Extract original filename info
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"processed_features_{timestamp}.csv"

        filepath = self.output_dir / filename

        df.to_csv(filepath, index=False)

        file_size = filepath.stat().st_size / (1024 * 1024)  # MB

        print(f"✅ Saved: {filepath}")
        print(f"   Size: {file_size:.2f} MB")
        print(f"   Rows: {len(df):,}")
        print(f"   Columns: {len(df.columns)}")

        return str(filepath)

    def generate_feature_report(self, df: pd.DataFrame) -> str:
        """
        Generate feature engineering report

        Args:
            df: Processed DataFrame

        Returns:
            Path to report file
        """
        print("\n📊 Generating Feature Report")
        print("=" * 70)

        report_path = self.output_dir / "feature_report.txt"

        with open(report_path, "w", encoding="utf-8") as f:
            f.write("=" * 70 + "\n")
            f.write("FEATURE ENGINEERING REPORT\n")
            f.write("=" * 70 + "\n")
            f.write(f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n")

            f.write("DATASET SUMMARY\n")
            f.write("-" * 70 + "\n")
            f.write(f"Total Rows: {len(df):,}\n")
            f.write(f"Total Features: {len(df.columns)}\n")
            f.write(f"Date Range: {df['timestamp'].min()} to {df['timestamp'].max()}\n")
            f.write(
                f"Duration: {(df['timestamp'].max() - df['timestamp'].min()).days} days\n\n"
            )

            f.write("FEATURE BREAKDOWN\n")
            f.write("-" * 70 + "\n")
            f.write(f"Original Features: {self.stats['original_features']}\n")
            f.write(f"Technical Indicators: {self.stats['technical_features']}\n")
            f.write(f"Time Features: {self.stats['time_features']}\n")
            f.write(f"Total Features: {self.stats['total_features']}\n\n")

            f.write("FEATURE CATEGORIES\n")
            f.write("-" * 70 + "\n")

            # Technical features by category
            tech_groups = self.tech_indicators.get_feature_groups(df)
            f.write("\nTechnical Indicators:\n")
            for group, features in tech_groups.items():
                f.write(f"  {group.title():15s}: {len(features)} features\n")

            # Time features
            time_feats = self.time_features.get_feature_list(df)
            f.write(f"\nTime Features: {len(time_feats)} features\n")

            f.write("\nDATA QUALITY\n")
            f.write("-" * 70 + "\n")
            f.write(f"Missing Values Before: {self.stats['missing_values_before']:,}\n")
            f.write(f"Missing Values After: {self.stats['missing_values_after']:,}\n")
            f.write(f"Rows Processed: {self.stats['processed_rows']:,}\n")

            f.write("\n" + "=" * 70 + "\n")
            f.write("END OF REPORT\n")
            f.write("=" * 70 + "\n")

        print(f"✅ Report saved: {report_path}")

        return str(report_path)

    def process_file(
        self,
        input_file: str,
        output_file: Optional[str] = None,
        missing_method: str = "forward_fill",
    ) -> pd.DataFrame:
        """
        Process a single file through complete pipeline

        Args:
            input_file: Path to input CSV file
            output_file: Path to output CSV file (optional)
            missing_method: Method to handle missing values

        Returns:
            Processed DataFrame
        """
        print("\n" + "=" * 70)
        print("FEATURE ENGINEERING PIPELINE")
        print("=" * 70)

        # Load data
        df = self.load_data(input_file)

        # Add features
        df = self.add_features(df)

        # Handle missing values
        df = self.handle_missing_values(df, method=missing_method)

        # Validate
        is_valid, issues = self.validate_data(df)

        # Save
        if output_file is None:
            # Generate filename from input
            input_path = Path(input_file)
            base_name = input_path.stem
            output_file = f"{base_name}_features.csv"

        output_path = self.save_processed_data(df, output_file)

        # Generate report
        report_path = self.generate_feature_report(df)

        print("\n" + "=" * 70)
        print("🎉 PIPELINE COMPLETE!")
        print("=" * 70)
        print(f"✅ Input: {input_file}")
        print(f"✅ Output: {output_path}")
        print(f"✅ Report: {report_path}")
        print(f"\n📊 Summary:")
        print(
            f"   Rows: {self.stats['original_rows']:,} → {self.stats['processed_rows']:,}"
        )
        print(
            f"   Features: {self.stats['original_features']} → {self.stats['total_features']}"
        )
        print(f"   Technical: {self.stats['technical_features']} features")
        print(f"   Time: {self.stats['time_features']} features")
        print()

        return df


def main():
    """Run pipeline on sample data"""
    print("=" * 70)
    print("FEATURE PIPELINE - TEST RUN")
    print("=" * 70)

    # Process M15 data
    pipeline = FeaturePipeline(output_dir="data/processed")

    input_file = "data/raw/XAUUSD_M15_20251101_172509.csv"

    if not Path(input_file).exists():
        print(f"❌ Input file not found: {input_file}")
        print("Please run: python collect_all_timeframes.py")
        return

    # Process file
    df = pipeline.process_file(
        input_file=input_file,
        output_file="XAUUSD_M15_features_complete.csv",
        missing_method="forward_fill",
    )

    # Show sample
    print("\n📊 Sample (last 5 rows, selected features):")
    sample_cols = [
        "timestamp",
        "close",
        "RSI_14",
        "MACD",
        "BB_pct_b",
        "hour",
        "session_newyork",
        "is_peak_hours",
    ]
    available_cols = [col for col in sample_cols if col in df.columns]
    print(df[available_cols].tail())

    print("\n✅ Feature Pipeline ready for production!")
    print("\nNext steps:")
    print("  1. Process all timeframes")
    print("  2. Start model training (Phase 3)")
    print("  3. Build trading strategies")


if __name__ == "__main__":
    main()
