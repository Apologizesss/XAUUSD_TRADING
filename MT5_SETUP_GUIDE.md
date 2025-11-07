# 📊 MT5 SETUP GUIDE - คู่มือตั้งค่า MetaTrader 5

## 🚨 ปัญหาที่พบ
```
❌ Missing MT5 credentials in .env file
[Error] ไม่สามารถเชื่อมต่อ MT5 ได้
```

---

## ✅ วิธีแก้ไขทีละขั้นตอน

### 📥 ขั้นตอนที่ 1: ดาวน์โหลดและติดตั้ง MetaTrader 5

#### สำหรับ Windows:
1. **เลือกโบรกเกอร์** (แนะนำ):
   - **XM Global**: https://www.xm.com/mt5
   - **IC Markets**: https://www.icmarkets.com/mt5
   - **Exness**: https://www.exness.com/mt5
   - **FBS**: https://fbs.com/mt5
   - **Pepperstone**: https://www.pepperstone.com/mt5

2. **ดาวน์โหลด MT5**:
   - ไปที่เว็บโบรกเกอร์ที่เลือก
   - คลิก "Download MT5" หรือ "ดาวน์โหลด MT5"
   - เลือก Windows version

3. **ติดตั้ง**:
   - ดับเบิลคลิกไฟล์ที่ดาวน์โหลด (mt5setup.exe)
   - ทำตามขั้นตอนการติดตั้ง
   - รอจนติดตั้งเสร็จ

---

### 📝 ขั้นตอนที่ 2: สร้าง Demo Account

1. **เปิด MetaTrader 5**

2. **สร้างบัญชี Demo**:
   - เมนู: File → Open an Account
   - หรือคลิก "Open an Account" ที่หน้าแรก

3. **เลือกโบรกเกอร์**:
   - พิมพ์ชื่อโบรกเกอร์ในช่องค้นหา (เช่น "XM", "IC Markets")
   - เลือก server ที่มีคำว่า "Demo"

4. **กรอกข้อมูล**:
   ```
   ชื่อ: [ชื่อของคุณ]
   นามสกุล: [นามสกุล]
   อีเมล: [อีเมลของคุณ]
   โทรศัพท์: [เบอร์โทร]
   
   Account Type: Demo
   Deposit: 10,000 USD (หรือตามต้องการ)
   Leverage: 1:100 (แนะนำสำหรับ Gold)
   ```

5. **รับข้อมูล Login**:
   - **Login**: ตัวเลข 7-8 หลัก (เช่น 12345678)
   - **Password**: รหัสผ่านที่ได้รับ
   - **Server**: ชื่อ server (เช่น XMGlobal-Demo 3)

   ⚠️ **สำคัญมาก**: บันทึกข้อมูลนี้ไว้!

---

### ⚙️ ขั้นตอนที่ 3: ตั้งค่า MT5 สำหรับ Python

1. **เปิด MT5 Settings**:
   - เมนู: Tools → Options (หรือกด Ctrl+O)

2. **ไปที่แท็บ "Expert Advisors"**:
   - ✅ ติ๊ก "Allow automated trading"
   - ✅ ติ๊ก "Allow DLL imports"
   - ✅ ติ๊ก "Allow WebRequest for listed URL"
   - คลิก OK

3. **ตรวจสอบว่า Algo Trading เปิดอยู่**:
   - ดูที่ toolbar ด้านบน
   - ปุ่ม "Algo Trading" ต้องเป็นสีเขียว
   - ถ้าเป็นสีแดง ให้คลิกเพื่อเปิด

---

### 📁 ขั้นตอนที่ 4: แก้ไขไฟล์ config/.env

1. **เปิดไฟล์ `config/.env`** ด้วย Notepad หรือ VS Code

2. **แก้ไขข้อมูลตามนี้**:
   ```env
   # MetaTrader 5 Credentials
   MT5_LOGIN=12345678
   MT5_PASSWORD=yourpassword123
   MT5_SERVER=XMGlobal-Demo 3
   
   # News API (optional - ไว้ก่อนได้)
   NEWS_API_KEY=your_newsapi_key_here
   
   # Telegram Bot (optional - ไว้ก่อนได้)
   TELEGRAM_BOT_TOKEN=your_telegram_bot_token
   TELEGRAM_CHAT_ID=your_telegram_chat_id
   
   # Trading Parameters
   INITIAL_CAPITAL=10000.0
   MAX_RISK_PER_TRADE=0.02
   MAX_DAILY_LOSS=0.05
   MAX_DRAWDOWN=0.15
   
   # Database
   DATABASE_PATH=data/trading.db
   
   # Logging
   LOG_LEVEL=INFO
   ```

3. **บันทึกไฟล์**

---

### 🧪 ขั้นตอนที่ 5: ทดสอบการเชื่อมต่อ

