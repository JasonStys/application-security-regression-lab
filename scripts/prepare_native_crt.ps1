# Jason Stys: read only licensed installed VS redistributables; no installer, registry or user-profile writes.
# Variables: VS/CRT paths identify actual signed Microsoft app-local DLLs; output is ignored developer metadata.
$ErrorActionPreference = 'Stop'
Set-StrictMode -Version Latest
Import-Module (Join-Path $PSHOME 'Modules/Microsoft.PowerShell.Security/Microsoft.PowerShell.Security.psd1') -ErrorAction Stop
Import-Module (Join-Path $PSHOME 'Modules/Microsoft.PowerShell.Utility/Microsoft.PowerShell.Utility.psd1') -ErrorAction Stop
$Repo = Split-Path $PSScriptRoot -Parent
$Vswhere = Join-Path ${env:ProgramFiles(x86)} 'Microsoft Visual Studio/Installer/vswhere.exe'
$Vs = (& $Vswhere -latest -products '*' -requires Microsoft.VisualStudio.Component.VC.Tools.x86.x64 -property installationPath).Trim()
if ($LASTEXITCODE -ne 0 -or -not $Vs) { throw 'Licensed VS redistributable source unavailable.' }
$Redist = Join-Path $Vs 'VC/Redist/MSVC'
$Version = Get-ChildItem -LiteralPath $Redist -Directory | Where-Object Name -Match '^\d+\.\d+\.\d+$' | Sort-Object { [Version]$_.Name } -Descending | Select-Object -First 1
if (-not $Version) { throw 'Versioned redistributable source unavailable.' }
$Crt = Get-ChildItem -LiteralPath (Join-Path $Version.FullName 'x64') -Directory -Filter 'Microsoft.VC*.CRT' | Select-Object -First 1
if (-not $Crt) { throw 'App-local x64 CRT directory unavailable.' }
$Files = @()
foreach ($Name in @('vcruntime140.dll', 'vcruntime140_1.dll')) {
    $Dll = Join-Path $Crt.FullName $Name
    if ((Get-AuthenticodeSignature -LiteralPath $Dll).Status -ne 'Valid' -or (Get-Item -LiteralPath $Dll).VersionInfo.CompanyName -ne 'Microsoft Corporation') { throw 'Microsoft CRT signature/identity verification failed.' }
    $Files += @{name=$Name;sha256=(Get-FileHash -LiteralPath $Dll -Algorithm SHA256).Hash.ToLowerInvariant()}
}
$Output = Join-Path $Repo 'out/native-crt.json'
@{directory=$Crt.FullName;files=$Files} | ConvertTo-Json -Depth 4 | Set-Content -LiteralPath $Output -Encoding utf8
Write-Output 'Actual signed app-local Microsoft CRT identity recorded; no global runtime changes.'
