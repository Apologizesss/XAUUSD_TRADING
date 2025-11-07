#!/bin/bash

echo "================================================================================"
echo "                      AI GOLD BOT - COMPLETE INSTALLATION"
echo "================================================================================"
echo ""

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Check if Python is installed
if ! command -v python3 &> /dev/null; then
    echo -e "${RED}[ERROR] Python 3 is not installed!${NC}"
    echo ""
    echo "Please install Python 3.9-3.11:"
    echo "  Ubuntu/Debian: sudo apt update && sudo apt install python3 python3-pip python3-venv"
    echo "  macOS: brew install python@3.11"
    echo "  Or visit: https://www.python.org/downloads/"
    exit 1
fi

# Get Python version
PYTHON_VERSION=$(python3 --version | cut -d' ' -f2)
echo -e "${GREEN}[OK] Found Python $PYTHON_VERSION${NC}"
echo ""

# Check Python version compatibility
echo "Checking Python compatibility..."
python3 -c "import sys; exit(0 if (3,9) <= sys.version_info < (3,12) else 1)"
if [ $? -ne 0 ]; then
    echo -e "${YELLOW}[WARNING] Python version may not be fully compatible!${NC}"
    echo "Recommended: Python 3.9, 3.10, or 3.11"
    echo "Current: Python $PYTHON_VERSION"
    echo ""
    read -p "Continue anyway? (y/n): " -n 1 -r
    echo ""
    if [[ ! $REPLY =~ ^[Yy]$ ]]; then
        exit 1
    fi
fi

echo "================================================================================"
echo "STEP 1: Creating Virtual Environment"
echo "================================================================================"
echo ""

# Check if venv exists
if [ -d "venv" ]; then
    echo "Virtual environment already exists."
    read -p "Do you want to delete and recreate it? (y/n): " -n 1 -r
    echo ""
    if [[ $REPLY =~ ^[Yy]$ ]]; then
        echo "Removing old virtual environment..."
        rm -rf venv
        echo ""
    fi
fi

if [ ! -d "venv" ]; then
    echo "Creating new virtual environment..."
    python3 -m venv venv
    if [ $? -ne 0 ]; then
        echo -e "${RED}[ERROR] Failed to create virtual environment!${NC}"
        exit 1
    fi
    echo -e "${GREEN}[OK] Virtual environment created${NC}"
fi
echo ""

# Activate virtual environment
echo "Activating virtual environment..."
source venv/bin/activate
if [ $? -ne 0 ]; then
    echo -e "${RED}[ERROR] Failed to activate virtual environment!${NC}"
    exit 1
fi
echo -e "${GREEN}[OK] Virtual environment activated${NC}"
echo ""

echo "================================================================================"
echo "STEP 2: Upgrading Core Tools"
echo "================================================================================"
echo ""

echo "Upgrading pip, setuptools, and wheel..."
python -m pip install --upgrade pip setuptools wheel
echo ""

echo "================================================================================"
echo "STEP 3: Installing System Dependencies (if needed)"
echo "================================================================================"
echo ""

# Detect OS
if [[ "$OSTYPE" == "linux-gnu"* ]]; then
    echo "Detected Linux system"
    echo "Installing system dependencies for TA-Lib..."
    if command -v apt-get &> /dev/null; then
        sudo apt-get update
        sudo apt-get install -y build-essential wget
        sudo apt-get install -y libta-lib0-dev
    elif command -v yum &> /dev/null; then
        sudo yum groupinstall -y "Development Tools"
        sudo yum install -y wget
    fi
elif [[ "$OSTYPE" == "darwin"* ]]; then
    echo "Detected macOS system"
    if command -v brew &> /dev/null; then
        echo "Installing TA-Lib via Homebrew..."
        brew install ta-lib
    else
        echo -e "${YELLOW}[WARNING] Homebrew not found. Please install Homebrew first.${NC}"
        echo "Visit: https://brew.sh/"
    fi
fi
echo ""

echo "================================================================================"
echo "STEP 4: Installing Core Dependencies"
echo "================================================================================"
echo ""

echo "[1/10] Installing numpy (numerical computing)..."
pip install numpy==1.26.4
echo ""

echo "[2/10] Installing pandas (data manipulation)..."
pip install pandas==2.2.3
echo ""

echo "[3/10] Installing scikit-learn (machine learning)..."
pip install scikit-learn==1.6.1
echo ""

echo "================================================================================"
echo "STEP 5: Installing Trading & Data Collection Packages"
echo "================================================================================"
echo ""

echo "[4/10] Installing MetaTrader5..."
pip install MetaTrader5==5.0.5388
if [ $? -ne 0 ]; then
    echo -e "${YELLOW}[WARNING] MetaTrader5 may not be available on Linux/Mac${NC}"
fi
echo ""

echo "[5/10] Installing data collection tools..."
pip install beautifulsoup4==4.12.3 requests==2.32.3 yfinance==0.2.50 newsapi-python==0.2.7
echo ""

echo "================================================================================"
echo "STEP 6: Installing Machine Learning Libraries"
echo "================================================================================"
echo ""

echo "[6/10] Installing XGBoost..."
pip install xgboost==2.1.3
echo ""

echo "[7/10] Installing TensorFlow (this may take a while)..."
pip install tensorflow==2.18.0
if [ $? -ne 0 ]; then
    echo -e "${YELLOW}[WARNING] TensorFlow 2.18.0 failed, trying older version...${NC}"
    pip install tensorflow==2.13.0
fi
echo ""

