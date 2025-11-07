# ======================================================================
# Git Push Script - PowerShell Version
# ======================================================================
# This script pushes changes to GitHub repository
# ======================================================================

Write-Host ""
Write-Host "======================================================================"
Write-Host "Git Push to GitHub - XAUUSD Trading Bot"
Write-Host "======================================================================"
Write-Host ""

# Step 1: Add all files
Write-Host "[1/4] Adding all files to staging..." -ForegroundColor Cyan
git add -A

if ($LASTEXITCODE -ne 0) {
    Write-Host "ERROR: Failed to add files!" -ForegroundColor Red
    Read-Host "Press Enter to exit"
    exit 1
}
Write-Host "Done!" -ForegroundColor Green
Write-Host ""

# Step 2: Commit changes
Write-Host "[2/4] Committing changes..." -ForegroundColor Cyan
git commit -m "Update live trading system with display improvements and news sentiment"

if ($LASTEXITCODE -ne 0) {
    Write-Host "WARNING: Nothing to commit or commit failed" -ForegroundColor Yellow
    Write-Host "This might mean there are no changes to commit." -ForegroundColor Yellow
}
Write-Host "Done!" -ForegroundColor Green
Write-Host ""

# Step 3: Push to GitHub
Write-Host "[3/4] Pushing to GitHub..." -ForegroundColor Cyan
Write-Host "Repository: https://github.com/Apologizesss/XAUUSD_TRADING.git" -ForegroundColor Gray

git push origin main

if ($LASTEXITCODE -ne 0) {
    Write-Host ""
    Write-Host "ERROR: Failed to push to GitHub!" -ForegroundColor Red
    Write-Host ""
    Write-Host "Possible issues:" -ForegroundColor Yellow
    Write-Host "  - Not authenticated with GitHub" -ForegroundColor Yellow
    Write-Host "  - No internet connection" -ForegroundColor Yellow
    Write-Host "  - Wrong repository URL" -ForegroundColor Yellow
    Write-Host "  - Branch protection rules" -ForegroundColor Yellow
    Write-Host ""
    Write-Host "Try running: git push -u origin main --force" -ForegroundColor Cyan
    Write-Host ""
    Read-Host "Press Enter to exit"
    exit 1
}
Write-Host "Done!" -ForegroundColor Green
Write-Host ""

# Step 4: Success
Write-Host "[4/4] Success!" -ForegroundColor Green
Write-Host "======================================================================"
Write-Host "All changes pushed to GitHub successfully!" -ForegroundColor Green
Write-Host "Repository: https://github.com/Apologizesss/XAUUSD_TRADING.git" -ForegroundColor Cyan
Write-Host "======================================================================"
Write-Host ""

# Show what was pushed
Write-Host "Recent commits:" -ForegroundColor Cyan
git log --oneline -3
Write-Host ""

Read-Host "Press Enter to exit"
