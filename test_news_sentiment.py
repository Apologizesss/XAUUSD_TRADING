"""
Test News Sentiment System
--------------------------
ทดสอบระบบ News Sentiment Analysis

ขั้นตอน:
1. ดึงข่าวจาก NewsAPI (ถ้ามี API key)
2. วิเคราะห์ sentiment ด้วย TextBlob/FinBERT
3. รวม sentiment features กับข้อมูลราคา
4. แสดงผลและบันทึก

วิธีใช้:
    python test_news_sentiment.py

    หรือใช้ข้อมูลตัวอย่าง (ไม่ต้องมี API key):
    python test_news_sentiment.py --sample
"""

import argparse
from datetime import datetime
from pathlib import Path

import pandas as pd

from src.data_collection.news_collector import NewsCollector
from src.features.news_features import NewsSentimentFeatures, create_sample_news_data


def test_news_collection():
    """ทดสอบการดึงข่าว"""
    print("\n" + "=" * 70)
    print("TEST 1: NEWS COLLECTION")
    print("=" * 70)

    collector = NewsCollector()

    # ดึงข่าว 7 วันย้อนหลัง
    df_news = collector.get_gold_news(days=7)

    if df_news.empty:
        print("⚠️ No news collected. Using sample data instead.")
        return None

    # บันทึก
    news_path = collector.save_news(df_news)

    return news_path


def test_sentiment_features(news_path: str):
    """ทดสอบการสร้าง sentiment features"""
    print("\n" + "=" * 70)
    print("TEST 2: SENTIMENT FEATURES")
    print("=" * 70)

    # โหลดข้อมูลราคา
    price_files = list(Path("data").glob("processed_data_*.csv"))

    if not price_files:
        print("❌ No price data found!")
        print("💡 Run 'python daily_update.py' first to collect price data.")
        return None

    latest_price_file = sorted(price_files)[-1]
    print(f"\n📊 Loading price data: {latest_price_file.name}")

    df_price = pd.read_csv(latest_price_file)
    print(f"   Total rows: {len(df_price)}")
    print(f"   Features: {len(df_price.columns)}")

    # รวม sentiment features
    sentiment_features = NewsSentimentFeatures()
    df_combined = sentiment_features.merge_price_and_news(
        df_price, str(news_path), windows=[1, 4, 12, 24]
    )

    # แสดงผล
    sentiment_cols = [col for col in df_combined.columns if "news_" in col]

    print("\n" + "=" * 70)
    print("📊 RESULTS")
    print("=" * 70)
    print(f"\nTotal rows: {len(df_combined)}")
    print(f"Total features: {len(df_combined.columns)}")
    print(f"Sentiment features added: {len(sentiment_cols)}")

    print("\n📰 Sentiment Feature Samples:")
    print("-" * 70)
    for col in sentiment_cols[:10]:
        print(f"  - {col}")
    if len(sentiment_cols) > 10:
        print(f"  ... and {len(sentiment_cols) - 10} more")

    # แสดงตัวอย่างข้อมูล
    print("\n📈 Sample Data (first 5 rows):")
    print("-" * 70)
    display_cols = ["timestamp", "close"] + sentiment_cols[:3]
    print(df_combined[display_cols].head())

    # Statistics
    print("\n📊 Sentiment Statistics:")
    print("-" * 70)
    for col in [
        "news_24h_sentiment_avg",
        "news_24h_positive_ratio",
        "news_24h_negative_ratio",
    ]:
        if col in df_combined.columns:
            print(f"  {col}:")
            print(f"    Mean: {df_combined[col].mean():.4f}")
            print(f"    Min:  {df_combined[col].min():.4f}")
            print(f"    Max:  {df_combined[col].max():.4f}")

    # บันทึก
    output_path = (
        Path("data") / f"price_with_sentiment_{datetime.now().strftime('%Y%m%d')}.csv"
    )
    df_combined.to_csv(output_path, index=False)
    print(f"\n💾 Saved combined data: {output_path}")

    return output_path


def test_with_sample_data():
    """ทดสอบด้วยข้อมูลตัวอย่าง (ไม่ต้องมี API key)"""
    print("\n" + "=" * 70)
    print("🧪 TESTING WITH SAMPLE DATA")
    print("=" * 70)

    # สร้างข้อมูลข่าวตัวอย่าง
    news_path = create_sample_news_data()

    # ทดสอบ sentiment features
    result = test_sentiment_features(str(news_path))

    return result


def main():
    """ฟังก์ชันหลัก"""
    parser = argparse.ArgumentParser(description="Test News Sentiment System")
    parser.add_argument(
        "--sample",
        action="store_true",
        help="Use sample data instead of real news (no API key needed)",
    )

    args = parser.parse_args()

    print("=" * 70)
    print("NEWS SENTIMENT SYSTEM - TEST SUITE")
    print("=" * 70)
    print(f"\nMode: {'SAMPLE DATA' if args.sample else 'REAL NEWS'}")

    if args.sample:
        # ใช้ข้อมูลตัวอย่าง
        result = test_with_sample_data()
    else:
        # ดึงข่าวจริง
        news_path = test_news_collection()

        if news_path:
            result = test_sentiment_features(str(news_path))
        else:
            print("\n⚠️ News collection failed. Trying sample data...")
            result = test_with_sample_data()

    # สรุปผล
    print("\n" + "=" * 70)
    print("✅ TEST COMPLETE")
    print("=" * 70)

    if result:
        print("\n✅ All tests passed successfully!")
        print("\n📋 Next Steps:")
        print("  1. Train new model with sentiment features:")
        print(f"     python train_xgboost.py --data-path {result}")
        print("\n  2. Or update daily_update.py to include sentiment features")
        print("\n  3. Get NewsAPI key from: https://newsapi.org/")
        print("     Then create .env file with: NEWS_API_KEY=your_key_here")
    else:
        print("\n⚠️ Some tests failed. Please check the errors above.")


if __name__ == "__main__":
    main()
