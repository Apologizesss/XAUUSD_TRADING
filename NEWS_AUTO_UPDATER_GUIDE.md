# News Auto Updater - คู่มือการใช้งาน

## 🚀 ภาพรวม

ระบบอัปเดตข่าวอัตโนมัติทุก 10 นาที พร้อมการวิเคราะห์ sentiment ด้วย **FinBERT** (Financial BERT Model)

### ✨ Features

- ✅ **ดึงข่าวอัตโนมัติ** - ทุก 10 นาที (ปรับได้)
- ✅ **FinBERT Sentiment Analysis** - โมเดล AI ที่เทรนจากข่าวการเงิน (Accuracy ~85-90%)
- ✅ **Auto-append Mode** - บันทึกเพิ่มในไฟล์เดียว ไม่สร้างไฟล์ใหม่ทุกครั้ง
- ✅ **Duplicate Detection** - กรองข่าวซ้ำอัตโนมัติ (ตาม URL)
- ✅ **Real-time Summary** - แสดง sentiment distribution ทันที
- ✅ **Master + Daily Files** - เก็บทั้งข่าวทั้งหมดและรายวัน

---

## 📋 การติดตั้ง

### 1. ติดตั้ง Dependencies

```bash
# ติดตั้ง tf-keras สำหรับ FinBERT
pip install tf-keras

# ติดตั้ง packages อื่นๆ (ถ้ายังไม่มี)
pip install transformers torch newsapi-python textblob
```

### 2. ตั้งค่า API Key

สร้างไฟล์ `.env`:

```env
NEWS_API_KEY=your_newsapi_key_here
```

**Get Free API Key:** https://newsapi.org/

---

## 🎯 วิธีใช้งาน

### Mode 1: อัปเดตอัตโนมัติต่อเนื่อง (แนะนำ)

```bash
# อัปเดตทุก 10 นาที (default)
python news_auto_updater.py

# กำหนดเวลาเอง (เช่น ทุก 5 นาที)
python news_auto_updater.py --interval 5

# กำหนดเวลาเอง (เช่น ทุก 30 นาที)
python news_auto_updater.py --interval 30
```

**หยุดการทำงาน:** กด `Ctrl+C`

### Mode 2: อัปเดตครั้งเดียว

```bash
# รันครั้งเดียวแล้วหยุด
python news_auto_updater.py --once
```

---

## 📊 Output Files

### 1. Master File (ข่าวทั้งหมด)
```
data/news/news_master.csv
```
- เก็บข่าวสะสมทั้งหมด
- Append mode - ไม่ลบข้อมูลเก่า
- กรองข่าวซ้ำอัตโนมัติ

### 2. Daily File (รายวัน)
```
data/news/news_daily_20251107.csv
```
- เก็บข่าวของวันนั้นๆ
- สร้างไฟล์ใหม่ทุกวัน
- ใช้สำหรับตรวจสอบข่าววันนี้

### 3. ตัวอย่างข้อมูลในไฟล์:

| timestamp | title | source | sentiment | polarity | confidence |
|-----------|-------|--------|-----------|----------|------------|
| 2025-11-07 10:30:00 | Gold prices surge... | Reuters | positive | 0.8523 | 0.92 |
| 2025-11-07 10:25:00 | Fed raises rates... | Bloomberg | negative | -0.6541 | 0.87 |

---

## 🧠 FinBERT vs TextBlob

### FinBERT (Default)
- ✅ โมเดล BERT ที่เทรนจากข่าวการเงิน
- ✅ ความแม่นยำสูง (85-90%)
- ✅ เข้าใจบริบททางการเงิน
- ⚠️ ช้ากว่า (ใช้เวลา ~2-3 วินาทีต่อข่าว)
- ⚠️ ต้องโหลดโมเดล 438 MB

### TextBlob (Fallback)
- ⚡ เร็วมาก (< 0.1 วินาทีต่อข่าว)
- ✅ ไม่ต้องโหลดโมเดล
- ⚠️ ความแม่นยำต่ำกว่า (60-70%)
- ⚠️ ไม่เข้าใจบริบททางการเงิน

**ระบบจะใช้ FinBERT อัตโนมัติถ้ามี tf-keras**

---

## 📈 ตัวอย่างการทำงาน

```
======================================================================
🚀 NEWS AUTO UPDATER - STARTED
======================================================================
⏰ Update Interval: 10 minutes
📁 Master File: data/news/news_master.csv
📁 Daily File: data/news/news_daily_20251107.csv
🛑 Press Ctrl+C to stop
======================================================================

🤖 Loading FinBERT sentiment model...
✅ FinBERT model loaded successfully

📰 Fetching news from last 60 minutes...
   Time range: 10:42:32 to 11:42:32

✅ Found 16 articles

🔍 Processing 16 articles...
  Processed 10/16 articles...

✅ Successfully processed 16 articles

📊 Sentiment Distribution:
sentiment
neutral     11
negative     3
positive     2

📈 Average Polarity: -0.0564

   📁 Created master file: 16 articles

======================================================================
📊 UPDATE SUMMARY #1
======================================================================
⏰ Time: 2025-11-07 11:43:03
📰 New Articles: 16

🎯 Sentiment Distribution:
   Neutral: 11 (68.8%)
   Negative: 3 (18.8%)
   Positive: 2 (12.5%)

📈 Average Polarity: -0.0564

✨ Most Positive:
   Evonith targets aggressive ramp-up in steel capacity...
   Polarity: 0.9119

⚡ Most Negative:
   Cautious sentiment to hurt Sensex, Nifty movements...
   Polarity: -0.9649

======================================================================
📊 Session Statistics:
   Updates: 1
   Total Articles: 16
   Uptime: 0:00:01
   Next update in: 10 minutes
======================================================================

💤 Sleeping for 10 minutes...
   (Next update at 11:53:03)
```

