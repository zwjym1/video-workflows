# 在用户 PC 上抽「审片拼图」所需的帧（只读视频，不改任何已有文件）。
# 用法（需 PowerShell 7 的 pwsh，用到 ForEach-Object -Parallel）: pwsh -NoProfile -ExecutionPolicy Bypass -File pc_frames.ps1 -List jobs.csv -Out <Downloads下新建目录>
# jobs.csv: id,path  （UTF-8，无表头）
param([string]$List, [string]$Out)
$ErrorActionPreference = 'Stop'
New-Item -ItemType Directory -Force -Path $Out | Out-Null
$sw = [Diagnostics.Stopwatch]::StartNew()
Get-Content -Encoding UTF8 $List | ForEach-Object {
  $id, $path = $_.Split(',', 2)
  $d = Join-Path $Out $id; New-Item -ItemType Directory -Force -Path $d | Out-Null
  $dur = [double](& ffprobe -v error -show_entries format=duration -of csv=p=0 $path)
  $hook = @(0.0, 0.25, 0.5, 1.0, 1.5, 2.0, 2.5, 3.0)
  $contact = 0..15 | ForEach-Object { $dur * ($_ + 0.5) / 16 }
  $jobs = @()
  foreach ($t in $hook) { $w = $(if ($t -eq 0) {540} else {260}); $jobs += ,@($t, $w, 'h') }
  foreach ($t in $contact) { $jobs += ,@($t, 240, 'c') }
  $jobs | ForEach-Object -Parallel {
    $t, $w, $k = $_; $name = '{0}_{1:0.000}.jpg' -f $k, $t
    & ffmpeg -v error -y -ss ('{0:0.000}' -f $t) -i $using:path -frames:v 1 -vf "scale=${w}:-2" -q:v 3 (Join-Path $using:d $name)
  } -ThrottleLimit 8
  "{0},{1:0.000}" -f $id, $dur | Out-File -Append -Encoding utf8 (Join-Path $Out 'durations.csv')
}
"elapsed_s={0:0.0}" -f $sw.Elapsed.TotalSeconds | Out-File -Encoding utf8 (Join-Path $Out 'timing.txt')
Compress-Archive -Force -Path (Join-Path $Out '*') -DestinationPath ($Out.TrimEnd('\') + '.zip')
Get-Content (Join-Path $Out 'timing.txt')
