# SMITE 2 Divine Arsenal - Comprehensive Test Runner
# Run this script to test all build optimizer functionality

Write-Host "🧪 SMITE 2 DIVINE ARSENAL - COMPREHENSIVE TESTING" -ForegroundColor Cyan
Write-Host "=" * 60 -ForegroundColor Gray

# Check if Python is available
try {
    $pythonVersion = python --version 2>&1
    Write-Host "✅ Python found: $pythonVersion" -ForegroundColor Green
}
catch {
    Write-Host "❌ Python not found. Please install Python 3.8+" -ForegroundColor Red
    exit 1
}

# Check if requests library is available
try {
    python -c "import requests" 2>$null
    Write-Host "✅ Requests library available" -ForegroundColor Green
}
catch {
    Write-Host "⚠️ Installing requests library..." -ForegroundColor Yellow
    pip install requests
}

Write-Host ""
Write-Host "🚀 STARTING TESTS..." -ForegroundColor Cyan
Write-Host ""

# Test 1: SQLite (local development)
Write-Host "🔍 Testing with SQLite (Local Development)" -ForegroundColor Yellow
Write-Host "Starting local server..." -ForegroundColor Gray

# Start the server in background
$serverProcess = Start-Process -FilePath "powershell" -ArgumentList "-Command", "cd divine_arsenal/backend; python app_with_migrations.py" -PassThru -WindowStyle Hidden

# Wait for server to start
Start-Sleep 5

# Run tests
Write-Host "Running tests against SQLite..." -ForegroundColor Gray
python test_build_optimizer.py

# Stop server
Write-Host "Stopping local server..." -ForegroundColor Gray
Stop-Process -Id $serverProcess.Id -Force -ErrorAction SilentlyContinue

Write-Host ""
Write-Host "🔍 Testing with PostgreSQL (Production)" -ForegroundColor Yellow

# Test 2: PostgreSQL (production)
$env:DATABASE_URL = 'postgresql://divine_arsenal_db_user:PHc5f6cz2mPKBlfhZhe6mRgvxDNsRkmH@dpg-d1op9jbipnbc73fa7gg0-a.oregon-postgres.render.com/divine_arsenal_db'

Write-Host "Starting server with PostgreSQL..." -ForegroundColor Gray

# Start server with PostgreSQL
$serverProcess = Start-Process -FilePath "powershell" -ArgumentList "-Command", "cd divine_arsenal/backend; python app_with_migrations.py" -PassThru -WindowStyle Hidden

# Wait for server to start
Start-Sleep 5

# Run tests
Write-Host "Running tests against PostgreSQL..." -ForegroundColor Gray
python test_build_optimizer.py

# Stop server
Write-Host "Stopping server..." -ForegroundColor Gray
Stop-Process -Id $serverProcess.Id -Force -ErrorAction SilentlyContinue

Write-Host ""
Write-Host "📊 TEST RESULTS SUMMARY" -ForegroundColor Cyan
Write-Host "Check test_results.json for detailed results" -ForegroundColor Gray

# Show results if file exists
if (Test-Path "test_results.json") {
    $results = Get-Content "test_results.json" | ConvertFrom-Json
    Write-Host "✅ Passed: $($results.passed)" -ForegroundColor Green
    Write-Host "❌ Failed: $($results.failed)" -ForegroundColor Red
    Write-Host "📈 Success Rate: $($results.success_rate)%" -ForegroundColor Cyan
    
    if ($results.ready_for_deployment) {
        Write-Host ""
        Write-Host "🚀 BUILD OPTIMIZER READY FOR DEPLOYMENT!" -ForegroundColor Green
        Write-Host "You can now proceed with confidence to deploy to Render" -ForegroundColor Green
    }
    else {
        Write-Host ""
        Write-Host "⚠️ BUILD OPTIMIZER NEEDS FIXES BEFORE DEPLOYMENT" -ForegroundColor Yellow
        Write-Host "Review the failed tests and fix issues before deploying" -ForegroundColor Yellow
    }
}

Write-Host ""
Write-Host "🎯 NEXT STEPS:" -ForegroundColor Cyan
Write-Host "1. Review test results in test_results.json" -ForegroundColor Gray
Write-Host "2. Fix any failing tests" -ForegroundColor Gray
Write-Host "3. If tests pass, proceed with Render deployment" -ForegroundColor Gray
Write-Host "4. Test community features (Phase 2)" -ForegroundColor Gray

Write-Host ""
Write-Host "Done! 🎉" -ForegroundColor Green 