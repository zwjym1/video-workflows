$ErrorActionPreference = "Stop"
$homeDir = "C:\Users\Administrator"
$root = "D:\编程\项目\视频制作\作品\2026-10-29_火箭水母云"
$parts = Join-Path $root "out\_parts"
$pub = Join-Path $root "发布"
New-Item -ItemType Directory -Force -Path $parts | Out-Null
New-Item -ItemType Directory -Force -Path $pub | Out-Null

$expected = @{
  "part_00" = "264fcf308c819f4578b34bd7facd9121eb68a3eb59664edbc69aa59cba4a52ed"
  "part_01" = "e3740e34727b5f926f4eca33ed7e8a2fc7340d0ce5791ff34024a1b83e86c273"
  "part_02" = "d75de604f7e9272dce9b0213641a46b1e8f36736a356a96838a092d886c6a2d1"
  "part_03" = "e232c93ede04f43bd7592d65047e616c778130dc0b74decab90407b862085b64"
}

foreach ($name in @("part_00","part_01","part_02","part_03")) {
  $src = Join-Path $homeDir $name
  if (-not (Test-Path -LiteralPath $src)) { throw "MISSING_HOME $name" }
  $hash = (Get-FileHash -Algorithm SHA256 -LiteralPath $src).Hash.ToLower()
  if ($hash -ne $expected[$name]) { throw "HASH_FAIL $name got=$hash" }
  Write-Output "OK $name $hash"
  Copy-Item -LiteralPath $src -Destination (Join-Path $parts $name) -Force
}

$wantV = "f8ba5d83c74dc67353825adbefec3bd414933c1bf518d0e878f88dc6a99f3041"
$wantH = "a9c576a4371a270bf2bb904d69be2376e04624b64561468fe956f7d1ef6fae77"
$srcV = $null
$srcH = $null
Get-ChildItem -LiteralPath $homeDir -File | ForEach-Object {
  if ($_.Length -lt 500KB -or $_.Length -gt 2MB) { return }
  $h = (Get-FileHash -Algorithm SHA256 -LiteralPath $_.FullName).Hash.ToLower()
  if ($h -eq $wantV -and -not $script:srcV) { $script:srcV = $_.FullName }
  if ($h -eq $wantH -and -not $script:srcH) { $script:srcH = $_.FullName }
}
if (-not $srcV) { throw "MISSING cover_v" }
if (-not $srcH) { throw "MISSING cover_h" }
$coverV = "火箭水母云_封面_竖9x16_1080x1920.png"
$coverH = "火箭水母云_封面_横4x3_1440x1080.png"
$mp4Name = "火箭水母云_成片_1080x1920.mp4"
Copy-Item -LiteralPath $srcV -Destination (Join-Path $pub $coverV) -Force
Copy-Item -LiteralPath $srcH -Destination (Join-Path $pub $coverH) -Force
Write-Output "COVERS_OK"

$out = Join-Path $pub $mp4Name
$fs = [IO.File]::Create($out)
foreach ($p in 0..3) {
  $b = [IO.File]::ReadAllBytes((Join-Path $parts ("part_0{0}" -f $p)))
  $fs.Write($b, 0, $b.Length)
}
$fs.Close()
$final = (Get-FileHash -Algorithm SHA256 -LiteralPath $out).Hash.ToLower()
$len = (Get-Item -LiteralPath $out).Length
Write-Output "FINAL $final size=$len"
if ($final -ne "ca9c1936d3ced4026d2a6c66c0efbfdf9a104480b6ee0123af82c3c9bdd129a5") { throw "FINAL_HASH_FAIL" }
Write-Output "PUB_CONTENTS:"
Get-ChildItem -LiteralPath $pub | ForEach-Object { Write-Output ("  " + $_.Name + " " + $_.Length) }
Write-Output "DONE"
