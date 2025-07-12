@echo off
echo 🎮 SMITE 2 Divine Arsenal - Patch Update Tool
echo ================================================
echo.

echo 🔍 Checking current patch status...
python patch_monitor.py
echo.

echo 📥 Running automated patch updater...
python automated_patch_updater.py
echo.

echo 📊 Generating status report...
python patch_status_report.py
echo.

echo ✅ Patch update process completed!
echo.
echo 🌐 Your build optimizer is now up to date!
echo    Access via: http://localhost:5002
echo.
pause 