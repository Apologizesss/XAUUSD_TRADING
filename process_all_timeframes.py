"""
Process All Timeframes - Feature Engineering Pipeline
====================================================
Process all collected XAUUSD data through the feature engineering pipeline.
Generates features for M5, M15, M30, H1, H4, D1 timeframes.
"""

import os
import sys
from pathlib import Path
import glob
import time
from datetime import datetime

# Add project root to path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

from src.features.feature_pipeline import FeaturePipeline


def main():
    """Process all timeframes through feature pipeline."""

    print("=" * 80)
    print("🔧 FEATURE ENGINEERING - ALL TIMEFRAMES")
    print("=" * 80)
    print(f"Started at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")

    # Initialize pipeline
    pipeline = FeaturePipeline()

    # Define input/output directories
    raw_dir = project_root / "data" / "raw"
    processed_dir = project_root / "data" / "processed"
    processed_dir.mkdir(parents=True, exist_ok=True)

    # Find all raw CSV files
    raw_files = sorted(glob.glob(str(raw_dir / "XAUUSD_*.csv")))

    if not raw_files:
        print("❌ No raw data files found in data/raw/")
        return

    print(f"📂 Found {len(raw_files)} raw data files:\n")
    for f in raw_files:
        print(f"   • {os.path.basename(f)}")
    print()

    # Process each file
    results = []
    total_start = time.time()

    for i, raw_file in enumerate(raw_files, 1):
        file_name = os.path.basename(raw_file)

        # Extract timeframe from filename (e.g., XAUUSD_M15_20251101_172141.csv -> M15)
        parts = file_name.split("_")
        if len(parts) >= 2:
            timeframe = parts[1]
        else:
            timeframe = "UNKNOWN"

        print("-" * 80)
        print(f"[{i}/{len(raw_files)}] Processing: {file_name}")
        print(f"           Timeframe: {timeframe}")
        print("-" * 80)

        start_time = time.time()

        try:
            # Generate output filename
            output_filename = f"XAUUSD_{timeframe}_features_complete.csv"
            output_file = str(processed_dir / output_filename)

            # Process file
            df_processed = pipeline.process_file(
                input_file=raw_file, output_file=output_file
            )

            elapsed = time.time() - start_time

            print(f"✅ SUCCESS in {elapsed:.2f}s")
            print(f"   Output: {output_filename}\n")

            results.append(
                {
                    "timeframe": timeframe,
                    "input": file_name,
                    "output": output_filename,
                    "status": "SUCCESS",
                    "time": elapsed,
                }
            )

        except Exception as e:
            elapsed = time.time() - start_time
            print(f"❌ FAILED in {elapsed:.2f}s")
            print(f"   Error: {str(e)}\n")

            results.append(
                {
                    "timeframe": timeframe,
                    "input": file_name,
                    "output": None,
                    "status": "FAILED",
                    "time": elapsed,
                    "error": str(e),
                }
            )

    # Summary
    total_elapsed = time.time() - total_start

    print("=" * 80)
    print("📊 PROCESSING SUMMARY")
    print("=" * 80)

    success_count = sum(1 for r in results if r["status"] == "SUCCESS")
    failed_count = len(results) - success_count

    print(f"\nTotal files processed: {len(results)}")
    print(f"✅ Successful: {success_count}")
    print(f"❌ Failed: {failed_count}")
    print(f"⏱️  Total time: {total_elapsed:.2f}s ({total_elapsed / 60:.2f} minutes)")
    print()

    # Detailed results
    print("Detailed Results:")
    print("-" * 80)
    for r in results:
        status_icon = "✅" if r["status"] == "SUCCESS" else "❌"
        print(
            f"{status_icon} {r['timeframe']:5s} | {r['input']:40s} | {r['time']:6.2f}s"
        )
        if r["status"] == "FAILED":
            print(f"          Error: {r.get('error', 'Unknown error')}")

    print("\n" + "=" * 80)
    print(f"✨ Processing complete! Check data/processed/ for output files.")
    print("=" * 80)
    print(f"Finished at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")

    # List all processed files
    processed_files = sorted(glob.glob(str(processed_dir / "*_features_complete.csv")))
    if processed_files:
        print(f"\n📁 Processed files available ({len(processed_files)}):")
        for pf in processed_files:
            file_size = os.path.getsize(pf) / (1024 * 1024)  # MB
            print(f"   • {os.path.basename(pf)} ({file_size:.2f} MB)")


if __name__ == "__main__":
    main()