---

## ⚙️ การตั้งค่าขั้นสูง

### 1. รันเป็น Background Service (Windows)

สร้างไฟล์ `run_news_updater.bat`:

```batch
@echo off
start /B python news_auto_updater.py --interval 10
```

### 2. รันเป็น Background Service (Linux/Mac)

```bash
# ใช้ nohup
nohup python news_auto_updater.py --interval 10 > news_updater.log 2>&1 &

# หรือใช้ screen
screen -dmS news_updater python news_auto_updater.py --interval 10

# ดู log
tail -f news_updater.log

# หยุด
pkill -f news_auto_updater.py
```

### 3. ตั้งค่า Auto-start (Windows Task Scheduler)

1. เปิด Task Scheduler
2. Create Basic Task
3. Trigger: At startup
4. Action: Start a program
5. Program: `python`
6. Arguments: `D:\Zed\ai-gold-bot\news_auto_updater.py --interval 10`

---

## 🔧 Troubleshooting

### ปัญหา 1: FinBERT ไม่โหลด

```
⚠️ Could not load FinBERT: Your currently installed version of Keras is Keras 3...
```

**วิธีแก้:**
```bash
pip install tf-keras
```

### ปัญหา 2: ไม่มีข่าวใหม่

```
⚠️ No new articles in the last X minutes
```

**สาเหตุ:**
- ไม่มีข่าวเกี่ยวกับทองคำในช่วงเวลานั้น
- NewsAPI มีข้อจำกัด (Free: 100 requests/day)

**วิธีแก้:**
- รอการอัปเดตครั้งต่อไป
- เพิ่มช่วงเวลา: `--interval 30` (30 นาที)

### ปัญหา 3: API Rate Limit

```
❌ API Error: You have made too many requests recently
```

**วิธีแก้:**
- Free Plan: 100 requests/วัน
- ปรับ interval ให้มากขึ้น: `--interval 15` หรือ `--interval 30`
- หรืออัพเกรดเป็น Paid Plan

### ปัญหา 4: Duplicate Articles

ระบบกรองอัตโนมัติตาม URL แล้ว แต่ถ้าต้องการเช็คเอง:

```python
import pandas as pd

df = pd.read_csv('data/news/news_master.csv')
duplicates = df[df.duplicated(subset=['url'], keep=False)]
print(f"Duplicates: {len(duplicates)}")
```

---

## 📊 การใช้งานกับโมเดล Trading

### วิธีที่ 1: ใช้ Master File

```python
from src.features.news_features import NewsSentimentFeatures
import pandas as pd

# โหลดข้อมูลราคา
df_price = pd.read_csv("data/processed_data_20251107.csv")

# รวมกับข่าวจาก Master File
sentiment_features = NewsSentimentFeatures()
df_combined = sentiment_features.merge_price_and_news(
    df_price,
    news_path="data/news/news_master.csv",  # ใช้ Master File
    windows=[1, 4, 12, 24]
)

# เทรนโมเดล
# python train_xgboost.py --data-path data/price_with_sentiment.csv
```

### วิธีที่ 2: ใช้ Daily File

```python
# รวมกับข่าววันนี้เท่านั้น
df_combined = sentiment_features.merge_price_and_news(
    df_price,
    news_path="data/news/news_daily_20251107.csv",  # ใช้ Daily File
    windows=[1, 4, 12, 24]
)
```

---

## 📚 ข้อมูลอ้างอิง

- **FinBERT Model:** https://huggingface.co/ProsusAI/finbert
- **NewsAPI Docs:** https://newsapi.org/docs
- **TextBlob Docs:** https://textblob.readthedocs.io/

---

## 🎯 Best Practices

### 1. Update Interval

| Interval | จำนวน Updates/วัน | เหมาะสำหรับ |
|----------|------------------|-------------|
| 5 นาที | 288 | Live Trading (ต้อง Paid API) |
| 10 นาที | 144 | ✅ **แนะนำ** - สมดุลระหว่างความเร็วและ API limit |
| 30 นาที | 48 | Daily Trading |
| 60 นาที | 24 | Swing Trading |

### 2. ประหยัด API Calls

```python
# ดึงข่าวน้อยลงในช่วงที่ไม่มีการเทรด
# ปรับใน news_auto_updater.py:

from datetime import datetime

def should_update():
    now = datetime.now()
    hour = now.hour
    
    # ข้ามช่วง 0:00-6:00 (ตลาดปิด)
    if 0 <= hour < 6:
        return False
    
    return True
```

### 3. Monitoring

```bash
# เช็คว่ามีข่าวใหม่หรือไม่
tail -f news_updater.log

# นับจำนวนข่าว
wc -l data/news/news_master.csv

# ดู sentiment distribution
python -c "import pandas as pd; df = pd.read_csv('data/news/news_master.csv'); print(df['sentiment'].value_counts())"
```

---

## 🚀 Next Steps

1. **รันอัตโนมัติ:**
   ```bash
   python news_auto_updater.py --interval 10
   ```

2. **ตรวจสอบไฟล์:**
   ```bash
   ls -lh data/news/
   ```

3. **ใช้กับ Trading Model:**
   ```bash
   python test_news_sentiment.py
   ```

4. **เทรนโมเดลใหม่:**
   ```bash
   python train_xgboost.py --data-path data/price_with_sentiment_20251107.csv
   ```

---

**Created:** 2025-11-07  
**Version:** 2.0.0 (with FinBERT)  
**Status:** ✅ Production Ready
