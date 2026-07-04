# Create Desktop Shortcut for Leave Management Agent
$WshShell = New-Object -ComObject WScript.Shell
$Desktop = [Environment]::GetFolderPath("Desktop")
$ShortcutPath = Join-Path $Desktop "Leave Management Agent.lnk"
$Shortcut = $WshShell.CreateShortcut($ShortcutPath)
$Shortcut.TargetPath = Join-Path $PSScriptRoot "START_APP.bat"
$Shortcut.WorkingDirectory = $PSScriptRoot
$Shortcut.Description = "Leave Management Agent - Enterprise HRMS Dashboard"
$Shortcut.IconLocation = "shell32.dll,21"  # Calendar icon
$Shortcut.Save()

Write-Host ""
Write-Host "========================================" -ForegroundColor Green
Write-Host "  Desktop Shortcut Created!" -ForegroundColor Green
Write-Host "========================================" -ForegroundColor Green
Write-Host ""
Write-Host "A shortcut 'Leave Management Agent' has been created on your Desktop!" -ForegroundColor Cyan
Write-Host ""
Write-Host "Double-click it to start the application!" -ForegroundColor Yellow
Write-Host ""
Read-Host "Press Enter to exit"
