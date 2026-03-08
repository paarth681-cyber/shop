# Simple cleanup script for Shop Manager Pro
Write-Host "Starting cleanup of deprecated files..." -ForegroundColor Cyan

# Files to delete
$filesToDelete = @(
    "app.py",
    "app_complete.py", 
    "app_enhanced.py",
    "app_modern.py",
    "app_professional.py",
    "ai_widgets.py",
    "check_users.py",
    "debug_ai_tab.py",
    "test_login.py",
    "test_demo.py",
    "api.py",
    "config.py",
    "deploy.py",
    "setup.py",
    "business_logic.py",
    "reports.py",
    "utils.py",
    "db_init.py",
    "init_database.py",
    "init_db.py"
)

$deletedCount = 0
$totalSize = 0

foreach ($file in $filesToDelete) {
    if (Test-Path $file) {
        $size = (Get-Item $file).Length
        $totalSize += $size
        $sizeKB = [math]::Round($size/1024, 1)
        Write-Host "Deleting: $file ($sizeKB KB)" -ForegroundColor Red
        Remove-Item $file -Force
        $deletedCount++
    } else {
        Write-Host "Not found: $file" -ForegroundColor Yellow
    }
}

Write-Host ""
Write-Host "Cleanup complete!" -ForegroundColor Green
Write-Host "Files deleted: $deletedCount" -ForegroundColor Green
Write-Host "Space freed: $([math]::Round($totalSize/1024, 1)) KB" -ForegroundColor Green

# List remaining files
Write-Host ""
Write-Host "Remaining files in directory:" -ForegroundColor Cyan
Get-ChildItem -File | Sort-Object Name | ForEach-Object {
    $size = [math]::Round($_.Length/1024, 1)
    Write-Host "  $($_.Name) ($size KB)" -ForegroundColor Green
}

Write-Host ""
Write-Host "Codebase is now clean and optimized!" -ForegroundColor Green