# PowerShell script to create virtual environment and build threedipa package
# Use powershell -ExecutionPolicy Bypass -File .\build.ps1 if .\build.ps1 fails
$ErrorActionPreference = "Stop"  # Exit on error

Write-Host "=== UV Build and Sync Script ===" -ForegroundColor Cyan
Write-Host ""

# Check if uv is installed
if (-not (Get-Command uv -ErrorAction SilentlyContinue)) {
    Write-Host "UV is not installed or not in PATH" -ForegroundColor Yellow
    $response = Read-Host "Install UV? (y/n)"
    if ($response -eq 'y' -or $response -eq 'Y') {
        Invoke-RestMethod https://astral.sh/uv/install.ps1 | Invoke-Expression
    } else {
        Write-Host "Please install UV manually: https://github.com/astral-sh/uv"
        exit 1
    }
    Write-Host "Please close and reopen PowerShell to use UV" -ForegroundColor Yellow
    exit 1
}

Write-Host "uv is installed: $(uv --version)"
Write-Host ""
 if (-not (Test-Path .venv)) {
    $response = Read-Host "Do you want to create threedipa virtual environment? (y/n)"
    if ($response -eq 'y' -or $response -eq 'Y') {
        # Run uv build
        Write-Host "=== Running uv build ===" -ForegroundColor Green
        uv build
        Write-Host ""

        # Run uv sync
        Write-Host "=== Running uv sync ===" -ForegroundColor Green
        uv sync
        Write-Host ""

        Write-Host "=== Build and sync complete! ===" -ForegroundColor Cyan
    } else {
        Write-Host "Please create threedipa virtual environment manually: uv venv"
        exit 1
    }
 }

Write-Host "=== Opening Virtual Environment and Building ThreeDIPA Package ===" -ForegroundColor Green
.\.venv\Scripts\Activate.ps1
uv pip install -e .
Write-Host "=== Build Complete! ===" -ForegroundColor Cyan

Write-Host "=== Type `deactivate` to exit the virtual environment ===" -ForegroundColor Cyan
