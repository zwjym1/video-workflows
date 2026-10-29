<# 通用 PC 端合并脚本（配合 make_pc_bundle.sh）。只新建、不删除；任何一块哈希不对就停。
   在 $HOME（以及 -Search 里给的目录）里按名字找 <TAG>__manifest.json 和分块；
   名字找不到时再按 大小+sha256 在同一批目录里找（应对 CopyFromBox 改名/乱码，EP-20261029-01 的 find_parts 问题）。
   用法：powershell -NoProfile -ExecutionPolicy Bypass -File <TAG>__assemble.ps1 [-Tag x] [-Dest 'D:\...\发布'] [-Search 'C:\a','C:\b'] [-PartsDir 'D:\...\out\_parts'] [-Force]
   -Dest 默认取 manifest 里的目标目录；-PartsDir 给了就把校验过的分块复制一份过去留档（不移动、不删 $HOME 里的）。
   目标文件已存在且哈希一致 → 跳过；已存在但哈希不同 → 停下，除非 -Force（-Force 也只覆盖这一个成品文件）。 #>
param(
  [string]$Tag = "__DEFAULT_TAG__",
  [string]$Dest = "",
  [string[]]$Search = @(),
  [string]$PartsDir = "",
  [switch]$Force
)
$ErrorActionPreference = "Stop"
$dirs = @($HOME, (Join-Path $HOME "Downloads"), (Join-Path $HOME "Desktop")) + $Search | Where-Object { $_ -and (Test-Path -LiteralPath $_) } | Select-Object -Unique
function Sha($p) { (Get-FileHash -Algorithm SHA256 -LiteralPath $p).Hash.ToLower() }
function Find-ByName($name) {
  foreach ($d in $dirs) { $p = Join-Path $d $name; if (Test-Path -LiteralPath $p) { return $p } }
  return $null
}
function Find-ByHash($size, $sha) {
  foreach ($d in $dirs) {
    foreach ($f in Get-ChildItem -LiteralPath $d -File -ErrorAction SilentlyContinue) {
      if ($f.Length -eq $size -and (Sha $f.FullName) -eq $sha) { return $f.FullName }
    }
  }
  return $null
}
$manPath = Find-ByName "$($Tag)__manifest.json"
if (-not $manPath) { throw "MISSING_MANIFEST $($Tag)__manifest.json（在 $($dirs -join '; ') 里都没找到）" }
$man = Get-Content -LiteralPath $manPath -Raw -Encoding UTF8 | ConvertFrom-Json
if (-not $Dest) { $Dest = $man.dest }
New-Item -ItemType Directory -Force -Path $Dest | Out-Null
if ($PartsDir) { New-Item -ItemType Directory -Force -Path $PartsDir | Out-Null }
Write-Output "MANIFEST $manPath → $Dest"
foreach ($fi in $man.files) {
  $out = Join-Path $Dest $fi.name
  if (Test-Path -LiteralPath $out) {
    if ((Sha $out) -eq $fi.sha256) { Write-Output "SKIP_OK $($fi.name)"; continue }
    if (-not $Force) { throw "EXISTS_DIFFERENT $out（加 -Force 才覆盖这一个文件）" }
  }
  $srcs = @()
  foreach ($p in $fi.parts) {
    $src = Find-ByName $p.name
    if ($src -and (Sha $src) -ne $p.sha256) { Write-Output "NAME_HIT_BAD_HASH $src"; $src = $null }
    if (-not $src) { $src = Find-ByHash $p.size $p.sha256 }
    if (-not $src) { throw "MISSING_PART $($p.name) size=$($p.size)（只重传这一块）" }
    Write-Output "OK $($p.name) ← $src"
    if ($PartsDir) { Copy-Item -LiteralPath $src -Destination (Join-Path $PartsDir $p.name) -Force }
    $srcs += $src
  }
  $tmp = "$out.partial"
  $fs = [IO.File]::Create($tmp)
  try { foreach ($s in $srcs) { $b = [IO.File]::ReadAllBytes($s); $fs.Write($b, 0, $b.Length) } } finally { $fs.Close() }
  $got = Sha $tmp
  if ($got -ne $fi.sha256) { throw "FINAL_HASH_FAIL $($fi.name) got=$got want=$($fi.sha256)（临时文件留在 $tmp）" }
  Move-Item -LiteralPath $tmp -Destination $out -Force
  Write-Output "FILE_OK $($fi.name) $($fi.size) B"
}
Write-Output "DEST_CONTENTS:"
Get-ChildItem -LiteralPath $Dest -File | ForEach-Object { Write-Output ("  " + $_.Name + " " + $_.Length) }
Write-Output "DONE"
