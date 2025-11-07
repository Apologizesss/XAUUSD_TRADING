@echo off
setlocal enabledelayedexpansion

echo ================================================================================
echo                      AI GOLD BOT - COMPLETE INSTALLATION
echo ================================================================================
echo.

REM Check if Python is installed
python --version >nul 2>&1
if errorlevel 1 (
    echo [ERROR] Python is not installed or not in PATH!
    echo.
    echo Please install Python 3.9-3.11 from: https://www.python.org/downloads/
    echo Make sure to check "Add Python to PATH" during installation
    pause
    exit /b 1
)

REM Get Python version
for /f "tokens=2" %%i in ('python --version 2^>^&1') do set PYTHON_VERSION=%%i
echo [OK] Found Python %PYTHON_VERSION%
echo.

REM Check Python version compatibility
echo Checking Python compatibility...
python -c "import sys; exit(0 if (3,9) <= sys.version_info < (3,12) else 1)"
if errorlevel 1 (
    echo [WARNING] Python version may not be fully compatible!
    echo Recommended: Python 3.9, 3.10, or 3.11
    echo Current: Python %PYTHON_VERSION%
    echo.
    choice /C YN /M "Continue anyway?"
    if errorlevel 2 exit /b 1
)

echo ================================================================================
echo STEP 1: Creating Virtual Environment
echo ================================================================================
echo.

REM Check if venv exists
if exist "venv" (
    echo Virtual environment already exists.
    choice /C YN /M "Do you want to delete and recreate it?"
    if errorlevel 2 goto :activate_venv
    echo Removing old virtual environment...
    rmdir /s /q venv
    echo.
)

echo Creating new virtual environment...
python -m venv venv
if errorlevel 1 (
    echo [ERROR] Failed to create virtual environment!
    pause
    exit /b 1
)
echo [OK] Virtual environment created
echo.

:activate_venv
echo Activating virtual environment...
call venv\Scripts\activate.bat
if errorlevel 1 (
    echo [ERROR] Failed to activate virtual environment!
    pause
    exit /b 1
)
echo [OK] Virtual environment activated
echo.

echo ================================================================================
echo STEP 2: Upgrading Core Tools
echo ================================================================================
echo.

echo Upgrading pip, setuptools, and wheel...
python -m pip install --upgrade pip setuptools wheel
if errorlevel 1 (
    echo [WARNING] Failed to upgrade core tools, continuing...
)
echo.

echo ================================================================================
echo STEP 3: Installing Core Dependencies
echo ================================================================================
echo.

echo Installing essential packages first...
echo.

REM Install core packages first to avoid conflicts
echo [1/10] Installing numpy (numerical computing)...
pip install numpy==1.26.4
if errorlevel 1 echo [WARNING] numpy installation had issues

echo [2/10] Installing pandas (data manipulation)...
pip install pandas==2.2.3
if errorlevel 1 echo [WARNING] pandas installation had issues

echo [3/10] Installing scikit-learn (machine learning)...
pip install scikit-learn==1.6.1
if errorlevel 1 echo [WARNING] scikit-learn installation had issues

echo.
echo ================================================================================
echo STEP 4: Installing Trading & Data Collection Packages
echo ================================================================================
echo.

echo [4/10] Installing MetaTrader5...
pip install MetaTrader5==5.0.5388
if errorlevel 1 echo [WARNING] MetaTrader5 installation had issues

echo [5/10] Installing data collection tools...
pip install beautifulsoup4==4.12.3 requests==2.32.3 yfinance==0.2.50 newsapi-python==0.2.7
if errorlevel 1 echo [WARNING] Data collection tools installation had issues

echo.
echo ================================================================================
echo STEP 5: Installing Machine Learning Libraries
echo ================================================================================
echo.

echo [6/10] Installing XGBoost...
pip install xgboost==2.1.3
if errorlevel 1 echo [WARNING] XGBoost installation had issues

echo [7/10] Installing TensorFlow (this may take a while)...
pip install tensorflow==2.18.0
if errorlevel 1 (
    echo [WARNING] TensorFlow 2.18.0 failed, trying older version...
    pip install tensorflow==2.13.0
)

echo [8/10] Installing PyTorch (this may take a while)...
pip install torch==2.5.1 torchvision==0.20.1
if errorlevel 1 (
    echo [WARNING] PyTorch installation had issues
    echo You may need to install from: https://pytorch.org/
)

echo [9/10] Installing Transformers for NLP...
pip install transformers==4.47.1
if errorlevel 1 echo [WARNING] Transformers installation had issues

echo.
echo ================================================================================
echo STEP 6: Installing Technical Analysis Libraries
echo ================================================================================
echo.

echo Installing pandas-ta...
pip install pandas-ta==0.4.71b0
if errorlevel 1 echo [WARNING] pandas-ta installation had issues

echo.
echo Installing TA-Lib (special process)...
echo.

REM Check Python version for TA-Lib wheel
for /f "tokens=1,2 delims=." %%a in ("%PYTHON_VERSION%") do (
    set PYTHON_MAJOR=%%a
    set PYTHON_MINOR=%%b
)

