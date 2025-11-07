"""
News Sentiment Features
-----------------------
รวม News Sentiment เข้ากับข้อมูลราคา

Features:
- รวม sentiment score กับ timeframe ของราคา
- สร้าง aggregated sentiment features
- คำนวณ sentiment momentum และ trends
"""

from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, Optional

import numpy as np
import pandas as pd


class NewsSentimentFeatures:
    """
    สร้าง features จาก News Sentiment
    """

    def __init__(self):
        """Initialize News Sentiment Features"""
        self.news_data = None

    def load_news(self, news_path: str) -> pd.DataFrame:
        """
        โหลดข้อมูลข่าว

        Args:
            news_path: path ไปยังไฟล์ข่าว

        Returns:
            DataFrame ของข่าว
        """
        try:
            df = pd.read_csv(news_path)
            df["timestamp"] = pd.to_datetime(df["timestamp"])

            print(f"✅ Loaded {len(df)} news articles")
            print(f"   Date range: {df['timestamp'].min()} to {df['timestamp'].max()}")

            self.news_data = df
            return df

        except Exception as e:
            print(f"❌ Error loading news: {e}")
            return pd.DataFrame()

    def aggregate_sentiment(
        self, df_news: pd.DataFrame, timestamp: datetime, window_hours: int = 24
    ) -> Dict:
        """
        คำนวณ sentiment รวมในช่วงเวลาที่กำหนด

        Args:
            df_news: DataFrame ของข่าว
            timestamp: เวลาที่ต้องการคำนวณ
            window_hours: ช่วงเวลาย้อนหลัง (ชั่วโมง)

        Returns:
            Dict with aggregated sentiment
        """
        # แปลง timestamp ให้เป็น timezone-aware ถ้าข่าวมี timezone
        if df_news["timestamp"].dt.tz is not None:
            # ถ้าข่าวมี timezone แต่ timestamp ไม่มี
            if not hasattr(timestamp, "tzinfo") or timestamp.tzinfo is None:
                timestamp = pd.Timestamp(timestamp).tz_localize("UTC")
        else:
            # ถ้าข่าวไม่มี timezone แต่ timestamp มี
            if hasattr(timestamp, "tzinfo") and timestamp.tzinfo is not None:
                timestamp = timestamp.tz_localize(None)

        # กรองข่าวในช่วงเวลาที่กำหนด
        start_time = timestamp - timedelta(hours=window_hours)
        mask = (df_news["timestamp"] >= start_time) & (
            df_news["timestamp"] <= timestamp
        )
        news_window = df_news[mask]

        if len(news_window) == 0:
            return {
                "news_count": 0,
                "sentiment_avg": 0.0,
                "sentiment_sum": 0.0,
                "sentiment_max": 0.0,
                "sentiment_min": 0.0,
                "sentiment_std": 0.0,
                "positive_count": 0,
                "negative_count": 0,
                "neutral_count": 0,
                "positive_ratio": 0.0,
                "negative_ratio": 0.0,
            }

        # คำนวณ statistics
        polarities = news_window["polarity"]
        sentiments = news_window["sentiment"]

        positive_count = (sentiments == "positive").sum()
        negative_count = (sentiments == "negative").sum()
        neutral_count = (sentiments == "neutral").sum()
        total_count = len(news_window)

        return {
            "news_count": total_count,
            "sentiment_avg": polarities.mean(),
            "sentiment_sum": polarities.sum(),
            "sentiment_max": polarities.max(),
            "sentiment_min": polarities.min(),
            "sentiment_std": polarities.std() if total_count > 1 else 0.0,
            "positive_count": positive_count,
            "negative_count": negative_count,
            "neutral_count": neutral_count,
            "positive_ratio": positive_count / total_count if total_count > 0 else 0.0,
            "negative_ratio": negative_count / total_count if total_count > 0 else 0.0,
        }

    def add_sentiment_features(
        self,
        df_price: pd.DataFrame,
        df_news: pd.DataFrame,
        windows: list = [1, 4, 12, 24, 48],  # hours
    ) -> pd.DataFrame:
        """
        เพิ่ม sentiment features ให้กับข้อมูลราคา

        Args:
            df_price: DataFrame ของราคา (ต้องมี column 'timestamp' หรือ 'time')
            df_news: DataFrame ของข่าว
            windows: รายการช่วงเวลาสำหรับคำนวณ (ชั่วโมง)

        Returns:
            DataFrame with sentiment features
        """
        df = df_price.copy()

        # ตรวจสอบว่ามี timestamp column
        if "timestamp" not in df.columns and "time" in df.columns:
            df["timestamp"] = pd.to_datetime(df["time"])
        elif "timestamp" in df.columns:
            df["timestamp"] = pd.to_datetime(df["timestamp"])
        else:
            print("❌ Error: No timestamp column found")
            return df

        print(f"\n🔍 Adding sentiment features...")
        print(f"   Price data: {len(df)} rows")
        print(f"   News data: {len(df_news)} articles")

        # สำหรับแต่ละ window
        for window in windows:
            print(f"   Processing {window}h window...")

            # สร้าง features สำหรับแต่ละแถว
            features = []
            for timestamp in df["timestamp"]:
                sent_stats = self.aggregate_sentiment(df_news, timestamp, window)
                features.append(sent_stats)

            # แปลงเป็น DataFrame
            df_features = pd.DataFrame(features)

            # เพิ่ม prefix ตาม window
            df_features = df_features.add_prefix(f"news_{window}h_")

            # รวมเข้ากับ df หลัก
            df = pd.concat([df, df_features], axis=1)

        print(f"\n✅ Added sentiment features for {len(windows)} time windows")
        print(f"   Total features now: {len(df.columns)}")

        return df

    def add_sentiment_momentum(
        self, df: pd.DataFrame, window: int = 24
    ) -> pd.DataFrame:
        """
        เพิ่ม sentiment momentum features

        Args:
            df: DataFrame with sentiment features
            window: ช่วงเวลาที่ใช้ (ชั่วโมง)

        Returns:
            DataFrame with momentum features
        """
        col_prefix = f"news_{window}h_"
        avg_col = f"{col_prefix}sentiment_avg"

        if avg_col not in df.columns:
            print(f"⚠️ Warning: Column {avg_col} not found")
            return df

        # คำนวณ momentum (อัตราการเปลี่ยนแปลง)
        df[f"{col_prefix}sentiment_momentum"] = df[avg_col].diff()

        # คำนวณ trend (moving average of sentiment)
        df[f"{col_prefix}sentiment_trend"] = (
            df[avg_col].rolling(window=10, min_periods=1).mean()
        )

        # คำนวณ acceleration (rate of change of momentum)
        df[f"{col_prefix}sentiment_acceleration"] = df[
            f"{col_prefix}sentiment_momentum"
        ].diff()

        return df

    def merge_price_and_news(
        self, df_price: pd.DataFrame, news_path: str, windows: list = [1, 4, 12, 24, 48]
    ) -> pd.DataFrame:
        """
        รวมข้อมูลราคาและข่าว (หนึ่งฟังก์ชันเดียวจบ)

        Args:
            df_price: DataFrame ของราคา
            news_path: path ไปยังไฟล์ข่าว
            windows: รายการช่วงเวลา

        Returns:
            DataFrame with price and sentiment features
        """
        # โหลดข่าว
        df_news = self.load_news(news_path)

        if df_news.empty:
            print("⚠️ No news data available. Skipping sentiment features.")
            return df_price

        # เพิ่ม sentiment features
        df = self.add_sentiment_features(df_price, df_news, windows)

        # เพิ่ม momentum features
        for window in windows:
            df = self.add_sentiment_momentum(df, window)

        return df


