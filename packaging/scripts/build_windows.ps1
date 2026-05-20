$ErrorActionPreference = "Stop"

$ProjectRoot = Resolve-Path (Join-Path $PSScriptRoot "../..")
Set-Location $ProjectRoot

py -3 -m venv .venv-build
& ".\.venv-build\Scripts\python.exe" -m pip install --upgrade pip
& ".\.venv-build\Scripts\python.exe" -m pip install -r requirements.txt

& ".\.venv-build\Scripts\python.exe" -m PyInstaller --clean --noconfirm packaging\pyinstaller\windows.spec

$ArtifactDir = Join-Path $ProjectRoot "release_artifacts\windows"
New-Item -ItemType Directory -Force -Path $ArtifactDir | Out-Null

$InnoCandidates = @(
    "${env:ProgramFiles(x86)}\Inno Setup 6\ISCC.exe",
    "${env:ProgramFiles}\Inno Setup 6\ISCC.exe"
)
$InnoCompiler = $InnoCandidates | Where-Object { Test-Path $_ } | Select-Object -First 1

if ($InnoCompiler) {
    & $InnoCompiler "packaging\installer\windows\SpringLab.iss"
    Write-Host "Done: release_artifacts\windows\SpringLab-Windows-Setup.exe"
} else {
    Copy-Item "dist\SpringLab.exe" "$ArtifactDir\SpringLab-Windows-Portable.exe" -Force
    Write-Host "Inno Setup was not found. Portable file was created:"
    Write-Host "  release_artifacts\windows\SpringLab-Windows-Portable.exe"
    Write-Host "To create installer .exe, install Inno Setup 6 and run this script again."
}
