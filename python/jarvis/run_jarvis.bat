@echo off
chcp 65001 >nul
cd /d "%~dp0"
echo.
echo ============================================
echo   JARVIS ishga tushmoqda...
echo ============================================
echo.
echo   Buyruq berish: avval "Jarvis" deb ayting,
echo   keyin: soat necha / muzikani qo'y / latifa aytib ber
echo.
echo   To'xtatish: Ctrl+C
echo ============================================
echo.
python jarvis.py
if errorlevel 1 pause
