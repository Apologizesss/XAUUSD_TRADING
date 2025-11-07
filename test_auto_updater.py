"""
Test News Auto Updater with FinBERT
"""

from datetime import datetime

from news_auto_updater import NewsAutoUpdater

print("=" * 70)
print("TESTING NEWS AUTO UPDATER WITH FINBERT")
print("=" * 70)

# Create updater
updater = NewsAutoUpdater(interval_minutes=10)

# Test with longer time range (24 hours)
print("\n🧪 Testing with 24-hour lookback...")
df = updater.fetch_recent_news(minutes_back=1440)  # 24 hours

if not df.empty:
    print(f"\n✅ Successfully fetched {len(df)} articles")

    # Save
    updater.save_news(df)
    updater.total_articles = len(df)
    updater.update_count = 1

    # Show summary
    updater.print_summary(df)
else:
    print("\n⚠️ No articles found in the last 24 hours")

print("\n" + "=" * 70)
print("✅ TEST COMPLETE")
print("=" * 70)
