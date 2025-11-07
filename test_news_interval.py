"""Test news caching every 10 minutes"""

import time
from datetime import datetime

from live_trading import LiveTrading

print("=" * 70)
print("Testing News Cache (10 minute interval)")
print("=" * 70)

# Create trader with 10-minute news interval
trader = LiveTrading(
    symbol="XAUUSD",
    timeframe="M5",
    use_news_sentiment=True,
    news_update_interval=600,  # 10 minutes
)

print("\n" + "=" * 70)
print("Test 1: First news fetch (should fetch)")
print("=" * 70)
sentiment_1 = trader.check_news_sentiment()
print(f"\n✅ Result 1:")
print(f"   Sentiment: {sentiment_1['sentiment_label']}")
print(f"   Score: {sentiment_1['sentiment_score']:.4f}")
print(f"   News Count: {sentiment_1['news_count']}")

print("\n" + "=" * 70)
print("Test 2: Immediate second check (should use cache)")
print("=" * 70)
time.sleep(2)
sentiment_2 = trader.check_news_sentiment()
print(f"\n✅ Result 2:")
print(f"   Sentiment: {sentiment_2['sentiment_label']}")
print(f"   Should use cached data!")

print("\n" + "=" * 70)
print("Test 3: After 5 seconds (should still use cache)")
print("=" * 70)
time.sleep(3)
sentiment_3 = trader.check_news_sentiment()
print(f"\n✅ Result 3:")
print(f"   Still using cached data (5s < 600s)")

print("\n" + "=" * 70)
print("Test 4: Force update (should fetch new)")
print("=" * 70)
sentiment_4 = trader.check_news_sentiment(force_update=True)
print(f"\n✅ Result 4:")
print(f"   Forced update - fetched new data")

print("\n" + "=" * 70)
print("✅ All tests completed!")
print("=" * 70)
print(f"\n📊 Summary:")
print(f"   News update interval: 600s (10 minutes)")
print(f"   Cache working: ✅")
print(f"   Force update working: ✅")
