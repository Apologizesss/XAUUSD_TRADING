"""
News Auto Updater
-----------------
อัปเดตข่าวอัตโนมัติทุก 10 นาที

Features:
- ดึงข่าวจาก NewsAPI ทุก 10 นาที
- วิเคราะห์ sentiment ด้วย FinBERT
- บันทึกข้อมูลเพิ่มเติมในไฟล์เดียว (append mode)
- แสดง summary การอัปเดตแต่ละครั้ง
- สามารถหยุดด้วย Ctrl+C

วิธีใช้:
    python news_auto_updater.py

    หรือกำหนดเวลา:
    python news_auto_updater.py --interval 10  # นาที
"""

import argparse
import time
from datetime import datetime, timedelta
from pathlib import Path

import pandas as pd

from src.data_collection.news_collector import NewsCollector


class NewsAutoUpdater:
    """
    อัปเดตข่าวอัตโนมัติทุกๆ X นาที
    """

    def __init__(self, interval_minutes: int = 10):
        """
        Initialize Auto Updater

        Args:
            interval_minutes: ช่วงเวลาระหว่างการอัปเดต (นาที)
        """
        self.interval_minutes = interval_minutes
        self.interval_seconds = interval_minutes * 60
        self.collector = NewsCollector()

        # สร้างโฟลเดอร์
        self.news_dir = Path("data/news")
        self.news_dir.mkdir(parents=True, exist_ok=True)

        # ไฟล์สำหรับเก็บข่าวทั้งหมด
        self.master_file = self.news_dir / "news_master.csv"
        self.daily_file = (
            self.news_dir / f"news_daily_{datetime.now().strftime('%Y%m%d')}.csv"
        )

        # สถิติ
        self.update_count = 0
        self.total_articles = 0
        self.start_time = datetime.now()

    def fetch_recent_news(self, minutes_back: int = 30) -> pd.DataFrame:
        """
        ดึงข่าวล่าสุด

        Args:
            minutes_back: ดึงข่าวย้อนหลังกี่นาที

        Returns:
            DataFrame of news
        """
        to_date = datetime.now()
        from_date = to_date - timedelta(minutes=minutes_back)

        print(f"\n📰 Fetching news from last {minutes_back} minutes...")
        print(
            f"   Time range: {from_date.strftime('%H:%M:%S')} to {to_date.strftime('%H:%M:%S')}"
        )

        # ดึงข่าว
        articles = self.collector.fetch_news(
            query="gold OR XAUUSD OR 'gold price' OR 'precious metals'",
            from_date=from_date,
            to_date=to_date,
            sort_by="publishedAt",
            page_size=100,
        )

        if not articles:
            print("   ⚠️ No new articles found")
            return pd.DataFrame()

        # ประมวลผล
        df = self.collector.process_articles(articles, sentiment_method="auto")

        return df

    def save_news(self, df: pd.DataFrame) -> None:
        """
        บันทึกข่าว (append mode)

        Args:
            df: DataFrame ของข่าว
        """
        if df.empty:
            return

        # บันทึกใน master file (append)
        if self.master_file.exists():
            # อ่านไฟล์เดิม
            df_existing = pd.read_csv(self.master_file)
            df_existing["timestamp"] = pd.to_datetime(df_existing["timestamp"])

            # รวมกับข่าวใหม่
            df_combined = pd.concat([df_existing, df], ignore_index=True)

            # ลบข่าวซ้ำ (ตาม URL)
            df_combined = df_combined.drop_duplicates(subset=["url"], keep="last")

            # เรียงตาม timestamp
            df_combined = df_combined.sort_values("timestamp", ascending=False)

            # บันทึก
            df_combined.to_csv(self.master_file, index=False)

            new_articles = len(df_combined) - len(df_existing)
            print(
                f"   📁 Updated master file: +{new_articles} new articles (total: {len(df_combined)})"
            )
        else:
            # สร้างไฟล์ใหม่
            df.to_csv(self.master_file, index=False)
            print(f"   📁 Created master file: {len(df)} articles")

        # บันทึกใน daily file
        if self.daily_file.exists():
            df_daily = pd.read_csv(self.daily_file)
            df_daily = pd.concat([df_daily, df], ignore_index=True)
            df_daily = df_daily.drop_duplicates(subset=["url"], keep="last")
            df_daily.to_csv(self.daily_file, index=False)
        else:
            df.to_csv(self.daily_file, index=False)

    def print_summary(self, df: pd.DataFrame) -> None:
        """
        แสดง summary ของการอัปเดต

        Args:
            df: DataFrame ของข่าว
        """
        if df.empty:
            return

        print(f"\n{'=' * 70}")
        print(f"📊 UPDATE SUMMARY #{self.update_count}")
        print(f"{'=' * 70}")
        print(f"⏰ Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print(f"📰 New Articles: {len(df)}")

        # Sentiment distribution
        if "sentiment" in df.columns:
            sentiment_counts = df["sentiment"].value_counts()
            print(f"\n🎯 Sentiment Distribution:")
            for sentiment, count in sentiment_counts.items():
                percentage = (count / len(df)) * 100
                print(f"   {sentiment.capitalize()}: {count} ({percentage:.1f}%)")

            # Average polarity
            avg_polarity = df["polarity"].mean()
            print(f"\n📈 Average Polarity: {avg_polarity:.4f}")

            # ข่าวที่มี sentiment สูงสุด/ต่ำสุด
            if len(df) > 0:
                most_positive = df.loc[df["polarity"].idxmax()]
                most_negative = df.loc[df["polarity"].idxmin()]

                print(f"\n✨ Most Positive:")
                print(f"   {most_positive['title'][:60]}...")
                print(f"   Polarity: {most_positive['polarity']:.4f}")

                print(f"\n⚡ Most Negative:")
                print(f"   {most_negative['title'][:60]}...")
                print(f"   Polarity: {most_negative['polarity']:.4f}")

        # Statistics
        uptime = datetime.now() - self.start_time
        uptime_str = str(uptime).split(".")[0]  # Remove microseconds

        print(f"\n{'=' * 70}")
        print(f"📊 Session Statistics:")
        print(f"   Updates: {self.update_count}")
        print(f"   Total Articles: {self.total_articles}")
        print(f"   Uptime: {uptime_str}")
        print(f"   Next update in: {self.interval_minutes} minutes")
        print(f"{'=' * 70}")

    def update_once(self) -> None:
        """อัปเดตข่าวครั้งเดียว"""
        try:
            self.update_count += 1

            # ดึงข่าว (ครั้งแรกดึง 60 นาที, ครั้งต่อไปดึงตาม interval)
            minutes_back = 60 if self.update_count == 1 else (self.interval_minutes + 5)
            df = self.fetch_recent_news(minutes_back=minutes_back)

            if not df.empty:
                # บันทึก
                self.save_news(df)

                # อัปเดตสถิติ
                self.total_articles += len(df)

                # แสดง summary
                self.print_summary(df)
            else:
                print(f"\n⚠️ No new articles in the last {minutes_back} minutes")
                print(f"   Next update in: {self.interval_minutes} minutes")

        except Exception as e:
            print(f"\n❌ Error during update: {e}")
            import traceback

            traceback.print_exc()

    def run(self) -> None:
        """รันอัปเดตอัตโนมัติ"""
        print(f"\n{'=' * 70}")
        print(f"🚀 NEWS AUTO UPDATER - STARTED")
        print(f"{'=' * 70}")
        print(f"⏰ Update Interval: {self.interval_minutes} minutes")
        print(f"📁 Master File: {self.master_file}")
        print(f"📁 Daily File: {self.daily_file}")
        print(f"🛑 Press Ctrl+C to stop")
        print(f"{'=' * 70}\n")

        try:
            while True:
                self.update_once()

                # รอจนถึงการอัปเดตครั้งต่อไป
                print(f"\n💤 Sleeping for {self.interval_minutes} minutes...")
                print(
                    f"   (Next update at {(datetime.now() + timedelta(minutes=self.interval_minutes)).strftime('%H:%M:%S')})"
                )

                time.sleep(self.interval_seconds)

        except KeyboardInterrupt:
            print(f"\n\n{'=' * 70}")
            print(f"🛑 NEWS AUTO UPDATER - STOPPED")
            print(f"{'=' * 70}")
            print(f"📊 Final Statistics:")
            print(f"   Total Updates: {self.update_count}")
            print(f"   Total Articles: {self.total_articles}")

            uptime = datetime.now() - self.start_time
            uptime_str = str(uptime).split(".")[0]
            print(f"   Uptime: {uptime_str}")
            print(f"{'=' * 70}\n")


def main():
    """ฟังก์ชันหลัก"""
    parser = argparse.ArgumentParser(description="Auto-update news every X minutes")
    parser.add_argument(
        "--interval",
        type=int,
        default=10,
        help="Update interval in minutes (default: 10)",
    )
    parser.add_argument(
        "--once", action="store_true", help="Run update only once (no loop)"
    )

    args = parser.parse_args()

    # Create updater
    updater = NewsAutoUpdater(interval_minutes=args.interval)

    if args.once:
        # Run once
        print("Running single update...")
        updater.update_once()
    else:
        # Run continuously
        updater.run()


if __name__ == "__main__":
    main()
