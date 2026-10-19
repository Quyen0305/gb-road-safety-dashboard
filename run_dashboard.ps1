[CmdletBinding()]
param([ValidateRange(1024,65535)][int]$Port = 8501)

$ErrorActionPreference = 'Stop'
$roadlensRoot = $PSScriptRoot
$roadlensPython = Join-Path $roadlensRoot '.venv\Scripts\python.exe'
$roadlensCsv = if ($env:ROADLENS_DATA) { $env:ROADLENS_DATA } else { Join-Path $roadlensRoot 'du_lieu_tai_nan_2024_san_sang_truc_quan.csv' }
if (-not (Test-Path -LiteralPath $roadlensPython)) {
    throw 'Python environment not found. Follow the setup steps in README.md.'
}
if (-not (Test-Path -LiteralPath $roadlensCsv)) {
    throw "Data file not found: $roadlensCsv"
}
Push-Location -LiteralPath $roadlensRoot
try {
    Write-Host "RoadLens: http://127.0.0.1:$Port  (Ctrl+C to stop)"
    & $roadlensPython -m streamlit run app.py --server.address 127.0.0.1 --server.port $Port --server.headless true --browser.gatherUsageStats false
    if ($LASTEXITCODE -ne 0) { throw "Streamlit exited with code $LASTEXITCODE" }
} finally {
    Pop-Location
}
