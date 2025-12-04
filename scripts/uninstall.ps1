param(
    [string]$InstallDir = (Join-Path $env:LOCALAPPDATA "RunbatMaker")
)

$targetExe = Join-Path $InstallDir "runbat_maker.exe"

if (Test-Path $targetExe) {
    Write-Host "Removing context menus and auto-start..."
    & $targetExe --unregister-shell --silent
    & $targetExe --unregister-startup --silent
}

if (Test-Path "HKCU:\Software\RunbatMaker") {
    Remove-Item -Path "HKCU:\Software\RunbatMaker" -Recurse -Force -ErrorAction SilentlyContinue
    Write-Host "RunbatMaker registry entries cleaned."
}

if (Test-Path $InstallDir) {
    Remove-Item -Path $InstallDir -Recurse -Force -ErrorAction SilentlyContinue
    Write-Host "Deleted install directory: $InstallDir"
}

Write-Host "Uninstall complete."
