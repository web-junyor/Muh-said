Write-Host "============================="
Write-Host "🚀 Starting Django Backend..."
Write-Host "============================="

Start-Process powershell -ArgumentList "cd '$PSScriptRoot'; python manage.py runserver 127.0.0.1:8001"

Start-Sleep -Seconds 2

Write-Host "============================="
Write-Host "🤖 Starting Telegram Bot..."
Write-Host "============================="

Start-Process powershell -ArgumentList "cd '$PSScriptRoot\bot'; python main.py"
