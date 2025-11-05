"""
Live Trading System - Execute Real Orders on MT5
================================================
[WARNING] WARNING: This script executes REAL trades on MT5!
Use with Demo Account first to test thoroughly.

Features:
- Real order execution on MT5
- Risk management (position sizing, SL/TP)
- Trade logging and monitoring
- Safety checks and validations
- Emergency stop mechanisms
"""

import sys
from pathlib import Path
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import time
import json
import MetaTrader5 as mt5
from typing import Dict, Optional, List

# Add project root to path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

from inference_pipeline import TradingInference


class LiveTrading:
    """
    Live trading system with real order execution
    """

    def __init__(
        self,
        symbol: str = "XAUUSD",
        timeframe: str = "M5",
        model_path: str = "results/xgboost/xgboost_model.pkl",
        scaler_path: str = "results/xgboost/xgboost_scaler.pkl",
        confidence_threshold: float = 0.70,
        risk_per_trade: float = 0.01,  # 1% risk per trade
        max_positions: int = 5,
        max_daily_loss: float = 0.05,  # 5% max daily loss
        profit_target: float = 5.0,  # Close position at $5 profit
        stop_loss_amount: float = -10.0,  # Close position at -$10 loss
        log_dir: str = "logs/live_trading",
        test_mode: bool = False,  # Force signal for testing
        fixed_lot: float = 0.01,  # Fixed lot size (0.01 lots)
    ):
        """
        Initialize live trading system

        Args:
            symbol: Trading symbol (e.g., "XAUUSD")
            timeframe: Timeframe (e.g., "H1", "M5")
            model_path: Path to trained model
            scaler_path: Path to feature scaler
            confidence_threshold: Minimum confidence (0.70 = 70%)
            risk_per_trade: Risk per trade as fraction (0.01 = 1%)
            max_positions: Maximum open positions
            max_daily_loss: Maximum daily loss as fraction (0.05 = 5%)
            log_dir: Directory for logs
        """
        print("=" * 70)
        print("[WARNING]  LIVE TRADING SYSTEM - REAL MONEY AT RISK [WARNING]")
        print("=" * 70)
        print()

        self.symbol = symbol
        self.timeframe = timeframe
        self.confidence_threshold = confidence_threshold
        self.risk_per_trade = risk_per_trade
        self.max_positions = max_positions
        self.max_daily_loss = max_daily_loss
        self.profit_target = profit_target
        self.stop_loss_amount = stop_loss_amount
        self.test_mode = test_mode
        self.fixed_lot = fixed_lot

        # Setup logging
        self.log_dir = Path(log_dir)
        self.log_dir.mkdir(parents=True, exist_ok=True)

        # Initialize inference pipeline
        self.inference = TradingInference(
            model_path=model_path,
            scaler_path=scaler_path,
            confidence_threshold=confidence_threshold,
            symbol=symbol,
            timeframe=timeframe,
        )

        # Initialize MT5
        if not mt5.initialize():
            raise RuntimeError(f"MT5 initialization failed: {mt5.last_error()}")

        # Get account info
        account_info = mt5.account_info()
        if account_info is None:
            raise RuntimeError("Failed to get account info")

        self.initial_balance = account_info.balance
        self.account_currency = account_info.currency
        self.is_demo = account_info.trade_mode == mt5.ACCOUNT_TRADE_MODE_DEMO

        print(f"Account Type: {'DEMO' if self.is_demo else '[REAL] REAL'}")
        print(f"Balance: {self.initial_balance:.2f} {self.account_currency}")
        print(f"Symbol: {symbol}")
        print(f"Timeframe: {timeframe}")
        print(f"Confidence Threshold: {confidence_threshold:.0%}")
        print(f"Risk per Trade: {risk_per_trade:.0%}")
        print(f"Max Daily Loss: {max_daily_loss:.0%}")
        print(f"Profit Target: ${profit_target:.2f} per position")
        print(f"Stop Loss: ${stop_loss_amount:.2f} per position")
        print()

        # Safety confirmation
        if not self.is_demo:
            print("[WARNING]" * 35)
            print("WARNING: THIS IS A REAL ACCOUNT!")
            print("[WARNING]" * 35)
            print()
            response = input(
                "Are you ABSOLUTELY SURE you want to trade with REAL MONEY? (type 'YES' to continue): "
            )
            if response != "YES":
                print("Live trading cancelled.")
                mt5.shutdown()
                sys.exit(0)
            print()

        # Trading state
        self.trades_today = []
        self.daily_pnl = 0.0
        self.last_check_date = datetime.now().date()
        self.is_trading_enabled = True

        # Load state if exists
        self.state_file = self.log_dir / "live_trading_state.json"
        self.load_state()

        print("[OK] Live trading system initialized")
        print()

    def ensure_mt5_connected(self) -> bool:
        """
        Ensure MT5 is connected, reconnect if necessary

        Returns:
            True if connected, False otherwise
        """
        # Check if already connected
        if mt5.terminal_info() is not None:
            return True

        print("  [WARNING] MT5 connection lost, reconnecting...")

        # Try to reconnect
        if not mt5.initialize():
            print(f"  [ERROR] MT5 reconnection failed: {mt5.last_error()}")
            return False

        print("  [OK] MT5 reconnected successfully")
        return True

    def get_symbol_info(self) -> Optional[Dict]:
        """Get symbol trading information"""
        symbol_info = mt5.symbol_info(self.symbol)
        if symbol_info is None:
            print(f"ERROR: Symbol {self.symbol} not found")
            return None

        if not symbol_info.visible:
            if not mt5.symbol_select(self.symbol, True):
                print(f"ERROR: Failed to select symbol {self.symbol}")
                return None

        return {
            "point": symbol_info.point,
            "digits": symbol_info.digits,
            "trade_contract_size": symbol_info.trade_contract_size,
            "volume_min": symbol_info.volume_min,
            "volume_max": symbol_info.volume_max,
            "volume_step": symbol_info.volume_step,
            "spread": symbol_info.spread,
        }

    def calculate_position_size(self, entry_price: float, stop_loss: float) -> float:
        """
        Calculate position size based on risk management

        Args:
            entry_price: Entry price
            stop_loss: Stop loss price

        Returns:
            Position size in lots
        """
        account_info = mt5.account_info()
        if account_info is None:
            return 0.0

        balance = account_info.balance
        risk_amount = balance * self.risk_per_trade

        # Get symbol info
        symbol_info = self.get_symbol_info()
        if symbol_info is None:
            return 0.0

        # Calculate risk in points
        risk_points = abs(entry_price - stop_loss) / symbol_info["point"]

        # Calculate lot size
        # Risk = Lots * Contract Size * Point Value * Risk Points
        point_value = symbol_info["point"] * symbol_info["trade_contract_size"]
        lots = risk_amount / (risk_points * point_value)

        # Round to volume step
        volume_step = symbol_info["volume_step"]
        lots = round(lots / volume_step) * volume_step

        # Clamp to min/max
        lots = max(symbol_info["volume_min"], min(lots, symbol_info["volume_max"]))

        return lots

    def place_order(
        self,
        direction: str,
        entry_price: float,
        stop_loss: float,
        take_profit: float,
        comment: str = "",
    ) -> Optional[Dict]:
        """
        Place order on MT5

        Args:
            direction: "LONG" or "SHORT"
            entry_price: Entry price
            stop_loss: Stop loss price
            take_profit: Take profit price
            comment: Order comment

        Returns:
            Order result dict or None
        """
        # Ensure MT5 is connected
        if not self.ensure_mt5_connected():
            print(f"  [ERROR] Cannot place order: MT5 not connected")
            return None

        # Use fixed lot size
        lots = self.fixed_lot
        print(f"  [Tip] Using fixed lot size: {lots:.2f}")

        if lots <= 0:
            print(f"  [ERROR] Invalid position size: {lots}")
            return None

        # Get current price
        tick = mt5.symbol_info_tick(self.symbol)
        if tick is None:
            print(f"  [ERROR] Failed to get tick for {self.symbol}")
            return None

        # Determine order type and price
        if direction == "LONG":
            order_type = mt5.ORDER_TYPE_BUY
            price = tick.ask
        elif direction == "SHORT":
            order_type = mt5.ORDER_TYPE_SELL
            price = tick.bid
        else:
            print(f"  [ERROR] Invalid direction: {direction}")
            return None

        # Prepare request
        request = {
            "action": mt5.TRADE_ACTION_DEAL,
            "symbol": self.symbol,
            "volume": lots,
            "type": order_type,
            "price": price,
            "sl": stop_loss,
            "tp": take_profit,
            "deviation": 10,
            "magic": 234000,
            "comment": comment or f"AI_{self.timeframe}",
            "type_time": mt5.ORDER_TIME_GTC,
            "type_filling": mt5.ORDER_FILLING_IOC,
        }

        print(f"  📤 Sending order: {direction} {lots:.2f} lots @ {price:.2f}")
        print(f"     SL: {stop_loss:.2f} | TP: {take_profit:.2f}")

        # DEBUG: Show full request
        print(f"\n  [Info] DEBUG - Order Request:")
        for key, value in request.items():
            print(f"     {key}: {value}")
        print()

        # Send order
        print(f"  [Processing] Calling mt5.order_send()...")
        result = mt5.order_send(request)
        print(f"  [OK] order_send() returned: {result}")

        if result is None:
            print(f"  [ERROR] Order failed: No result from MT5")
            print(f"  [Info] Last error: {mt5.last_error()}")
            return None

        print(f"  [Info] Result retcode: {result.retcode}")
        print(f"  [Info] Expected: {mt5.TRADE_RETCODE_DONE}")

        if result.retcode != mt5.TRADE_RETCODE_DONE:
            print(f"  [ERROR] Order failed!")
            print(f"     Return code: {result.retcode}")
            print(f"     Comment: {result.comment}")
            print(f"     Request ID: {result.request_id}")
            print(f"     Volume: {result.volume}")
            print(f"     Price: {result.price}")
            return None

        print(f"  ✅ Order executed! Ticket: {result.order}")
        print(f"     Volume: {result.volume:.2f} lots")
        print(f"     Price: {result.price:.2f}")
        print()

        # Log trade
        trade_log = {
            "timestamp": datetime.now().isoformat(),
            "ticket": result.order,
            "direction": direction,
            "symbol": self.symbol,
            "volume": result.volume,
            "entry_price": result.price,
            "stop_loss": stop_loss,
            "take_profit": take_profit,
            "comment": comment,
        }

        self.trades_today.append(trade_log)
        self.save_trade_log(trade_log)

        return trade_log

    def check_daily_limits(self) -> bool:
        """
        Check if daily limits are breached

        Returns:
            True if trading is allowed, False otherwise
        """
        # Reset daily counters if new day
        today = datetime.now().date()
        if today != self.last_check_date:
            print(f"\n📅 New trading day: {today}")
            self.trades_today = []
            self.daily_pnl = 0.0
            self.last_check_date = today
            self.is_trading_enabled = True

        # Ensure MT5 is connected
        if not self.ensure_mt5_connected():
            print(f"  [ERROR] MT5 not connected!")
            return False

        # Check daily loss limit
        account_info = mt5.account_info()
        if account_info is None:
            print(f"  [Info] DEBUG: account_info is None after connection check!")
            print(f"  [Info] Terminal info: {mt5.terminal_info()}")
            print(f"  [Info] Last error: {mt5.last_error()}")
            return False

        print(f"  [Info] DEBUG: Account Info")
        print(f"     Initial Balance: {self.initial_balance:.2f}")
        print(f"     Current Balance: {account_info.balance:.2f}")

        daily_loss = self.initial_balance - account_info.balance
        daily_loss_pct = daily_loss / self.initial_balance

        print(f"     Daily Loss: {daily_loss:.2f} ({daily_loss_pct:.2%})")
        print(f"     Max Allowed: {self.max_daily_loss:.2%}")
        print(f"     Trading Enabled: {self.is_trading_enabled}")

        if daily_loss_pct >= self.max_daily_loss:
            if self.is_trading_enabled:
                print(f"\n[Stop] DAILY LOSS LIMIT REACHED: {daily_loss_pct:.2%}")
                print(f"   Trading disabled for today.")
                self.is_trading_enabled = False
            return False

        # Check max positions
        positions = mt5.positions_get(symbol=self.symbol)
        print(f"  [Info] DEBUG: Checking positions for {self.symbol}")
        print(f"     Positions result: {positions}")

        if positions is None:
            print(f"     Positions is None (no positions)")
            num_positions = 0
        else:
            num_positions = len(positions)
            print(f"     Number of positions: {num_positions}")

            if num_positions > 0:
                print(f"     Open positions:")
                for pos in positions:
                    print(
                        f"       Ticket: {pos.ticket}, Type: {pos.type}, Volume: {pos.volume}"
                    )

        print(f"     Max positions allowed: {self.max_positions}")

        if num_positions >= self.max_positions:
            print(
                f"  [WARNING] Max positions reached ({num_positions}/{self.max_positions})"
            )
            return False

        print(f"  [OK] All checks passed!")
        return True

    def process_signal(self, signal: Dict) -> bool:
        """
        Process trading signal and execute if valid

        Args:
            signal: Signal dictionary from inference

        Returns:
            True if order placed, False otherwise
        """
        print(f"\n  [Info] DEBUG: process_signal called")
        print(f"     Direction: {signal.get('direction')}")
        print(f"     should_trade: {signal.get('should_trade', False)}")
        print(f"     entry_price: {signal.get('entry_price')}")
        print(f"     stop_loss: {signal.get('stop_loss')}")
        print(f"     take_profit: {signal.get('take_profit')}")

        if not signal.get("should_trade", False):
            print("  ⚪ No trade signal")
            return False

        direction = signal.get("direction", "NEUTRAL")
        if direction == "NEUTRAL":
            print("  ⚪ Neutral signal - skipping")
            return False

        print(f"  [OK] Non-neutral signal: {direction}")

        # Check daily limits
        print(f"  [Info] Checking daily limits...")
        if not self.check_daily_limits():
            print(f"  [ERROR] Daily limits check failed")
            return False
        print(f"  [OK] Daily limits OK")

        # Extract signal info
        entry_price = signal.get("entry_price")
        stop_loss = signal.get("stop_loss")
        take_profit = signal.get("take_profit")
        confidence = signal.get("confidence", "UNKNOWN")
        prob_up = signal.get("probability_up", 0.5)

        if None in [entry_price, stop_loss, take_profit]:
            print(f"  [ERROR] Invalid signal: Missing price levels")
            print(f"     entry_price: {entry_price}")
            print(f"     stop_loss: {stop_loss}")
            print(f"     take_profit: {take_profit}")
            return False

        print(f"\n  🎯 VALID Signal: {direction}")
        print(f"     Confidence: {confidence}")
        print(f"     Probability: {prob_up:.2%}")
        print(f"     Entry: {entry_price}")
        print(f"     SL: {stop_loss}")
        print(f"     TP: {take_profit}")

        # Place order
        print(f"\n  📞 Calling place_order()...")
        comment = f"{self.timeframe}_{confidence}_{prob_up:.0%}"
        result = self.place_order(
            direction=direction,
            entry_price=entry_price,
            stop_loss=stop_loss,
            take_profit=take_profit,
            comment=comment,
        )

        if result is not None:
            print(f"  ✅ place_order() succeeded!")
            return True
        else:
            print(f"  [ERROR] place_order() failed!")
            return False

    def monitor_positions(self):
        """Monitor and log open positions, close if profit target reached"""
        print(f"\n  [Stats] Monitoring positions...")

        positions = mt5.positions_get(symbol=self.symbol)

        if positions is None:
            print(f"     No positions found (None)")
            return

        if len(positions) == 0:
            print(f"     No open positions (0)")
            return

        print(f"     Found {len(positions)} open position(s)")

        positions_to_close = []

        for pos in positions:
            pnl = pos.profit
            direction = "LONG" if pos.type == mt5.ORDER_TYPE_BUY else "SHORT"
            print(f"   Ticket: {pos.ticket}")
            print(f"   {direction} {pos.volume:.2f} @ {pos.price_open:.2f}")
            print(f"   Current: {pos.price_current:.2f}")
            print(f"   P&L: {pnl:+.2f} {self.account_currency}")

            # Check profit target
            if pnl >= self.profit_target:
                print(
                    f"   🎯 PROFIT TARGET REACHED! (${pnl:.2f} >= ${self.profit_target:.2f})"
                )
                positions_to_close.append(pos)

            # Check stop loss
            elif pnl <= self.stop_loss_amount:
                print(
                    f"   [Stop] STOP LOSS HIT! (${pnl:.2f} <= ${self.stop_loss_amount:.2f})"
                )
                positions_to_close.append(pos)

            print()

        # Close positions that reached profit target
        for pos in positions_to_close:
            self.close_position(pos)

    def run_inference(self) -> Optional[Dict]:
        """Run inference and generate signal"""
        try:
            # Fetch live data
            df = self.inference.fetch_live_data(bars=300)
            if df is None:
                return None

            # Calculate features
            df_featured = self.inference.calculate_technical_indicators(df)
            if df_featured is None:
                return None

            # Prepare features
            features = self.inference.prepare_features_for_prediction(df_featured)
            if features is None:
                return None

            # Make prediction
            prob_up, predicted_class = self.inference.make_prediction(features)

            # Generate signal
            signal = self.inference.generate_signal(df_featured, prob_up)
            signal["probability_up"] = float(prob_up)

            # TEST MODE: Force a signal for testing
            if self.test_mode and signal["direction"] == "NEUTRAL":
                print("\n  🧪 TEST MODE: Forcing LONG signal for testing")
                latest = df_featured.iloc[-1]
                current_price = latest["close"]
                atr = latest.get("ATR_14", latest.get("atr_14", 20))

                signal["direction"] = "LONG"
                signal["should_trade"] = True
                signal["confidence"] = "TEST"
                signal["entry_price"] = float(current_price)
                signal["stop_loss"] = float(current_price - atr)
                signal["take_profit"] = float(current_price + atr * 2)
                signal["risk_reward_ratio"] = 2.0
                signal["reason"] = "TEST MODE - Forced signal"

            return signal

        except Exception as e:
            print(f"  [ERROR] Inference error: {e}")
            import traceback

            traceback.print_exc()
            return None

    def save_trade_log(self, trade: Dict):
        """Save trade to CSV log"""
        log_file = self.log_dir / f"trades_{datetime.now().strftime('%Y%m')}.csv"

        df = pd.DataFrame([trade])

        if log_file.exists():
            df.to_csv(log_file, mode="a", header=False, index=False)
        else:
            df.to_csv(log_file, index=False)

    def save_state(self):
        """Save trading state"""
        state = {
            "last_update": datetime.now().isoformat(),
            "initial_balance": self.initial_balance,
            "trades_today": self.trades_today,
            "daily_pnl": self.daily_pnl,
            "last_check_date": self.last_check_date.isoformat(),
            "is_trading_enabled": self.is_trading_enabled,
        }

        with open(self.state_file, "w") as f:
            json.dump(state, f, indent=2)

    def load_state(self):
        """Load trading state"""
        if not self.state_file.exists():
            return

        try:
            with open(self.state_file, "r") as f:
                state = json.load(f)

            self.trades_today = state.get("trades_today", [])
            self.daily_pnl = state.get("daily_pnl", 0.0)
            last_date = state.get("last_check_date")
            if last_date:
                self.last_check_date = datetime.fromisoformat(last_date).date()
            self.is_trading_enabled = state.get("is_trading_enabled", True)

            print("[OK] State loaded from previous session")
        except Exception as e:
            print(f"Warning: Could not load state: {e}")

    def run(
        self, check_interval_seconds: int = 300, duration_minutes: Optional[int] = None
    ):
        """
        Run live trading loop

        Args:
            check_interval_seconds: Seconds between checks (300 = 5 min)
            duration_minutes: Run duration in minutes (None = indefinite)
        """
        print("=" * 70)
        print("[Launch] STARTING LIVE TRADING")
        print("=" * 70)
        print(f"Check interval: {check_interval_seconds}s")
        print(
            f"Duration: {'Indefinite' if duration_minutes is None else f'{duration_minutes} minutes'}"
        )
        print()
        print("Press Ctrl+C to stop")
        print()

        start_time = datetime.now()
        check_count = 0

        try:
            while True:
                check_count += 1
                current_time = datetime.now()

                print(
                    f"[{current_time.strftime('%Y-%m-%d %H:%M:%S')}] Check #{check_count}"
                )

                # Check duration
                if duration_minutes is not None:
                    elapsed = (current_time - start_time).total_seconds() / 60
                    if elapsed >= duration_minutes:
                        print(
                            f"\n[Time] Duration limit reached ({duration_minutes} minutes)"
                        )
                        break

                # Run inference
                print("  [Predict] Running inference...")
                signal = self.run_inference()

                if signal is not None:
                    # Process signal
                    self.process_signal(signal)
                else:
                    print("  [WARNING] No signal generated")

                # Monitor positions
                self.monitor_positions()

                # Save state
                self.save_state()

                # Show account status
                account_info = mt5.account_info()
                if account_info:
                    print(
                        f"  [Money] Balance: {account_info.balance:.2f} {self.account_currency}"
                    )
                    print(
                        f"  📈 Equity: {account_info.equity:.2f} {self.account_currency}"
                    )
                    pnl_today = account_info.balance - self.initial_balance
                    print(
                        f"  {'[Down]' if pnl_today < 0 else '[Stats]'} P&L Today: {pnl_today:+.2f} {self.account_currency}"
                    )

                print()

                # Wait for next check
                print(f"  [Wait] Next check in {check_interval_seconds}s...")
                time.sleep(check_interval_seconds)

        except KeyboardInterrupt:
            print("\n\n[Stop] Live trading stopped by user")
        except Exception as e:
            print(f"\n\n[ERROR] Error: {e}")
            import traceback

            traceback.print_exc()
        finally:
            self.cleanup()

    def cleanup(self):
        """Cleanup and shutdown"""
        print("\n" + "=" * 70)
        print("SHUTTING DOWN")
        print("=" * 70)

        # Save final state
        self.save_state()

        # Show final stats
        account_info = mt5.account_info()
        if account_info:
            final_balance = account_info.balance
            total_pnl = final_balance - self.initial_balance
            print(
                f"\nInitial Balance: {self.initial_balance:.2f} {self.account_currency}"
            )
            print(f"Final Balance:   {final_balance:.2f} {self.account_currency}")
            print(
                f"Total P&L:       {total_pnl:+.2f} {self.account_currency} ({total_pnl / self.initial_balance * 100:+.2f}%)"
            )
            print(f"Trades Today:    {len(self.trades_today)}")

        # Close positions (optional - comment out if you want to keep them)
        # self.close_all_positions()

        mt5.shutdown()
        print("\n[OK] MT5 connection closed")
        print("[OK] Live trading stopped safely")

    def close_all_positions(self):
        """Close all open positions (emergency function)"""
        positions = mt5.positions_get(symbol=self.symbol)

        if positions is None or len(positions) == 0:
            print("No positions to close")
            return

        print(f"\n[WARNING] Closing {len(positions)} positions...")

        for pos in positions:
            direction = "SELL" if pos.type == mt5.ORDER_TYPE_BUY else "BUY"
            order_type = (
                mt5.ORDER_TYPE_SELL
                if pos.type == mt5.ORDER_TYPE_BUY
                else mt5.ORDER_TYPE_BUY
            )

            tick = mt5.symbol_info_tick(self.symbol)
            price = tick.bid if pos.type == mt5.ORDER_TYPE_BUY else tick.ask

            request = {
                "action": mt5.TRADE_ACTION_DEAL,
                "symbol": self.symbol,
                "volume": pos.volume,
                "type": order_type,
                "position": pos.ticket,
                "price": price,
                "deviation": 10,
                "magic": 234000,
                "comment": "Close all",
                "type_time": mt5.ORDER_TIME_GTC,
                "type_filling": mt5.ORDER_FILLING_IOC,
            }

            result = mt5.order_send(request)
            if result.retcode == mt5.TRADE_RETCODE_DONE:
                print(f"  [OK] Closed position {pos.ticket}")
            else:
                print(f"  ✗ Failed to close {pos.ticket}: {result.comment}")

    def close_position(self, position):
        """
        Close a specific position

        Args:
            position: Position object from MT5
        """
        if not self.ensure_mt5_connected():
            print(f"  [ERROR] Cannot close position: MT5 not connected")
            return False

        ticket = position.ticket
        volume = position.volume
        pos_type = position.type

        # Determine closing order type (opposite of position)
        close_type = (
            mt5.ORDER_TYPE_SELL
            if pos_type == mt5.ORDER_TYPE_BUY
            else mt5.ORDER_TYPE_BUY
        )

        # Get current price
        tick = mt5.symbol_info_tick(self.symbol)
        if tick is None:
            print(f"  [ERROR] Failed to get tick for closing position {ticket}")
            return False

        price = tick.bid if pos_type == mt5.ORDER_TYPE_BUY else tick.ask

        # Prepare close request
        request = {
            "action": mt5.TRADE_ACTION_DEAL,
            "symbol": self.symbol,
            "volume": volume,
            "type": close_type,
            "position": ticket,
            "price": price,
            "deviation": 10,
            "magic": 234000,
            "comment": f"TP_${self.profit_target}",
            "type_time": mt5.ORDER_TIME_GTC,
            "type_filling": mt5.ORDER_FILLING_IOC,
        }

        print(f"  [Processing] Closing position {ticket}...")
        result = mt5.order_send(request)

        if result is None:
            print(f"  [ERROR] Close failed: No result from MT5")
            return False

        if result.retcode != mt5.TRADE_RETCODE_DONE:
            print(f"  [ERROR] Close failed: {result.retcode} - {result.comment}")
            return False

        print(f"  ✅ Position {ticket} closed successfully!")
        print(f"     Final P&L: {position.profit:+.2f} {self.account_currency}")
        return True