def create_sample_news_data(output_path: str = "data/news"):
    """
    สร้างข้อมูลข่าวตัวอย่าง (สำหรับทดสอบ)
    """
    print("\n📰 Creating sample news data...")

    # สร้างข้อมูลตัวอย่าง
    dates = pd.date_range(end=datetime.now(), periods=100, freq="3H")

    sentiments = np.random.choice(
        ["positive", "negative", "neutral"], size=100, p=[0.3, 0.3, 0.4]
    )
    polarities = []

    for sent in sentiments:
        if sent == "positive":
            pol = np.random.uniform(0.1, 0.9)
        elif sent == "negative":
            pol = np.random.uniform(-0.9, -0.1)
        else:
            pol = np.random.uniform(-0.1, 0.1)
        polarities.append(pol)

    df_news = pd.DataFrame(
        {
            "timestamp": dates,
            "title": [f"Sample news {i}" for i in range(100)],
            "description": [f"Description {i}" for i in range(100)],
            "source": ["Sample Source"] * 100,
            "url": ["http://example.com"] * 100,
            "sentiment": sentiments,
            "polarity": polarities,
            "confidence": np.random.uniform(0.5, 0.95, 100),
            "subjectivity": np.random.uniform(0.3, 0.8, 100),
            "method": ["sample"] * 100,
        }
    )

    # บันทึก
    Path(output_path).mkdir(parents=True, exist_ok=True)
    filepath = (
        Path(output_path) / f"sample_news_{datetime.now().strftime('%Y%m%d')}.csv"
    )
    df_news.to_csv(filepath, index=False)

    print(f"✅ Created sample news data: {filepath}")
    print(f"   Total articles: {len(df_news)}")

    return filepath


def main():
    """
    ทดสอบการรวม sentiment features
    """
    print("=" * 70)
    print("NEWS SENTIMENT FEATURES - Testing")
    print("=" * 70)

    # สร้างข้อมูลตัวอย่าง
    news_path = create_sample_news_data()

    # โหลดข้อมูลราคา (ใช้ไฟล์ที่มีอยู่)
    price_files = list(Path("data").glob("processed_data_*.csv"))

    if not price_files:
        print("❌ No price data found. Please run daily_update.py first.")
        return

    latest_price_file = sorted(price_files)[-1]
    print(f"\n📊 Loading price data: {latest_price_file}")

    df_price = pd.read_csv(latest_price_file)
    print(f"   Total rows: {len(df_price)}")

    # รวม sentiment features
    sentiment_features = NewsSentimentFeatures()
    df_combined = sentiment_features.merge_price_and_news(
        df_price, str(news_path), windows=[1, 4, 12, 24]
    )

    # แสดงผล
    print("\n" + "=" * 70)
    print("📊 COMBINED DATA SAMPLE")
    print("=" * 70)

    sentiment_cols = [col for col in df_combined.columns if "news_" in col]
    print(f"\nSentiment columns added: {len(sentiment_cols)}")
    print(df_combined[["timestamp"] + sentiment_cols[:5]].head())

    # บันทึก
    output_path = (
        Path("data") / f"price_with_sentiment_{datetime.now().strftime('%Y%m%d')}.csv"
    )
    df_combined.to_csv(output_path, index=False)
    print(f"\n💾 Saved combined data: {output_path}")

    print("\n" + "=" * 70)
    print("✅ FEATURE ENGINEERING COMPLETE")
    print("=" * 70)


if __name__ == "__main__":
    main()
