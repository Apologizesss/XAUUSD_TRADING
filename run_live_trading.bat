@echo off
REM ======================================================================
REM Live Trading Launcher - Unbuffered Output
REM ======================================================================
REM This script ensures all output is shown immediately (no buffering)
REM ======================================================================

echo.
echo ======================================================================
echo Starting Live Trading Bot...
echo ======================================================================
echo.

REM Run Python with unbuffered output (-u flag)
REM This ensures all print statements show immediately
python -u live_trading.py --interval 300 --threshold 0.70 %*

echo.
echo ======================================================================
echo Live Trading Stopped
echo ======================================================================
echo.
pause
