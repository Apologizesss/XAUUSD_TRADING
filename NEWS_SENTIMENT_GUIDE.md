# News Sentiment Analysis - คู่มือการใช้งาน

## ภาพรวม

ระบบ News Sentiment Analysis เพิ่มความสามารถให้บอท Gold Trading ในการวิเคราะห์ความรู้สึกจากข่าวสารเพื่อปรับปรุงความแม่นยำในการทำนายราคา

## ⚙️ การติดตั้ง

### 1. ติดตั้ง Dependencies

Dependencies ที่จำเป็นมีอยู่ใน `requirements.txt` แล้ว:
- `transformers` - สำหรับ FinBERT sentiment analysis
- `newsapi-python` - สำหรับดึงข้อมูลข่าว
- `textblob` - สำหรับ sentiment analysis แบบพื้นฐาน
- `nltk` - สำหรับ NLP

```bash
pip install -r requirements.txt
```

### 2. ดาวน์โหลด NLTK Data (ครั้งแรกเท่านั้น)

```python
python -c "import nltk; nltk.download('brown'); nltk.download('punkt')"
```

### 3. ตั้งค่า API Key

1. สมัคร NewsAPI (ฟรี): https://newsapi.org/
2. สร้างไฟล์ `.env` ในโฟลเดอร์หลัก:

```env
NEWS_API_KEY=your_newsapi_key_here
```

**หมายเหตุ:** NewsAPI Free Plan:
- ข่าวย้อนหลังได้ 1 เดือน
- 100 requests/วัน
- เพียงพอสำหรับการเทรดรายวัน

---

## 🚀 การใช้งาน

### วิธีที่ 1: ทดสอบระบบ (แนะนำเริ่มต้น)

#### ทดสอบด้วยข้อมูลตัวอย่าง (ไม่ต้องมี API key)
```bash
python test_news_sentiment.py --sample
```

#### ทดสอบด้วยข่าวจริง (ต้องมี API key)
```bash
python test_news_sentiment.py
```

### วิธีที่ 2: ดึงข่าวและวิเคราะห์ Sentiment

```python
from src.data_collection.news_collector import NewsCollector

# สร้าง collector
collector = NewsCollector()

# ดึงข่าวทองคำ 7 วันย้อนหลัง
df_news = collector.get_gold_news(days=7)

# บันทึกข้อมูล
news_path = collector.save_news(df_news)
```

### วิธีที่ 3: รวม Sentiment Features กับข้อมูลราคา

```python
from src.features.news_features import NewsSentimentFeatures
import pandas as pd

# โหลดข้อมูลราคา
df_price = pd.read_csv("data/processed_data_20251107.csv")

# รวม sentiment features
sentiment_features = NewsSentimentFeatures()
df_combined = sentiment_features.merge_price_and_news(
    df_price,
    news_path="data/news/news_20251107.csv",
    windows=[1, 4, 12, 24]  # ชั่วโมง
)

# บันทึก
df_combined.to_csv("data/price_with_sentiment.csv", index=False)
```

### วิธีที่ 4: เทรนโมเดลพร้อม Sentiment Features

```bash
python train_xgboost.py --data-path data/price_with_sentiment_20251107.csv
```

---

## 📊 Sentiment Features ที่สร้างขึ้น

สำหรับแต่ละ time window (เช่น 1h, 4h, 12h, 24h, 48h):

### จำนวนข่าว
- `news_{window}h_news_count` - จำนวนข่าวทั้งหมด

### Sentiment Scores
- `news_{window}h_sentiment_avg` - sentiment เฉลี่ย (-1 ถึง 1)
- `news_{window}h_sentiment_sum` - sentiment รวม
- `news_{window}h_sentiment_max` - sentiment สูงสุด
- `news_{window}h_sentiment_min` - sentiment ต่ำสุด
- `news_{window}h_sentiment_std` - ค่าเบี่ยงเบนมาตรฐาน

### การนับประเภท Sentiment
- `news_{window}h_positive_count` - จำนวนข่าวบวก
- `news_{window}h_negative_count` - จำนวนข่าวลบ
- `news_{window}h_neutral_count` - จำนวนข่าวกลางๆ

### อัตราส่วน
- `news_{window}h_positive_ratio` - สัดส่วนข่าวบวก
- `news_{window}h_negative_ratio` - สัดส่วนข่าวลบ

### Momentum Features
- `news_{window}h_sentiment_momentum` - อัตราการเปลี่ยนแปลง sentiment
- `news_{window}h_sentiment_trend` - แนวโน้ม sentiment
- `news_{window}h_sentiment_acceleration` - ความเร่งของ sentiment

**ตัวอย่าง:** ถ้าใช้ windows=[1, 4, 24] จะได้ features รวม 3 × 14 = **42 features**

---

## 🤖 Sentiment Analysis Methods

### 1. TextBlob (Default Fallback)
- เร็ว, ใช้ง่าย
- เหมาะสำหรับทดสอบ
- Accuracy: พอใช้ (~60-70%)

