param(
    [string]$ExecutablePath = (Join-Path $PSScriptRoot "..\runbat_maker.exe"),
    [string]$InstallDir = (Join-Path $env:LOCALAPPDATA "RunbatMaker"),
    [string]$MCNP6Path
)

if (-not (Test-Path $ExecutablePath)) {
    Write-Error "Executable not found: $ExecutablePath"
    exit 1
}

if (-not $MCNP6Path) {
    $MCNP6Path = Read-Host "Enter MCNP6 installation directory"
}

if (-not (Test-Path $MCNP6Path)) {
    Write-Error "MCNP6 directory does not exist: $MCNP6Path"
    exit 1
}

New-Item -ItemType Directory -Path $InstallDir -Force | Out-Null
$targetExe = Join-Path $InstallDir "runbat_maker.exe"
Copy-Item -Path $ExecutablePath -Destination $targetExe -Force

Write-Host "Copied runbat_maker.exe to $InstallDir"

& $targetExe --set-mcnp-path "$MCNP6Path" --silent
& $targetExe --register-shell --silent
& $targetExe --register-startup --silent

Write-Host "Installation complete. Context menus and auto-start configured."
