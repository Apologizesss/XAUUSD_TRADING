"""
News Data Collector
-------------------
ดึงข้อมูลข่าวที่เกี่ยวข้องกับทองคำและตลาดการเงิน

Features:
- ดึงข้อมูลจาก NewsAPI
- กรองข่าวที่เกี่ยวข้องกับทองคำ, เศรษฐกิจ, ดอลลาร์
- วิเคราะห์ sentiment ด้วย TextBlob และ Transformers
- บันทึกข้อมูลเป็น DataFrame
"""

import os
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, List, Optional

import pandas as pd
import requests
from dotenv import load_dotenv

# NLP Libraries
from textblob import TextBlob

# Temporarily disable transformers import to speed up startup
# try:
#     from transformers import pipeline
#
#     TRANSFORMERS_AVAILABLE = True
# except ImportError:
#     TRANSFORMERS_AVAILABLE = False
#     print("⚠️ Warning: transformers not available. Using TextBlob only.")

TRANSFORMERS_AVAILABLE = False


class NewsCollector:
    """
    ดึงและวิเคราะห์ข่าวที่เกี่ยวข้องกับทองคำ
    """

    def __init__(self, api_key: Optional[str] = None):
        """
        Initialize News Collector

        Args:
            api_key: NewsAPI key (ถ้าไม่ระบุจะโหลดจาก .env)
        """
        load_dotenv()
        self.api_key = api_key or os.getenv("NEWS_API_KEY")

        if not self.api_key:
            print("⚠️ Warning: NEWS_API_KEY not found in .env file")
            print("📌 Get your free API key from: https://newsapi.org/")

        self.base_url = "https://newsapi.org/v2/everything"

        # Keywords ที่เกี่ยวข้องกับทองคำ
        self.gold_keywords = [
            "gold",
            "XAUUSD",
            "gold price",
            "precious metals",
            "federal reserve",
            "inflation",
            "dollar index",
            "USD",
            "interest rates",
            "treasury",
            "central bank",
        ]

        # Initialize sentiment analyzer
        self.sentiment_analyzer = None
        # Temporarily disable FinBERT due to PyTorch version incompatibility
        # Use TextBlob instead (fast and reliable for now)
        print("📊 Using TextBlob for sentiment analysis")
        if False and TRANSFORMERS_AVAILABLE:
            try:
                print("🤖 Loading FinBERT sentiment model...")

                # Auto-detect GPU
                import torch

                if torch.cuda.is_available():
                    device = 0  # Use GPU
                    print(f"   🚀 GPU detected: {torch.cuda.get_device_name(0)}")
                else:
                    device = -1  # Use CPU
                    print(f"   💻 Using CPU (GPU not available)")

                # ใช้ FinBERT สำหรับวิเคราะห์ความรู้สึกทางการเงิน
                # Use safetensors to avoid torch.load vulnerability
                os.environ["TRANSFORMERS_OFFLINE"] = "0"

                self.sentiment_analyzer = pipeline(
                    "sentiment-analysis",
                    model="ProsusAI/finbert",
                    device=device,
                    max_length=512,
                    truncation=True,
                    batch_size=8 if device == 0 else 4,  # Larger batch for GPU
                    use_safetensors=True,  # Force use safetensors format
                )

                device_name = "GPU" if device == 0 else "CPU"
                print(f"✅ FinBERT model loaded successfully on {device_name}")
            except Exception as e:
                print(f"⚠️ Could not load FinBERT: {e}")
                print("📌 Using TextBlob as fallback")

    def fetch_news(
        self,
        query: str = "gold OR XAUUSD OR 'gold price'",
        from_date: Optional[datetime] = None,
        to_date: Optional[datetime] = None,
        language: str = "en",
        sort_by: str = "relevancy",
        page_size: int = 100,
    ) -> List[Dict]:
        """
        ดึงข่าวจาก NewsAPI

        Args:
            query: คำค้นหา
            from_date: วันที่เริ่มต้น (default: 7 วันย้อนหลัง)
            to_date: วันที่สิ้นสุด (default: วันนี้)
            language: ภาษา
            sort_by: เรียงตาม (relevancy, popularity, publishedAt)
            page_size: จำนวนข่าวสูงสุด

        Returns:
            List of news articles
        """
        if not self.api_key:
            print("❌ Error: NEWS_API_KEY is required")
            return []

        # Set default dates
        if to_date is None:
            to_date = datetime.now()
        if from_date is None:
            from_date = to_date - timedelta(days=7)

        # Format dates
        from_str = from_date.strftime("%Y-%m-%d")
        to_str = to_date.strftime("%Y-%m-%d")

        # API parameters
        params = {
            "q": query,
            "from": from_str,
            "to": to_str,
            "language": language,
            "sortBy": sort_by,
            "pageSize": page_size,
            "apiKey": self.api_key,
        }

        try:
            print(f"\n📰 Fetching news from {from_str} to {to_str}...")
            response = requests.get(self.base_url, params=params, timeout=30)
            response.raise_for_status()

            data = response.json()

            if data["status"] == "ok":
                articles = data.get("articles", [])
                print(f"✅ Found {len(articles)} articles")
                return articles
            else:
                print(f"❌ API Error: {data.get('message', 'Unknown error')}")
                return []

        except requests.exceptions.RequestException as e:
            print(f"❌ Request Error: {e}")
            return []
        except Exception as e:
            print(f"❌ Error: {e}")
            return []

    def analyze_sentiment_textblob(self, text: str) -> Dict:
        """
        วิเคราะห์ sentiment ด้วย TextBlob

        Args:
            text: ข้อความที่ต้องการวิเคราะห์

        Returns:
            Dict with sentiment scores
        """
        try:
            blob = TextBlob(text)
            polarity = blob.sentiment.polarity  # -1 to 1
            subjectivity = blob.sentiment.subjectivity  # 0 to 1

            # Convert to category
            if polarity > 0.1:
                sentiment = "positive"
            elif polarity < -0.1:
                sentiment = "negative"
            else:
                sentiment = "neutral"

            return {
                "sentiment": sentiment,
                "polarity": polarity,
                "subjectivity": subjectivity,
                "method": "textblob",
            }
        except Exception as e:
            print(f"⚠️ TextBlob error: {e}")
            return {
                "sentiment": "neutral",
                "polarity": 0.0,
                "subjectivity": 0.0,
                "method": "textblob",
            }

    def analyze_sentiment_finbert(self, text: str) -> Dict:
        """
        วิเคราะห์ sentiment ด้วย FinBERT

        Args:
            text: ข้อความที่ต้องการวิเคราะห์

        Returns:
            Dict with sentiment scores
        """
        if not self.sentiment_analyzer:
            return self.analyze_sentiment_textblob(text)

        try:
            # Truncate text to 512 tokens (BERT limit)
            text = text[:512]

            result = self.sentiment_analyzer(text)[0]

            sentiment = result["label"].lower()
            score = result["score"]

            # Convert to polarity scale (-1 to 1)
            if sentiment == "positive":
                polarity = score
            elif sentiment == "negative":
                polarity = -score
            else:  # neutral
                polarity = 0.0

            return {
                "sentiment": sentiment,
                "polarity": polarity,
                "confidence": score,
                "method": "finbert",
            }
        except Exception as e:
            print(f"⚠️ FinBERT error: {e}")
            return self.analyze_sentiment_textblob(text)

    def analyze_sentiment(self, text: str, method: str = "auto") -> Dict:
        """
        วิเคราะห์ sentiment (เลือก method อัตโนมัติ)

        Args:
            text: ข้อความที่ต้องการวิเคราะห์
            method: 'auto', 'finbert', 'textblob'

        Returns:
            Dict with sentiment scores
        """
        if method == "finbert" or (method == "auto" and self.sentiment_analyzer):
            return self.analyze_sentiment_finbert(text)
        else:
            return self.analyze_sentiment_textblob(text)

    def process_articles(
        self, articles: List[Dict], sentiment_method: str = "auto"
    ) -> pd.DataFrame:
        """
        ประมวลผลข่าวและวิเคราะห์ sentiment

        Args:
            articles: รายการข่าวจาก API
            sentiment_method: วิธีวิเคราะห์ sentiment

        Returns:
            DataFrame with processed news
        """
        processed_data = []

        print(f"\n🔍 Processing {len(articles)} articles...")

        for i, article in enumerate(articles):
            try:
                # Extract data
                title = article.get("title", "")
                description = article.get("description", "")
                content = article.get("content", "")
                published_at = article.get("publishedAt", "")
                source = article.get("source", {}).get("name", "Unknown")
                url = article.get("url", "")

                # Combine text for sentiment analysis
                full_text = f"{title}. {description}"

                # Analyze sentiment
                sentiment_result = self.analyze_sentiment(full_text, sentiment_method)

                # Parse datetime
                try:
                    pub_datetime = pd.to_datetime(published_at)
                except:
                    pub_datetime = datetime.now()

                processed_data.append(
                    {
                        "timestamp": pub_datetime,
                        "title": title,
                        "description": description,
                        "source": source,
                        "url": url,
                        "sentiment": sentiment_result["sentiment"],
                        "polarity": sentiment_result["polarity"],
                        "confidence": sentiment_result.get("confidence", 0.0),
                        "subjectivity": sentiment_result.get("subjectivity", 0.0),
                        "method": sentiment_result["method"],
                    }
                )

                if (i + 1) % 10 == 0:
                    print(f"  Processed {i + 1}/{len(articles)} articles...")

            except Exception as e:
                print(f"⚠️ Error processing article {i}: {e}")
                continue

        df = pd.DataFrame(processed_data)

        if len(df) > 0:
            print(f"\n✅ Successfully processed {len(df)} articles")
            print(f"\n📊 Sentiment Distribution:")
            print(df["sentiment"].value_counts())
            print(f"\n📈 Average Polarity: {df['polarity'].mean():.4f}")

        return df

    def get_gold_news(
        self, days: int = 7, sentiment_method: str = "auto"
    ) -> pd.DataFrame:
        """
        ดึงข่าวทองคำและวิเคราะห์ sentiment

        Args:
            days: จำนวนวันย้อนหลัง
            sentiment_method: วิธีวิเคราะห์ sentiment

        Returns:
            DataFrame with news and sentiment
        """
        to_date = datetime.now()
        from_date = to_date - timedelta(days=days)

        # ดึงข่าวที่เกี่ยวกับทองคำ ราคาทอง และปัจจัยที่ส่งผลต่อทอง
        query = '("gold price" OR XAUUSD OR "gold trading" OR "gold market" OR "gold futures" OR "gold rally" OR "gold outlook" OR "precious metal" OR "federal reserve" OR "interest rate" OR "inflation" OR "dollar index") AND NOT (mining OR copper OR iron OR aluminum OR platinum OR palladium)'
        articles = self.fetch_news(query=query, from_date=from_date, to_date=to_date)

        if not articles:
            print("⚠️ No articles found")
            return pd.DataFrame()

        # ประมวลผลและวิเคราะห์
        df = self.process_articles(articles, sentiment_method)

        return df

    def save_news(self, df: pd.DataFrame, output_dir: str = "data/news"):
        """
        บันทึกข้อมูลข่าว

        Args:
            df: DataFrame ของข่าว
            output_dir: โฟลเดอร์สำหรับบันทึก
        """
        if df.empty:
            print("⚠️ No data to save")
            return

        output_path = Path(output_dir)
        output_path.mkdir(parents=True, exist_ok=True)

        filename = f"news_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv"
        filepath = output_path / filename

        df.to_csv(filepath, index=False)
        print(f"\n💾 Saved news data to: {filepath}")
        print(f"   Total articles: {len(df)}")

        return filepath


def main():
    """
    ทดสอบการดึงข่าวและวิเคราะห์ sentiment
    """
    print("=" * 70)
    print("NEWS SENTIMENT COLLECTOR - GOLD TRADING")
    print("=" * 70)

    # Initialize collector
    collector = NewsCollector()

    # ดึงข่าว 7 วันย้อนหลัง
    df_news = collector.get_gold_news(days=7)

    if not df_news.empty:
        # บันทึกข้อมูล
        collector.save_news(df_news)

        # แสดงตัวอย่าง
        print("\n" + "=" * 70)
        print("📰 SAMPLE NEWS")
        print("=" * 70)
        print(df_news[["timestamp", "title", "sentiment", "polarity"]].head(10))

    print("\n" + "=" * 70)
    print("✅ COLLECTION COMPLETE")
    print("=" * 70)


if __name__ == "__main__":
    main()