def main():
    import argparse

    parser = argparse.ArgumentParser(
        description="Live trading with real order execution"
    )
    parser.add_argument("--symbol", "-s", default="XAUUSD", help="Trading symbol")
    parser.add_argument(
        "--timeframe", "-t", default="M5", help="Timeframe (M5, H1, H4)"
    )
    parser.add_argument(
        "--threshold",
        type=float,
        default=0.70,
        help="Confidence threshold (0.70 = 70%)",
    )
    parser.add_argument(
        "--risk",
        type=float,
        default=0.01,
        help="Risk per trade (0.01 = 1%%)",
    )
    parser.add_argument(
        "--max-loss",
        type=float,
        default=0.05,
        help="Max daily loss (0.05 = 5%%)",
    )
    parser.add_argument(
        "--interval",
        "-i",
        type=int,
        default=300,
        help="Check interval in seconds",
    )
    parser.add_argument(
        "--duration",
        "-d",
        type=int,
        help="Duration in minutes (default: run forever)",
    )
    parser.add_argument(
        "--test",
        action="store_true",
        help="Test mode - force a signal for testing",
    )

    args = parser.parse_args()

    # Create live trading system
    trader = LiveTrading(
        symbol=args.symbol,
        timeframe=args.timeframe,
        confidence_threshold=args.threshold,
        risk_per_trade=args.risk,
        max_daily_loss=args.max_loss,
        profit_target=5.0,  # Close at $5 profit
        stop_loss_amount=-10.0,  # Close at -$10 loss
        test_mode=args.test,
        fixed_lot=0.01,  # Fixed 0.01 lots per trade
    )

    # Run live trading
    trader.run(check_interval_seconds=args.interval, duration_minutes=args.duration)


if __name__ == "__main__":
    main()
