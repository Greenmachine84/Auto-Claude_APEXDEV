# Comprehensive Auto-Claude to APEXDEV branding fix script
# This script replaces all .auto-claude folder references with .apexdev

$root = $PSScriptRoot

Write-Host "=== APEXDEV Branding Fix Script ===" -ForegroundColor Cyan
Write-Host "Root: $root"

# Count before
$beforeCount = (Get-ChildItem -Recurse -File -Include "*.py","*.ts","*.tsx","*.md","*.json","*.yaml","*.toml" | 
    Select-String -Pattern '\.auto-claude|auto-claude-security|auto-claude-status' | Measure-Object).Count
Write-Host "Found $beforeCount occurrences of auto-claude patterns before fix"

# Process Python files in backend
Write-Host "`nProcessing backend Python files..." -ForegroundColor Yellow
Get-ChildItem "apps/backend" -Recurse -Filter "*.py" | ForEach-Object {
    $content = Get-Content $_.FullName -Raw -ErrorAction SilentlyContinue
    if ($content -and ($content -match '\.auto-claude|auto-claude-security|auto-claude-status')) {
        $newContent = $content
        $newContent = $newContent -replace '\.auto-claude-security', '.apexdev-security'
        $newContent = $newContent -replace '\.auto-claude-status', '.apexdev-status'
        $newContent = $newContent -replace '\.auto-claude/', '.apexdev/'
        $newContent = $newContent -replace '\.auto-claude', '.apexdev'
        $newContent = $newContent -replace '"auto-claude"', '"apexdev"'
        $newContent = $newContent -replace "'auto-claude'", "'apexdev'"
        if ($newContent -ne $content) {
            Set-Content $_.FullName -Value $newContent -Encoding UTF8 -NoNewline
            Write-Host "  Fixed: $($_.FullName -replace [regex]::Escape($root), '')"
        }
    }
}

# Process TypeScript/TSX files in frontend
Write-Host "`nProcessing frontend TypeScript files..." -ForegroundColor Yellow
Get-ChildItem "apps/frontend/src" -Recurse -Include "*.ts","*.tsx" | ForEach-Object {
    $content = Get-Content $_.FullName -Raw -ErrorAction SilentlyContinue
    if ($content -and ($content -match '\.auto-claude|auto-claude-security|auto-claude-status')) {
        $newContent = $content
        $newContent = $newContent -replace '\.auto-claude-security', '.apexdev-security'
        $newContent = $newContent -replace '\.auto-claude-status', '.apexdev-status'
        $newContent = $newContent -replace '\.auto-claude/', '.apexdev/'
        $newContent = $newContent -replace '\.auto-claude', '.apexdev'
        if ($newContent -ne $content) {
            Set-Content $_.FullName -Value $newContent -Encoding UTF8 -NoNewline
            Write-Host "  Fixed: $($_.FullName -replace [regex]::Escape($root), '')"
        }
    }
}

# Process markdown files
Write-Host "`nProcessing markdown files..." -ForegroundColor Yellow
Get-ChildItem -Recurse -Filter "*.md" | ForEach-Object {
    $content = Get-Content $_.FullName -Raw -ErrorAction SilentlyContinue
    if ($content -and ($content -match '\.auto-claude|auto-claude-security|auto-claude-status')) {
        $newContent = $content
        $newContent = $newContent -replace '\.auto-claude-security', '.apexdev-security'
        $newContent = $newContent -replace '\.auto-claude-status', '.apexdev-status'
        $newContent = $newContent -replace '\.auto-claude/', '.apexdev/'
        $newContent = $newContent -replace '\.auto-claude', '.apexdev'
        if ($newContent -ne $content) {
            Set-Content $_.FullName -Value $newContent -Encoding UTF8 -NoNewline
            Write-Host "  Fixed: $($_.FullName -replace [regex]::Escape($root), '')"
        }
    }
}

# Process gitignore files
Write-Host "`nProcessing .gitignore files..." -ForegroundColor Yellow
Get-ChildItem -Recurse -Filter ".gitignore" | ForEach-Object {
    $content = Get-Content $_.FullName -Raw -ErrorAction SilentlyContinue
    if ($content -and ($content -match '\.auto-claude|auto-claude-security|auto-claude-status')) {
        $newContent = $content
        $newContent = $newContent -replace '\.auto-claude-security', '.apexdev-security'
        $newContent = $newContent -replace '\.auto-claude-status', '.apexdev-status'
        $newContent = $newContent -replace '\.auto-claude/', '.apexdev/'
        $newContent = $newContent -replace '\.auto-claude', '.apexdev'
        if ($newContent -ne $content) {
            Set-Content $_.FullName -Value $newContent -Encoding UTF8 -NoNewline
            Write-Host "  Fixed: $($_.FullName -replace [regex]::Escape($root), '')"
        }
    }
}

# Process config files (yaml, toml, json)
Write-Host "`nProcessing config files..." -ForegroundColor Yellow
Get-ChildItem -Recurse -Include "*.yaml","*.yml","*.toml" | Where-Object { $_.FullName -notmatch "node_modules" } | ForEach-Object {
    $content = Get-Content $_.FullName -Raw -ErrorAction SilentlyContinue
    if ($content -and ($content -match '\.auto-claude|auto-claude-security|auto-claude-status')) {
        $newContent = $content
        $newContent = $newContent -replace '\.auto-claude-security', '.apexdev-security'
        $newContent = $newContent -replace '\.auto-claude-status', '.apexdev-status'
        $newContent = $newContent -replace '\.auto-claude/', '.apexdev/'
        $newContent = $newContent -replace '\.auto-claude', '.apexdev'
        if ($newContent -ne $content) {
            Set-Content $_.FullName -Value $newContent -Encoding UTF8 -NoNewline
            Write-Host "  Fixed: $($_.FullName -replace [regex]::Escape($root), '')"
        }
    }
}

# Count after
$afterCount = (Get-ChildItem -Recurse -File -Include "*.py","*.ts","*.tsx","*.md","*.yaml","*.toml" | 
    Select-String -Pattern '\.auto-claude|auto-claude-security|auto-claude-status' | Measure-Object).Count
Write-Host "`n=== Summary ===" -ForegroundColor Green
Write-Host "Before: $beforeCount occurrences"
Write-Host "After: $afterCount occurrences"
