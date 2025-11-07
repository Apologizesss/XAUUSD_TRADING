"""
Daily Trading Update Script
---------------------------
สคริปต์สำหรับ:
1. ดึงข้อมูลราคาใหม่จาก MT5
2. วิเคราะห์ผลการเทรดย้อนหลัง 1 วัน
3. Retrain model ด้วยข้อมูลใหม่
4. สร้างรายงานประจำวัน

วิธีใช้: python daily_update.py
"""

import json
import os
import pickle
from datetime import datetime, timedelta
from pathlib import Path

import MetaTrader5 as mt5
import numpy as np
import pandas as pd

# Import โมดูลที่มีอยู่
from src.data_collection.mt5_collector import MT5Collector
from src.data_collection.news_collector import NewsCollector
from src.features.feature_pipeline import FeaturePipeline
from src.features.news_features import NewsSentimentFeatures
from src.models.data_preprocessor import DataPreprocessor


class DailyUpdater:
    def __init__(self):
        self.data_dir = Path("data")
        self.news_dir = Path("data/news")
        self.results_dir = Path("results")
        self.models_dir = Path("models")
        self.logs_dir = Path("logs")

        # สร้างโฟลเดอร์ถ้ายังไม่มี
        for dir_path in [self.data_dir, self.news_dir, self.results_dir, self.logs_dir]:
            dir_path.mkdir(exist_ok=True)

        self.symbol = "XAUUSD"
        self.timeframe = mt5.TIMEFRAME_M5

        # News collector
        self.news_collector = NewsCollector()
        self.sentiment_features = NewsSentimentFeatures()

    def collect_new_data(self, days=7):
        """ดึงข้อมูลใหม่จาก MT5"""
        print("=" * 60)
        print("📥 ขั้นตอนที่ 1: ดึงข้อมูลใหม่จาก MT5")
        print("=" * 60)

        collector = MT5Collector(symbol=self.symbol, timeframe="M5")

        if not collector.initialize():
            print("[Error] ไม่สามารถเชื่อมต่อ MT5 ได้")
            return None

        if not collector.check_symbol():
            print("[Error] ไม่สามารถเข้าถึงสัญลักษณ์ได้")
            mt5.shutdown()
            return None

        # ดึงข้อมูล 7 วันย้อนหลัง
        end_date = datetime.now()
        start_date = end_date - timedelta(days=days)

        print(
            f"ดึงข้อมูล {self.symbol} จาก {start_date.strftime('%Y-%m-%d')} ถึง {end_date.strftime('%Y-%m-%d')}"
        )

        df = collector.collect_historical_data(
            date_from=start_date,
            date_to=end_date,
        )

        mt5.shutdown()

        if df is not None and len(df) > 0:
            print(f"[OK] ดึงข้อมูลสำเร็จ: {len(df)} แท่งเทียน")

            # เปลี่ยนชื่อ column timestamp เป็น time สำหรับ FeaturePipeline
            if "timestamp" in df.columns and "time" not in df.columns:
                df = df.rename(columns={"timestamp": "time"})
            elif "time" in df.columns and "timestamp" not in df.columns:
                df["timestamp"] = df["time"]

            # บันทึกข้อมูลดิบ
            raw_file = (
                self.data_dir / f"raw_data_{datetime.now().strftime('%Y%m%d')}.csv"
            )
            df.to_csv(raw_file, index=False)
            print(f"[Save] บันทึกไฟล์: {raw_file}")

            return df
        else:
            print("[Error] ไม่สามารถดึงข้อมูลได้")
            return None

    def analyze_trading_performance(self):
        """วิเคราะห์ผลการเทรดจาก log files"""
        print("\n" + "=" * 60)
        print("[Stats] ขั้นตอนที่ 2: วิเคราะห์ผลการเทรด")
        print("=" * 60)

        # ค้นหา trading log files
        log_files = list(self.logs_dir.glob("trading_*.json"))

        if not log_files:
            print("[Warning]  ไม่พบไฟล์ log การเทรด")
            return None

        # รวม log ทั้งหมด
        all_trades = []
        for log_file in sorted(log_files)[-7:]:  # เอาแค่ 7 วันล่าสุด
            try:
                with open(log_file, "r", encoding="utf-8") as f:
                    trades = json.load(f)
                    all_trades.extend(trades)
            except:
                continue

        if not all_trades:
            print("[Warning]  ไม่มีข้อมูลการเทรด")
            return None

        # คำนวณ metrics
        df_trades = pd.DataFrame(all_trades)

        if "profit" not in df_trades.columns:
            print("[Warning]  ข้อมูลไม่ครบถ้วน")
            return None

        total_trades = len(df_trades)
        winning_trades = len(df_trades[df_trades["profit"] > 0])
        losing_trades = len(df_trades[df_trades["profit"] < 0])

        win_rate = (winning_trades / total_trades * 100) if total_trades > 0 else 0

        total_profit = df_trades["profit"].sum()
        avg_profit = (
            df_trades[df_trades["profit"] > 0]["profit"].mean()
            if winning_trades > 0
            else 0
        )
        avg_loss = (
            df_trades[df_trades["profit"] < 0]["profit"].mean()
            if losing_trades > 0
            else 0
        )

        # คำนวณ Max Drawdown
        cumulative_profit = df_trades["profit"].cumsum()
        running_max = cumulative_profit.cummax()
        drawdown = running_max - cumulative_profit
        max_drawdown = drawdown.max() if len(drawdown) > 0 else 0

        metrics = {
            "total_trades": total_trades,
            "winning_trades": winning_trades,
            "losing_trades": losing_trades,
            "win_rate": win_rate,
            "total_profit": total_profit,
            "avg_profit": avg_profit,
            "avg_loss": avg_loss,
            "max_drawdown": max_drawdown,
            "profit_factor": abs(avg_profit / avg_loss) if avg_loss != 0 else 0,
            "last_updated": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        }

        # แสดงผล
        print(f"\n[Chart] สรุปผลการเทรด (รวม {total_trades} ออเดอร์)")
        print("-" * 60)
        print(f"[OK] ชนะ: {winning_trades} ครั้ง | [Error] แพ้: {losing_trades} ครั้ง")
        print(f"[Target] Win Rate: {win_rate:.2f}%")
        print(f"💰 กำไรรวม: ${total_profit:.2f}")
        print(f"[Stats] กำไรเฉลี่ย: ${avg_profit:.2f} | ขาดทุนเฉลี่ย: ${avg_loss:.2f}")
        print(f"[Warning]  Max Drawdown: ${max_drawdown:.2f}")
        print(f"[Chart] Profit Factor: {metrics['profit_factor']:.2f}")

        # บันทึกผล
        report_file = (
            self.results_dir / f"daily_report_{datetime.now().strftime('%Y%m%d')}.json"
        )
        with open(report_file, "w", encoding="utf-8") as f:
            json.dump(metrics, f, indent=4, ensure_ascii=False)
        print(f"\n[Save] บันทึกรายงาน: {report_file}")

        return metrics

    def collect_news(self, days=7):
        """ดึงข่าวและวิเคราะห์ sentiment"""
        print("\n" + "=" * 60)
        print("📰 ขั้นตอนที่ 2.5: ดึงข่าวและวิเคราะห์ Sentiment")
        print("=" * 60)

        try:
            # ดึงข่าว
            df_news = self.news_collector.get_gold_news(days=days)

            if df_news.empty:
                print("⚠️ ไม่สามารถดึงข่าวได้")
                return None

            # บันทึก
            news_file = self.news_dir / f"news_{datetime.now().strftime('%Y%m%d')}.csv"
            df_news.to_csv(news_file, index=False)
            print(f"💾 บันทึกข่าว: {news_file}")
            print(f"   จำนวน: {len(df_news)} บทความ")

            # แสดง sentiment summary
            if "sentiment" in df_news.columns:
                print(f"\n📊 Sentiment Summary:")
                for sentiment, count in df_news["sentiment"].value_counts().items():
                    percentage = (count / len(df_news)) * 100
                    print(f"   {sentiment.capitalize()}: {count} ({percentage:.1f}%)")
                print(f"   Average Polarity: {df_news['polarity'].mean():.4f}")

            return news_file

        except Exception as e:
            print(f"❌ Error collecting news: {e}")
            return None

    def prepare_training_data(self, df, news_file=None):
        """เตรียมข้อมูลสำหรับเทรน"""
        print("\n" + "=" * 60)
        print("[Feature Engineering] ขั้นตอนที่ 3: เตรียมข้อมูลสำหรับเทรน")
        print("=" * 60)

        # ตรวจสอบว่ามี column ที่จำเป็น
        if "timestamp" not in df.columns and "time" in df.columns:
            df["timestamp"] = df["time"]

        print(f"[Stats] ข้อมูลดิบ: {len(df)} แถว, {len(df.columns)} columns")

        # สร้าง features
        pipeline = FeaturePipeline()
        df_features = pipeline.add_features(df)

        print(f"[OK] สร้าง features เสร็จ: {len(df_features.columns)} features")

        # เพิ่ม sentiment features (ถ้ามีข่าว)
        if news_file and news_file.exists():
            print(f"\n📰 เพิ่ม Sentiment Features...")
            try:
                df_features = self.sentiment_features.merge_price_and_news(
                    df_features, str(news_file), windows=[1, 4, 12, 24]
                )
                print(f"✅ เพิ่ม sentiment features สำเร็จ")
                print(f"   Total features: {len(df_features.columns)}")
            except Exception as e:
                print(f"⚠️ ไม่สามารถเพิ่ม sentiment features: {e}")
        else:
            print(f"\n⚠️ ไม่มีข่าว - ข้าม sentiment features")

        # สร้าง target (ราคาขึ้นใน 4 ชั่วโมงข้างหน้า)
        df_features["future_price"] = df_features["close"].shift(-4)
        df_features["target"] = (
            df_features["future_price"] > df_features["close"]
        ).astype(int)

        print(f"[Stats] หลังสร้าง target: {len(df_features)} แถว")
        print(f"   Missing values: {df_features.isnull().sum().sum()} จุด")

        # ลบแถวที่ไม่มีข้อมูลเฉพาะ columns ที่สำคัญ
        important_cols = ["open", "high", "low", "close", "target"]
        df_features = df_features.dropna(subset=important_cols)

        print(f"[OK] เตรียมข้อมูลเสร็จ: {len(df_features)} แถว")

        if len(df_features) > 0:
            print(
                f"[Stats] Target distribution: UP={df_features['target'].sum()}, DOWN={len(df_features) - df_features['target'].sum()}"
            )
        else:
            print("[Warning]  ไม่มีข้อมูลหลังจากทำความสะอาด")

        # บันทึก
        processed_file = (
            self.data_dir / f"processed_data_{datetime.now().strftime('%Y%m%d')}.csv"
        )
        df_features.to_csv(processed_file, index=False)
        print(f"[Save] บันทึกไฟล์: {processed_file}")

        return df_features

    def update_existing_model(self, new_data):
        """อัพเดท model ที่มีอยู่ด้วยข้อมูลใหม่"""
        print("\n" + "=" * 60)
        print("🤖 ขั้นตอนที่ 4: อัพเดท Model")
        print("=" * 60)

        # ค้นหา model ล่าสุด
        model_files = list(self.models_dir.glob("lstm_model_*.keras"))

        if not model_files:
            print("[Warning]  ไม่พบ model ที่มีอยู่")
            print("[Tip] แนะนำ: รันคำสั่ง train_from_config.py เพื่อเทรน model ใหม่")
            return False

        latest_model = sorted(model_files)[-1]
        print(f"📂 พบ model: {latest_model.name}")

        try:
            from tensorflow import keras

            model = keras.models.load_model(latest_model)
            print(f"[OK] โหลด model สำเร็จ")

            # เตรียมข้อมูล
            exclude_cols = [
                "target",
                "future_price",
                "time",
                "timestamp",
                "symbol",
                "timeframe",
            ]
            feature_cols = [col for col in new_data.columns if col not in exclude_cols]

            print(f"[Stats] จำนวน features สำหรับเทรน: {len(feature_cols)}")

            X = new_data[feature_cols].values
            y = new_data["target"].values

            print(f"[Stats] ข้อมูลเทรน: X shape={X.shape}, y shape={y.shape}")

            # Normalize
            from sklearn.preprocessing import StandardScaler

            scaler = StandardScaler()
            X_scaled = scaler.fit_transform(X)

            # Reshape สำหรับ LSTM
            X_scaled = X_scaled.reshape((X_scaled.shape[0], 1, X_scaled.shape[1]))

            # Fine-tune model
            print(f"[Reload] กำลังอัพเดท model ด้วยข้อมูลใหม่...")
            history = model.fit(
                X_scaled, y, epochs=5, batch_size=32, validation_split=0.2, verbose=0
            )

            final_acc = history.history["accuracy"][-1]
            final_val_acc = history.history["val_accuracy"][-1]

            print(f"[OK] อัพเดท model เสร็จสิ้น")
            print(
                f"[Stats] Accuracy: {final_acc:.4f} | Val Accuracy: {final_val_acc:.4f}"
            )

            # บันทึก model ใหม่
            new_model_name = (
                f"lstm_model_updated_{datetime.now().strftime('%Y%m%d')}.keras"
            )
            new_model_path = self.models_dir / new_model_name
            model.save(new_model_path)
            print(f"[Save] บันทึก model ใหม่: {new_model_name}")

            return True

        except Exception as e:
            print(f"[Error] เกิดข้อผิดพลาด: {e}")
            print("[Tip] แนะนำ: รันคำสั่ง train_from_config.py เพื่อเทรน model ใหม่")
            return False

    def create_daily_summary(self, metrics):
        """สร้างสรุปประจำวัน"""
        print("\n" + "=" * 60)
        print("[Note] สร้างรายงานสรุปประจำวัน")
        print("=" * 60)

        summary = f"""
╔════════════════════════════════════════════════════════════╗
║           [Stats] รายงานประจำวัน - Gold Trading Bot           ║
╠════════════════════════════════════════════════════════════╣
║  วันที่: {datetime.now().strftime("%d/%m/%Y %H:%M:%S")}                        ║
╠════════════════════════════════════════════════════════════╣
"""

        if metrics:
            summary += f"""║  [Chart] ผลการเทรด                                             ║
║     • จำนวนออเดอร์: {metrics["total_trades"]:>3} ครั้ง                           ║
║     • ชนะ: {metrics["winning_trades"]:>3} | แพ้: {metrics["losing_trades"]:>3}                             ║
║     • Win Rate: {metrics["win_rate"]:>6.2f}%                                ║
║     • กำไรรวม: ${metrics["total_profit"]:>8.2f}                           ║
║     • Max Drawdown: ${metrics["max_drawdown"]:>8.2f}                       ║
║     • Profit Factor: {metrics["profit_factor"]:>5.2f}                             ║
╠════════════════════════════════════════════════════════════╣
"""

        summary += f"""║  [OK] การอัพเดทข้อมูล                                       ║
║     • ดึงข้อมูลใหม่จาก MT5                                ║
║     • อัพเดท features และ indicators                      ║
║     • Fine-tune model ด้วยข้อมูลใหม่                      ║
╠════════════════════════════════════════════════════════════╣
║  [Tip] คำแนะนำ                                                ║
║     • ตรวจสอบ logs ในโฟลเดอร์ logs/                       ║
║     • ดูรายงานเต็มในโฟลเดอร์ results/                     ║
║     • Model อัพเดทล่าสุดอยู่ในโฟลเดอร์ models/            ║
╚════════════════════════════════════════════════════════════╝
"""

        print(summary)

        # บันทึกรายงาน
        summary_file = (
            self.results_dir / f"summary_{datetime.now().strftime('%Y%m%d')}.txt"
        )
        with open(summary_file, "w", encoding="utf-8") as f:
            f.write(summary)

        return summary

    def run(self):
        """รันกระบวนการทั้งหมด"""
        print("\n" + "[Launch]" * 30)
        print("           DAILY UPDATE SCRIPT - Gold Trading Bot (with News)")
        print("[Launch]" * 30 + "\n")

        try:
            # 1. ดึงข้อมูลราคาใหม่
            df = self.collect_new_data(days=7)

            # 2. วิเคราะห์ผลการเทรด
            metrics = self.analyze_trading_performance()

            # 2.5. ดึงข่าวและวิเคราะห์ sentiment (NEW!)
            news_file = self.collect_news(days=7)

            # 3. เตรียมข้อมูลและ update model (พร้อม sentiment features)
            if df is not None and len(df) > 0:
                df_processed = self.prepare_training_data(df, news_file=news_file)

                if df_processed is not None and len(df_processed) > 50:
                    self.update_existing_model(df_processed)
                elif df_processed is not None and len(df_processed) > 0:
                    print(
                        f"[Warning]  ข้อมูลมีเพียง {len(df_processed)} แถว (ต้องการอย่างน้อย 50 แถว)"
                    )
                else:
                    print("[Warning]  ไม่มีข้อมูลหลังการเตรียม")

            # 4. สร้างรายงาน
            self.create_daily_summary(metrics)

            print("\n" + "=" * 60)
            print("[OK] อัพเดทประจำวันเสร็จสมบูรณ์! (พร้อม News Sentiment)")
            print("=" * 60)

        except Exception as e:
            print(f"\n[Error] เกิดข้อผิดพลาด: {e}")
            import traceback

            traceback.print_exc()


def main():
    """ฟังก์ชันหลัก"""
    updater = DailyUpdater()
    updater.run()


if __name__ == "__main__":
    main()
