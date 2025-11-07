# 🚀 HOW TO RUN LIVE TRADING

## ปัญหาที่พบ: โปรแกรมรันแล้วไม่แสดงผล

### สาเหตุ
Python มีการ **buffer output** ทำให้ข้อความไม่แสดงออกมาทันทีตอนโหลดโมเดล (ใช้เวลา 10-30 วินาที)

### วิธีแก้ไข: ใช้ `-u` flag (Unbuffered Output)

---

## ✅ วิธีที่ 1: รันด้วย Batch File (แนะนำ)

```batch
run_live_trading.bat
```

**ข้อดี:**
- แสดงผลทันทีทุกขั้นตอน
- ไม่ต้องพิมพ์คำสั่งยาวๆ
- รองรับ parameter เพิ่มเติม

**ตัวอย่าง:**
```batch
# รันแบบปกติ (5 นาทีต่อครั้ง)
run_live_trading.bat

# รันแบบกำหนดเวลา 30 นาที
run_live_trading.bat --duration 30

# รันแบบ test mode
run_live_trading.bat --test --duration 5
```

---

## ✅ วิธีที่ 2: รันด้วยคำสั่ง Python + `-u`

```batch
python -u live_trading.py --interval 300 --threshold 0.70
```

**สำคัญ:** ต้องมี `-u` เพื่อให้แสดงผลทันที!

---

## 📋 พารามิเตอร์ที่ใช้ได้

| พารามิเตอร์ | ค่าเริ่มต้น | คำอธิบาย |
|------------|------------|----------|
| `--symbol` | XAUUSD | สัญลักษณ์เทรด |
| `--timeframe` | M5 | กรอบเวลา (M5, H1, H4) |
| `--threshold` | 0.70 | ความมั่นใจขั้นต่ำ (70%) |
| `--risk` | 0.01 | ความเสี่ยงต่อเทรด (1%) |
| `--max-loss` | 0.05 | ขาดทุนสูงสุดต่อวัน (5%) |
| `--interval` | 300 | เวลาระหว่างการเช็ค (วินาที) |
| `--duration` | ∞ | ระยะเวลารวม (นาที) |
| `--test` | false | โหมดทดสอบ |

---

## 📊 ตัวอย่างการใช้งาน

### 1. รันแบบปกติ (ไม่มีกำหนด)
```batch
python -u live_trading.py --interval 300 --threshold 0.70
```

### 2. รันแบบจำกัดเวลา 1 ชั่วโมง
```batch
python -u live_trading.py --interval 300 --threshold 0.70 --duration 60
```

### 3. รันแบบเช็คบ่อยขึ้น (ทุก 1 นาที)
```batch
python -u live_trading.py --interval 60 --threshold 0.70
```

### 4. รันแบบ Confidence สูงขึ้น (80%)
```batch
python -u live_trading.py --interval 300 --threshold 0.80
```

### 5. รันแบบทดสอบ (สร้างสัญญาณปลอม)
```batch
python -u live_trading.py --interval 60 --threshold 0.70 --test --duration 5
```

---

## 🔍 สิ่งที่ควรเห็นตอนรัน

### 1. ขั้นตอนเริ่มต้น (10-30 วินาที)
```
======================================================================
🤖 AI GOLD TRADING BOT - LIVE TRADING SYSTEM
======================================================================
⚠️  WARNING: REAL MONEY AT RISK - USE DEMO ACCOUNT FIRST!
======================================================================

🔄 LOADING MODULES... (this may take 10-30 seconds)

   ✅ Basic modules loaded
   🔄 Loading MetaTrader5...
   ✅ MetaTrader5 loaded
   🔄 Loading NumPy and Pandas...
   ✅ NumPy and Pandas loaded
   🔄 Loading Joblib...
   ✅ Joblib loaded
   🔄 Loading Trading Inference Pipeline...
   ✅ Inference Pipeline loaded
   🔄 Loading News Collectors...
   ✅ All modules loaded!

🔄 INITIALIZING SYSTEM...

📰 Initializing News Sentiment System...
   📅 Update interval: 600s (10.0 minutes)
   🔄 [1/3] Loading News Collector...
   ✅ [2/3] Loading Sentiment Features...
   🔄 [3/3] Creating news directory...
✅ News system ready

⚙️ Initializing Trading Inference Pipeline...
   Model: results/ensemble/ensemble_model.pkl
   Scaler: results/ensemble/ensemble_scaler.pkl
   🔄 Loading models (this may take 10-30 seconds)...
✅ Inference pipeline ready

🔌 Connecting to MetaTrader 5...
✅ MT5 connected

📊 Fetching account information...
✅ Account info retrieved

======================================================================
ACCOUNT CONFIGURATION
======================================================================
Account Type: DEMO
Balance: 10000.00 USD
Symbol: XAUUSD
Timeframe: M5
Confidence Threshold: 70%
Risk per Trade: 1%
Max Daily Loss: 5%
Profit Target: $5.00 per position
Stop Loss: $-10.00 per position
======================================================================

[OK] Live trading system initialized
```

