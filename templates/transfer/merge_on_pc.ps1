<# 在用户 PC 上合并 split_for_pc.sh 的分块并校验 sha256。
   用法: powershell -ExecutionPolicy Bypass -File merge_on_pc.ps1 -Dir D:\...\工程\x.zip.parts -Name x.zip [-Out D:\...\工程]
   一致才输出 OK；不一致删掉合并结果并退出 1（分块保留，重传坏块）。 #>
param([Parameter(Mandatory=$true)][string]$Dir, [Parameter(Mandatory=$true)][string]$Name, [string]$Out = (Split-Path $Dir -Parent))
$ErrorActionPreference = 'Stop'
$dst = Join-Path $Out $Name
$parts = Get-ChildItem $Dir -Filter "$Name.part*" | Sort-Object Name
$fs = [IO.File]::Create($dst)
try { foreach ($p in $parts) { $b = [IO.File]::ReadAllBytes($p.FullName); $fs.Write($b, 0, $b.Length) } } finally { $fs.Close() }
$want = (Get-Content (Join-Path $Dir 'SHA256.txt')).Trim().ToLower()
$got = (Get-FileHash -Algorithm SHA256 $dst).Hash.ToLower()
if ($got -eq $want) { Write-Host "OK $dst ($($parts.Count) parts) sha256=$got" } else { Remove-Item $dst; Write-Error "sha256 不一致: got $got want $want"; exit 1 }
