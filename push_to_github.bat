@echo off
echo ====================================================================
echo PUSH AI GOLD TRADING BOT TO GITHUB
echo ====================================================================
echo.
echo BEFORE RUNNING THIS:
echo 1. Create NEW repository on GitHub: https://github.com/new
echo    - Name: ai-gold-trading-bot
echo    - Private: YES (recommended)
echo    - Do NOT initialize with README
echo.
echo 2. Copy your new repository URL
echo    Example: https://github.com/YOUR-USERNAME/ai-gold-trading-bot.git
echo.
echo ====================================================================
echo.

set /p REPO_URL="Enter your NEW repository URL: "

if "%REPO_URL%"=="" (
    echo ERROR: Repository URL cannot be empty!
    pause
    exit /b 1
)

echo.
echo Repository URL: %REPO_URL%
echo.
echo Press any key to continue with push, or Ctrl+C to cancel...
pause > nul

echo.
echo ====================================================================
echo STEP 1: Checking git status...
echo ====================================================================
git status
if errorlevel 1 (
    echo ERROR: Git repository not initialized!
    pause
    exit /b 1
)

echo.
echo ====================================================================
echo STEP 2: Adding remote repository...
echo ====================================================================
git remote remove origin 2>nul
git remote add origin %REPO_URL%
if errorlevel 1 (
    echo ERROR: Failed to add remote!
    pause
    exit /b 1
)

echo Remote added successfully!

echo.
echo ====================================================================
echo STEP 3: Verifying branch...
echo ====================================================================
git branch -M main
echo Branch set to 'main'

echo.
echo ====================================================================
echo STEP 4: Pushing to GitHub...
echo ====================================================================
echo This may take a moment...
echo.
git push -u origin main

if errorlevel 1 (
    echo.
    echo ====================================================================
    echo ERROR: Push failed!
    echo ====================================================================
    echo.
    echo POSSIBLE CAUSES:
    echo 1. Authentication failed
    echo    - GitHub requires Personal Access Token
    echo    - Generate at: https://github.com/settings/tokens
    echo    - Use token as password when prompted
    echo.
    echo 2. Repository doesn't exist
    echo    - Make sure you created it on GitHub first
    echo    - URL: https://github.com/new
    echo.
    echo 3. Wrong repository URL
    echo    - Check the URL you entered
    echo    - Format: https://github.com/USERNAME/REPO-NAME.git
    echo.
    pause
    exit /b 1
)

echo.
echo ====================================================================
echo SUCCESS! Project pushed to GitHub!
echo ====================================================================
echo.
echo Your repository: %REPO_URL%
echo.
echo IMPORTANT SECURITY CHECK:
echo 1. Go to your GitHub repository
echo 2. Verify config/.env is NOT visible (should be ignored)
echo 3. Only config/.env.example should be visible
echo.
echo NEXT STEPS:
echo 1. Fix MT5 connection (update config/.env with real account number)
echo 2. Test connection: python test_mt5_simple.py
echo 3. Start building the trading bot!
echo.
echo ====================================================================
pause
