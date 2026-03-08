# Shop Manager Pro - Cleanup Script
# Removes deprecated and junk files to clean up the codebase

Write-Host "🧹 Shop Manager Pro - Code Cleanup" -ForegroundColor Cyan
Write-Host "=" * 50

# Files to remove
$deprecated_apps = @(
    "app.py",
    "app_complete.py", 
    "app_enhanced.py",
    "app_modern.py",
    "app_professional.py"
)

$old_ai_components = @(
    "ai_widgets.py"
)

$debug_files = @(
    "check_users.py",
    "debug_ai_tab.py", 
    "test_login.py",
    "test_demo.py"
)

$unused_utilities = @(
    "api.py",
    "config.py",
    "deploy.py", 
    "setup.py",
    "business_logic.py",
    "reports.py",
    "utils.py"
)

$db_init_files = @(
    "db_init.py",
    "init_database.py",
    "init_db.py"
)

# Combine all files to remove
$all_junk_files = $deprecated_apps + $old_ai_components + $debug_files + $unused_utilities + $db_init_files

Write-Host "📊 Files to remove: $($all_junk_files.Length)" -ForegroundColor Yellow

$total_size = 0
$removed_count = 0

foreach ($file in $all_junk_files) {
    if (Test-Path $file) {
        $size = (Get-Item $file).Length
        $total_size += $size
        
        Write-Host "Removing: $file ($([math]::Round($size/1024, 1)) KB)" -ForegroundColor Red
        Remove-Item $file -Force
        $removed_count++
    } else {
        Write-Host "Not found: $file" -ForegroundColor Yellow
    }
}

Write-Host ""
Write-Host "✅ Cleanup completed!" -ForegroundColor Green
Write-Host "📊 Files removed: $removed_count"
Write-Host "💾 Space saved: $([math]::Round($total_size/1024, 1)) KB"

# Show remaining Python files
Write-Host ""
Write-Host "📁 Remaining Python files:" -ForegroundColor Cyan
Get-ChildItem "*.py" | Sort-Object Name | ForEach-Object {
    $size = [math]::Round($_.Length/1024, 1)
    Write-Host "  $($_.Name) ($size KB)" -ForegroundColor Green
}

Write-Host ""
Write-Host "Codebase is now clean and optimized!" -ForegroundColor Green