REM Check if TA-Lib wheel exists
if exist "ta_lib-0.6.8-cp312-cp312-win_amd64.whl" (
    echo Found local TA-Lib wheel, installing...
    pip install ta_lib-0.6.8-cp312-cp312-win_amd64.whl
) else (
    echo.
    echo [INFO] TA-Lib wheel not found locally.
    echo.
    echo To install TA-Lib:
    echo 1. Download from: https://www.lfd.uci.edu/~gohlke/pythonlibs/#ta-lib
    echo 2. Choose the file matching Python %PYTHON_MAJOR%.%PYTHON_MINOR%:
    echo    - Python 3.9:  TA_Lib-0.4.32-cp39-cp39-win_amd64.whl
    echo    - Python 3.10: TA_Lib-0.4.32-cp310-cp310-win_amd64.whl
    echo    - Python 3.11: TA_Lib-0.4.32-cp311-cp311-win_amd64.whl
    echo    - Python 3.12: TA_Lib-0.4.32-cp312-cp312-win_amd64.whl
    echo 3. Run: pip install [downloaded_file.whl]
    echo.
    echo Trying pip install (may fail on Windows)...
    pip install TA-Lib
)

echo.
echo ================================================================================
echo STEP 7: Installing Remaining Dependencies
echo ================================================================================
echo.

echo [10/10] Installing all remaining packages from requirements.txt...
pip install -r requirements.txt --no-deps 2>nul
echo.

echo ================================================================================
echo STEP 8: Installing Additional Tools
echo ================================================================================
echo.

echo Installing visualization tools...
pip install matplotlib==3.10.0 seaborn==0.13.2 plotly==5.24.1 mplfinance==0.12.10b0
if errorlevel 1 echo [WARNING] Some visualization tools had issues

echo Installing utilities...
pip install python-telegram-bot==21.9 python-dotenv==1.0.1 loguru==0.7.3 tqdm==4.67.1
if errorlevel 1 echo [WARNING] Some utilities had issues

echo Installing NLP tools...
pip install nltk==3.9.1 textblob==0.18.0
if errorlevel 1 echo [WARNING] Some NLP tools had issues

echo.
echo ================================================================================
echo STEP 9: Verification
echo ================================================================================
echo.

echo Creating test_installation.py...
(
echo import sys
echo print^("Python version:", sys.version^)
echo print^("="*60^)
echo.
echo # Test core imports
echo try:
echo     import pandas as pd
echo     print^("[OK] pandas", pd.__version__^)
echo except: print^("[FAIL] pandas"^)
echo.
echo try:
echo     import numpy as np
echo     print^("[OK] numpy", np.__version__^)
echo except: print^("[FAIL] numpy"^)
echo.
echo try:
echo     import sklearn
echo     print^("[OK] scikit-learn", sklearn.__version__^)
echo except: print^("[FAIL] scikit-learn"^)
echo.
echo try:
echo     import tensorflow as tf
echo     print^("[OK] tensorflow", tf.__version__^)
echo except: print^("[FAIL] tensorflow"^)
echo.
echo try:
echo     import xgboost as xgb
echo     print^("[OK] xgboost", xgb.__version__^)
echo except: print^("[FAIL] xgboost"^)
echo.
echo try:
echo     import MetaTrader5 as mt5
echo     print^("[OK] MetaTrader5"^)
echo except: print^("[FAIL] MetaTrader5"^)
echo.
echo try:
echo     import transformers
echo     print^("[OK] transformers", transformers.__version__^)
echo except: print^("[FAIL] transformers"^)
echo.
echo try:
echo     import torch
echo     print^("[OK] torch", torch.__version__^)
echo except: print^("[FAIL] torch"^)
echo.
echo try:
echo     import talib
echo     print^("[OK] TA-Lib"^)
echo except:
echo     print^("[WARNING] TA-Lib not installed (optional^)"^)
echo.
echo print^("="*60^)
echo print^("Installation test complete!"^)
) > test_installation.py

echo Running installation test...
echo.
python test_installation.py
echo.

echo ================================================================================
echo STEP 10: Setup Configuration
echo ================================================================================
echo.

REM Check if config directory exists
if not exist "config" (
    echo Creating config directory...
    mkdir config
)

REM Check if .env exists
if not exist "config\.env" (
    echo.
    echo Creating sample .env file...
    (
    echo # MetaTrader 5 Credentials
    echo MT5_LOGIN=your_demo_account_number
    echo MT5_PASSWORD=your_demo_password
    echo MT5_SERVER=your_broker_server
    echo.
    echo # News API (get free key from https://newsapi.org^)
    echo NEWS_API_KEY=your_newsapi_key_here
    echo.
    echo # Telegram Bot (optional^)
    echo TELEGRAM_BOT_TOKEN=your_telegram_bot_token
    echo TELEGRAM_CHAT_ID=your_telegram_chat_id
    echo.
    echo # Trading Parameters
    echo INITIAL_CAPITAL=10000.0
    echo MAX_RISK_PER_TRADE=0.02
    echo MAX_DAILY_LOSS=0.05
    echo MAX_DRAWDOWN=0.15
    echo.
    echo # Database
    echo DATABASE_PATH=data/trading.db
    echo.
    echo # Logging
    echo LOG_LEVEL=INFO
    ) > config\.env
    echo [OK] Created sample config\.env file
    echo.
    echo IMPORTANT: Edit config\.env with your actual credentials!
) else (
    echo [OK] config\.env already exists
)

echo.
echo ================================================================================
echo INSTALLATION COMPLETE!
echo ================================================================================
echo.
echo Next steps:
echo.
echo 1. Edit config\.env with your MT5 credentials and API keys
echo.
echo 2. Test MT5 connection:
echo    python -c "import MetaTrader5 as mt5; mt5.initialize(); print('MT5 OK')"
echo.
echo 3. Collect initial data:
echo    python collect_more_data.py
echo.
echo 4. Train models:
echo    python train_xgboost.py
echo.
echo 5. Start paper trading:
echo    python paper_trading.py
echo.
echo ================================================================================
echo.
echo Virtual environment is activated. To deactivate: deactivate
echo To reactivate later: venv\Scripts\activate
echo.

REM Cleanup
del test_installation.py 2>nul

pause
