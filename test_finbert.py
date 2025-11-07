"""
Test FinBERT Sentiment Analysis
"""

from src.data_collection.news_collector import NewsCollector

print("=" * 70)
print("TESTING FINBERT SENTIMENT ANALYSIS")
print("=" * 70)

# Create collector
collector = NewsCollector()

# Test sentences
test_sentences = [
    "Gold prices surge amid inflation fears",
    "Central bank raises interest rates, gold falls",
    "Markets remain stable as gold holds steady",
]

print("\n📊 Testing FinBERT on sample sentences:\n")

for sentence in test_sentences:
    print(f"Text: {sentence}")
    result = collector.analyze_sentiment(sentence, method="auto")
    print(f"  Sentiment: {result['sentiment']}")
    print(f"  Polarity: {result['polarity']:.4f}")
    print(f"  Method: {result['method']}")
    print()

print("=" * 70)
print("✅ FinBERT TEST COMPLETE")
print("=" * 70)
