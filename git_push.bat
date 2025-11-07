@echo off
chcp 65001 >nul
setlocal enabledelayedexpansion

echo.
echo ======================================================================
echo Git Push to GitHub - XAUUSD Trading Bot
echo ======================================================================
echo.

REM Step 1: Add all files
echo [1/4] Adding all files to staging...
git add -A
if errorlevel 1 (
    echo ERROR: Failed to add files!
    pause
    exit /b 1
)
echo Done!
echo.

REM Step 2: Commit changes
echo [2/4] Committing changes...
git commit -m "Update live trading system"
if errorlevel 1 (
    echo WARNING: Nothing to commit or commit failed
)
echo Done!
echo.

REM Step 3: Push to GitHub
echo [3/4] Pushing to GitHub...
echo Repository: https://github.com/Apologizesss/XAUUSD_TRADING.git
git push origin main
if errorlevel 1 (
    echo.
    echo ERROR: Failed to push to GitHub!
    echo.
    echo Possible issues:
    echo   - Not authenticated with GitHub
    echo   - No internet connection
    echo   - Wrong repository URL
    echo   - Branch protection rules
    echo.
    echo Try running: git push -u origin main --force
    echo.
    pause
    exit /b 1
)
echo Done!
echo.

REM Step 4: Success
echo [4/4] Success!
echo ======================================================================
echo All changes pushed to GitHub successfully!
echo Repository: https://github.com/Apologizesss/XAUUSD_TRADING.git
echo ======================================================================
echo.

echo Recent commits:
git log --oneline -3
echo.

pause