### 2. ลูปเทรดทุก 5 นาที
```
======================================================================
🚀 STARTING LIVE TRADING LOOP
======================================================================
⏱️  Check interval: 300s (5.0 minutes)
⌛ Duration: Indefinite (runs until stopped)
🎯 Confidence threshold: 70%
💰 Risk per trade: 1%

⚠️  Press Ctrl+C to stop safely
======================================================================

======================================================================
⏰ [2024-01-15 14:30:00] CHECK #1
======================================================================

📰 Checking news sentiment...
  ✅ Sentiment OK: 0.15 (neutral-positive)
  ✅ Trading allowed

🤖 Running AI inference...
     [1/4] Fetching live price data from MT5...
     ✅ Fetched 300 bars
     [2/4] Calculating technical indicators...
     ✅ Calculated 65 features
     [3/4] Adding sentiment features from news...
     ✅ Added sentiment features (Total: 68 features)
     [4/4] Preparing features for prediction...
     ✅ Features prepared
     🤖 Running AI prediction...
     ✅ Prediction complete (Probability UP: 65.34%)

📊 Signal generated: NEUTRAL
  ℹ️  No trade signal (confidence below threshold)

👁️  Monitoring open positions...
  ℹ️  No open positions

💾 Saving state...

💰 Account Status:
  Balance: 10000.00 USD
  Equity: 10000.00 USD
  P&L Today: +0.00 USD

======================================================================
⏳ Waiting 300s until next check...
   Next check at: 14:35:00
   Press Ctrl+C to stop
======================================================================
```

---

## ⚠️ ถ้ายังไม่แสดงผล

### วิธีแก้:

1. **ตรวจสอบว่าใช้ `-u` flag**
   ```batch
   python -u live_trading.py ...
   ```

2. **ใช้ไฟล์ .bat ที่สร้างไว้**
   ```batch
   run_live_trading.bat
   ```

3. **เปิด PowerShell/CMD แบบ Admin**
   - บางครั้ง permission ทำให้ output ไม่แสดง

4. **ตรวจสอบว่า MT5 เปิดอยู่**
   - ถ้า MT5 ไม่เปิด จะค้างตอนเชื่อมต่อ

5. **รัน test script เพื่อดูว่า console รองรับ UTF-8**
   ```batch
   python test_live_display.py
   ```

---

## 🛑 วิธีหยุดโปรแกรม

กด `Ctrl+C` แล้วจะหยุดอย่างปลอดภัย:

```
======================================================================
🛑 LIVE TRADING STOPPED BY USER
======================================================================
```

---

## 📌 หมายเหตุ

- **ต้องเปิด MT5 ก่อนรัน** - ไม่งั้นจะค้างตอนเชื่อมต่อ
- **ใช้ DEMO account ก่อน** - ทดสอบให้แน่ใจก่อนใช้เงินจริง
- **การโหลดโมเดลใช้เวลา 10-30 วินาที** - รอให้ขึ้น "✅ Inference pipeline ready"
- **ถ้าค้างนานกว่า 1 นาที** - กด Ctrl+C แล้วเช็คว่า MT5 เปิดอยู่ไหม

---

## 🎯 Quick Reference

| สถานการณ์ | คำสั่ง |
|-----------|--------|
| รันปกติ | `run_live_trading.bat` |
| รัน 30 นาที | `run_live_trading.bat --duration 30` |
| ทดสอบ | `run_live_trading.bat --test --duration 5` |
| เช็คบ่อย (1 นาที) | `python -u live_trading.py --interval 60 --threshold 0.70` |
| Confidence สูง (80%) | `python -u live_trading.py --interval 300 --threshold 0.80` |
| หยุด | กด `Ctrl+C` |

---

## ✅ สิ่งที่ต้องเตรียม

- [x] เปิด MetaTrader 5
- [x] Login บัญชี DEMO
- [x] โมเดล AI อยู่ใน `results/ensemble/`
- [x] Config ถูกต้อง
- [x] Internet เชื่อมต่อ

**พร้อมแล้วก็รันได้เลย!** 🚀