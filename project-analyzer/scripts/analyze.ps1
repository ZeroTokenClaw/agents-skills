# Project Analyzer - PowerShell Edition
# Usage: .\analyze.ps1
# Description: Quick scan of project identity and structure

Write-Host "🔍 Project Analyzer (Windows)" -ForegroundColor Cyan
Write-Host "============================"
Write-Host ""

# 1. Identity Scan
Write-Host "1. Identity & Config" -ForegroundColor Yellow
if (Test-Path "package.json") {
    $pkg = Get-Content "package.json" | ConvertFrom-Json
    Write-Host "   • Type: Node.js"
    Write-Host "   • Name: $($pkg.name)"
    if ($pkg.engines.node) { Write-Host "   • Node: $($pkg.engines.node)" }
    
    # Check package manager
    if (Test-Path "pnpm-lock.yaml") { Write-Host "   • Manager: pnpm" }
    elseif (Test-Path "yarn.lock") { Write-Host "   • Manager: yarn" }
    elseif (Test-Path "package-lock.json") { Write-Host "   • Manager: npm" }
}
elseif (Test-Path "Cargo.toml") { Write-Host "   • Type: Rust" }
elseif (Test-Path "go.mod") { Write-Host "   • Type: Go" }
elseif (Test-Path "pyproject.toml") { Write-Host "   • Type: Python" }
else { Write-Host "   • Type: Unknown" }

Write-Host ""
# 2. Structure Scan
Write-Host "2. Structure" -ForegroundColor Yellow
$dirs = Get-ChildItem -Directory | Select-Object -ExpandProperty Name
if ($dirs -contains "src") { Write-Host "   • Source: src/" }
if ($dirs -contains "app") { Write-Host "   • App: app/" }
if ($dirs -contains "lib") { Write-Host "   • Lib: lib/" }
if ($dirs -contains "components") { Write-Host "   • Components: components/" }
if ($dirs -contains "pages") { Write-Host "   • Pages: pages/" }

Write-Host ""
# 3. Config Files
Write-Host "3. Configuration" -ForegroundColor Yellow
$configs = Get-ChildItem -File | Where-Object { $_.Name -match "rc$|config\.|json$|yml$|toml$" } | Select-Object -ExpandProperty Name
foreach ($conf in $configs) {
    Write-Host "   • $conf"
}

Write-Host ""
Write-Host "📋 Next Step:" -ForegroundColor Green
Write-Host "   Run the Agent to generate the full skill:"
Write-Host "   'Analyze this project and generate the PROJECT.md skill file based on the template.'"