### 2. FinBERT (Recommended)
- โมเดล BERT ที่เทรนกับข่าวการเงิน
- ความแม่นยำสูง (~85-90%)
- ต้องใช้เวลาในการโหลดโมเดล
- รองรับ GPU (เร็วขึ้น)

```python
# เลือก method
collector = NewsCollector()
df_news = collector.get_gold_news(
    days=7,
    sentiment_method='finbert'  # หรือ 'textblob' หรือ 'auto'
)
```

---

## 🔄 Integration กับระบบเดิม

### อัปเดต daily_update.py ให้รวม News

```python
# เพิ่มที่ DailyUpdater class

from src.data_collection.news_collector import NewsCollector
from src.features.news_features import NewsSentimentFeatures

def collect_news(self, days=7):
    """ดึงข่าวและวิเคราะห์ sentiment"""
    print("📰 ดึงข่าว...")
    
    collector = NewsCollector()
    df_news = collector.get_gold_news(days=days)
    
    if not df_news.empty:
        news_path = collector.save_news(df_news)
        return news_path
    return None

def prepare_training_data(self, df):
    """เตรียมข้อมูล (แก้ไขให้รวม sentiment)"""
    # ... โค้ดเดิม ...
    
    # เพิ่ม sentiment features
    news_files = list(Path("data/news").glob("news_*.csv"))
    if news_files:
        latest_news = sorted(news_files)[-1]
        
        sentiment_features = NewsSentimentFeatures()
        df_features = sentiment_features.merge_price_and_news(
            df_features,
            str(latest_news),
            windows=[1, 4, 12, 24]
        )
    
    return df_features
```

---

## 📈 ผลลัพธ์ที่คาดหวัง

เมื่อรวม News Sentiment แล้ว:

### ✅ ข้อดี
- **ความแม่นยำเพิ่มขึ้น** - โมเดลรับรู้บริบทข่าว
- **ตอบสนองเหตุการณ์** - รู้ว่ามีข่าวสำคัญออกมา
- **Trend Detection** - จับทิศทางจากข่าว
- **Risk Management** - หลีกเลี่ยงช่วงข่าวผันผวน

### ⚠️ ข้อควรระวัง
- ข่าวไม่ได้ส่งผล 100% (ราคาขึ้นอยู่กับหลายปัจจัย)
- API มีข้อจำกัด (100 requests/day สำหรับ Free plan)
- ต้องเทรนโมเดลใหม่ (ข้อมูลเก่าไม่มี sentiment features)

---

## 🧪 การทดสอบและ Validation

### 1. ทดสอบการดึงข่าว
```bash
python -c "from src.data_collection.news_collector import NewsCollector; NewsCollector().get_gold_news(days=1)"
```

### 2. ทดสอบ Sentiment Features
```bash
python test_news_sentiment.py --sample
```

### 3. เปรียบเทียบโมเดล

เทรน 2 โมเดล:
```bash
# โมเดลไม่มี sentiment
python train_xgboost.py --data-path data/processed_data_20251107.csv

# โมเดลมี sentiment
python train_xgboost.py --data-path data/price_with_sentiment_20251107.csv
```

เปรียบเทียบ:
- Test Accuracy
- F1-Score
- Precision/Recall
- Feature Importance (sentiment features ติด top 20 หรือไม่)

---

## 🛠️ Troubleshooting

### ไม่มี API Key
```
⚠️ Warning: NEWS_API_KEY not found in .env file
```
**วิธีแก้:** สร้างไฟล์ `.env` และใส่ API key

### FinBERT โหลดไม่ได้
```
⚠️ Could not load FinBERT
```
**วิธีแก้:** 
- ตรวจสอบ internet connection
- หรือใช้ TextBlob: `sentiment_method='textblob'`

### ข่าวไม่ตรงกับราคา
**วิธีแก้:**
- ตรวจสอบ timezone ของข่าวและราคา
- ปรับ `windows` ให้เหมาะสม
- เพิ่มข้อมูลย้อนหลัง

---

## 📚 แหล่งข้อมูลเพิ่มเติม

- NewsAPI Docs: https://newsapi.org/docs
- FinBERT Model: https://huggingface.co/ProsusAI/finbert
- TextBlob Docs: https://textblob.readthedocs.io/

---

## 🎯 Roadmap (ต่อยอด)

- [ ] รองรับ news sources เพิ่มเติม (Finnhub, Alpha Vantage)
- [ ] Real-time news streaming
- [ ] Entity recognition (ระบุชื่อธนาคารกลาง, ผู้นำประเทศ)
- [ ] News impact scoring (คะแนนความสำคัญของข่าว)
- [ ] Sentiment visualization dashboard

---

**สร้างโดย:** AI Gold Trading Bot Team  
**อัปเดตล่าสุด:** 2025-11-07  
**เวอร์ชัน:** 1.0.0
