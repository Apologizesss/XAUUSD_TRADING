"""Test improved news query"""

from src.data_collection.news_collector import NewsCollector

print("🔍 Testing improved news query...")
print("=" * 60)

nc = NewsCollector()
df = nc.get_gold_news(days=1)

print(f"\n📊 Found {len(df)} articles")

if len(df) > 0:
    print("\n📰 Top 10 News:")
    print("-" * 60)
    for idx, row in df.head(10).iterrows():
        print(f"\n{idx + 1}. {row['title'][:80]}")
        print(
            f"   Sentiment: {row['sentiment'].upper()} (Polarity: {row['polarity']:.4f})"
        )
        print(f"   Source: {row['source']}")
else:
    print("⚠️ No articles found")
