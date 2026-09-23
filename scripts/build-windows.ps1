param([string]$OutputDirectory = "build-windows")
$ErrorActionPreference = "Stop"
Push-Location (Split-Path $PSScriptRoot -Parent)
try {
    cmake -S . -B $OutputDirectory -DCMAKE_BUILD_TYPE=Release
    if ($LASTEXITCODE -ne 0) { throw "CMake configuration failed." }
    cmake --build $OutputDirectory --config Release --parallel
    if ($LASTEXITCODE -ne 0) { throw "Build failed." }
    ctest --test-dir $OutputDirectory -C Release --output-on-failure
    if ($LASTEXITCODE -ne 0) { throw "Tests failed." }
} finally { Pop-Location }