1. **สร้างไฟล์ทดสอบ** `test_mt5.py`:
   ```python
   import MetaTrader5 as mt5
   from dotenv import load_dotenv
   import os
   
   # โหลด config
   load_dotenv('config/.env')
   
   # อ่านค่าจาก .env
   login = int(os.getenv('MT5_LOGIN', '0'))
   password = os.getenv('MT5_PASSWORD', '')
   server = os.getenv('MT5_SERVER', '')
   
   print("=" * 60)
   print("TESTING MT5 CONNECTION")
   print("=" * 60)
   print(f"Login: {login}")
   print(f"Server: {server}")
   print()
   
   # เชื่อมต่อ MT5
   if not mt5.initialize():
       print("❌ Failed to initialize MT5")
       print("Error:", mt5.last_error())
       quit()
   
   print("✅ MT5 initialized")
   
   # Login
   authorized = mt5.login(login, password, server)
   if not authorized:
       print("❌ Failed to login")
       print("Error:", mt5.last_error())
       mt5.shutdown()
       quit()
   
   print("✅ Login successful!")
   
   # แสดงข้อมูลบัญชี
   account_info = mt5.account_info()
   if account_info:
       print()
       print("ACCOUNT INFO:")
       print(f"  Balance: ${account_info.balance:,.2f}")
       print(f"  Equity: ${account_info.equity:,.2f}")
       print(f"  Leverage: 1:{account_info.leverage}")
       print(f"  Server: {account_info.server}")
       print(f"  Company: {account_info.company}")
   
   # ตรวจสอบ Symbol
   symbol_info = mt5.symbol_info("XAUUSD")
   if symbol_info:
       print()
       print("XAUUSD INFO:")
       print(f"  Bid: {symbol_info.bid}")
       print(f"  Ask: {symbol_info.ask}")
       print(f"  Spread: {(symbol_info.ask - symbol_info.bid) * 100:.1f} points")
   
   mt5.shutdown()
   print()
   print("✅ Test completed successfully!")
   ```

2. **รันทดสอบ**:
   ```bash
   python test_mt5.py
   ```

3. **ผลลัพธ์ที่ควรได้**:
   ```
   ============================================================
   TESTING MT5 CONNECTION
   ============================================================
   Login: 12345678
   Server: XMGlobal-Demo 3
   
   ✅ MT5 initialized
   ✅ Login successful!
   
   ACCOUNT INFO:
     Balance: $10,000.00
     Equity: $10,000.00
     Leverage: 1:100
     Server: XMGlobal-Demo 3
     Company: XM Global Limited
   
   XAUUSD INFO:
     Bid: 2653.45
     Ask: 2653.95
     Spread: 50.0 points
   
   ✅ Test completed successfully!
   ```

---

## 🔧 วิธีแก้ปัญหาที่พบบ่อย

### ปัญหา 1: "Failed to initialize MT5"
**สาเหตุ**: MT5 ยังไม่ได้เปิด
**แก้ไข**: เปิดโปรแกรม MetaTrader 5 ก่อนรันโค้ด

### ปัญหา 2: "Failed to login"
**สาเหตุ**: ข้อมูล login ผิด
**แก้ไข**: 
- ตรวจสอบ Login, Password, Server ใน .env
- ตรวจสอบว่าเป็น Demo account
- ลอง login ใน MT5 โดยตรงก่อน

### ปัญหา 3: "No module named 'dotenv'"
**สาเหตุ**: ยังไม่ได้ติดตั้ง python-dotenv
**แก้ไข**: `pip install python-dotenv`

### ปัญหา 4: "Symbol XAUUSD not found"
**สาเหตุ**: โบรกเกอร์อาจใช้ชื่อ symbol ต่างกัน
**แก้ไข**: 
- บางโบรกเกอร์ใช้ "GOLD"
- บางโบรกเกอร์ใช้ "XAUUSD.m"
- ดูใน Market Watch ของ MT5

---

## 📊 ตัวอย่างโบรกเกอร์และ Server Names

| โบรกเกอร์ | Demo Server Name | Symbol ทอง |
|----------|------------------|------------|
| XM | XMGlobal-Demo 3 | GOLD |
| IC Markets | ICMarketsSC-Demo | XAUUSD |
| Exness | Exness-Demo | XAUUSDm |
| FBS | FBS-Demo | XAUUSD |
| Pepperstone | Pepperstone-Demo | XAUUSD |

---

## 🎯 หลังจากตั้งค่าสำเร็จ

เมื่อทดสอบการเชื่อมต่อสำเร็จแล้ว คุณสามารถ:

1. **รัน Daily Update**:
   ```bash
   python daily_update.py
   ```

2. **เริ่ม Paper Trading**:
   ```bash
   python paper_trading.py
   ```

3. **Train โมเดลใหม่**:
   ```bash
   python train_xgboost.py
   ```

---

## 💡 Tips สำคัญ

1. **ใช้ Demo Account เท่านั้น** ในช่วงทดสอบ
2. **เปิด MT5 ตลอดเวลา** เมื่อรันบอท
3. **Internet ต้องเสถียร** เพื่อการเชื่อมต่อที่ดี
4. **Backup ไฟล์ .env** เก็บข้อมูล login ไว้
5. **ทดสอบช่วง Market Open** (จันทร์-ศุกร์)

---

## 📞 ต้องการความช่วยเหลือ?

หากยังมีปัญหา:
1. ตรวจสอบ error message อย่างละเอียด
2. ลองรันไฟล์ `test_mt5.py` เพื่อดู error
3. ตรวจสอบว่า MT5 version เป็นตัวล่าสุด
4. ลอง login ด้วย MT5 โดยตรงก่อน

---

**สร้างเมื่อ**: 2024-11-07
**อัพเดทล่าสุด**: 2024-11-07