echo "[8/10] Installing PyTorch (this may take a while)..."
# Detect if we have CUDA
if command -v nvidia-smi &> /dev/null; then
    echo "NVIDIA GPU detected, installing PyTorch with CUDA support..."
    pip install torch==2.5.1 torchvision==0.20.1 --index-url https://download.pytorch.org/whl/cu121
else
    echo "No NVIDIA GPU detected, installing CPU-only PyTorch..."
    pip install torch==2.5.1 torchvision==0.20.1 --index-url https://download.pytorch.org/whl/cpu
fi
echo ""

echo "[9/10] Installing Transformers for NLP..."
pip install transformers==4.47.1
echo ""

echo "================================================================================"
echo "STEP 7: Installing Technical Analysis Libraries"
echo "================================================================================"
echo ""

echo "Installing pandas-ta..."
pip install pandas-ta==0.4.71b0
echo ""

echo "Installing TA-Lib..."
pip install TA-Lib
if [ $? -ne 0 ]; then
    echo -e "${YELLOW}[WARNING] TA-Lib installation failed${NC}"
    echo "For Ubuntu/Debian: sudo apt-get install libta-lib0-dev"
    echo "For macOS: brew install ta-lib"
    echo "Then try: pip install TA-Lib"
fi
echo ""

echo "================================================================================"
echo "STEP 8: Installing Remaining Dependencies"
echo "================================================================================"
echo ""

echo "[10/10] Installing all remaining packages from requirements.txt..."
pip install -r requirements.txt --no-deps 2>/dev/null || true
echo ""

echo "Installing visualization tools..."
pip install matplotlib==3.10.0 seaborn==0.13.2 plotly==5.24.1 mplfinance==0.12.10b0
echo ""

echo "Installing utilities..."
pip install python-telegram-bot==21.9 python-dotenv==1.0.1 loguru==0.7.3 tqdm==4.67.1 joblib==1.4.2
echo ""

echo "Installing NLP tools..."
pip install nltk==3.9.1 textblob==0.18.0
echo ""

echo "Installing additional ML libraries..."
pip install lightgbm==4.5.0 statsmodels==0.14.4 scipy==1.14.1
echo ""

echo "================================================================================"
echo "STEP 9: Verification"
echo "================================================================================"
echo ""

# Create test script
cat > test_installation.py << 'EOF'
import sys
print("Python version:", sys.version)
print("="*60)

# Test core imports
packages = {
    'pandas': 'pd',
    'numpy': 'np',
    'sklearn': None,
    'tensorflow': 'tf',
    'xgboost': 'xgb',
    'MetaTrader5': 'mt5',
    'transformers': None,
    'torch': None,
    'talib': None
}

for package, alias in packages.items():
    try:
        if alias:
            exec(f"import {package} as {alias}")
        else:
            exec(f"import {package}")

        # Get version if available
        try:
            if alias:
                version = eval(f"{alias}.__version__")
            else:
                version = eval(f"{package}.__version__")
            print(f"[OK] {package} {version}")
        except:
            print(f"[OK] {package}")
    except ImportError:
        if package == 'talib':
            print(f"[WARNING] {package} not installed (optional)")
        else:
            print(f"[FAIL] {package}")

print("="*60)
print("Installation test complete!")
EOF

echo "Running installation test..."
echo ""
python test_installation.py
echo ""

# Cleanup test file
rm -f test_installation.py

echo "================================================================================"
echo "STEP 10: Setup Configuration"
echo "================================================================================"
echo ""

# Check if config directory exists
if [ ! -d "config" ]; then
    echo "Creating config directory..."
    mkdir -p config
fi

# Check if .env exists
if [ ! -f "config/.env" ]; then
    echo ""
    echo "Creating sample .env file..."
    cat > config/.env << 'EOF'
# MetaTrader 5 Credentials
MT5_LOGIN=your_demo_account_number
MT5_PASSWORD=your_demo_password
MT5_SERVER=your_broker_server

# News API (get free key from https://newsapi.org)
NEWS_API_KEY=your_newsapi_key_here

# Telegram Bot (optional)
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
EOF
    echo -e "${GREEN}[OK] Created sample config/.env file${NC}"
    echo ""
    echo -e "${YELLOW}IMPORTANT: Edit config/.env with your actual credentials!${NC}"
else
    echo -e "${GREEN}[OK] config/.env already exists${NC}"
fi

# Create necessary directories
echo ""
echo "Creating project directories..."
mkdir -p data logs models results
echo -e "${GREEN}[OK] Project directories created${NC}"

echo ""
echo "================================================================================"
echo "INSTALLATION COMPLETE!"
echo "================================================================================"
echo ""
echo -e "${GREEN}Successfully installed AI Gold Trading Bot dependencies!${NC}"
echo ""
echo "Next steps:"
echo ""
echo "1. Edit config/.env with your MT5 credentials and API keys:"
echo "   nano config/.env"
echo ""
echo "2. Test MT5 connection:"
echo "   python -c \"import MetaTrader5 as mt5; mt5.initialize(); print('MT5 OK')\""
echo ""
echo "3. Collect initial data:"
echo "   python collect_more_data.py"
echo ""
echo "4. Train models:"
echo "   python train_xgboost.py"
echo ""
echo "5. Start paper trading:"
echo "   python paper_trading.py"
echo ""
echo "================================================================================"
echo ""
echo "Virtual environment is activated."
echo "To deactivate: deactivate"
echo "To reactivate later: source venv/bin/activate"
echo ""
echo -e "${YELLOW}Note: Some packages like MetaTrader5 may not work on Linux/Mac.${NC}"
echo -e "${YELLOW}Consider using Windows or a Windows VM for full functionality.${NC}"
echo ""
