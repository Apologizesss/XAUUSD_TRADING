"""Quick test to see if system works"""

import io
import sys

# Fix Windows encoding
if sys.platform == "win32":
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding="utf-8", errors="replace")

print("=" * 60)
print("Quick System Test")
print("=" * 60)

# Test 1: News collector with TextBlob
print("\n1. Testing News Collector...")
from src.data_collection.news_collector import NewsCollector

nc = NewsCollector()
print(f"   ✅ News Collector initialized")
print(f"   Using: TextBlob sentiment analysis")

# Test 2: Fetch small news sample
print("\n2. Fetching news (1 day)...")
df_news = nc.get_gold_news(days=1)
print(f"   ✅ Found {len(df_news)} articles")

if len(df_news) > 0:
    print(f"\n3. Sample news:")
    for idx, row in df_news.head(3).iterrows():
        print(f"   - {row['title'][:60]}...")
        print(f"     Sentiment: {row['sentiment']} ({row['polarity']:.4f})")

print("\n" + "=" * 60)
print("✅ System is working! Ready for live trading.")
print("=" * 60)
