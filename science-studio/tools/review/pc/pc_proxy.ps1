# 在用户 PC 上做「剪辑质量 / BGM 契合」需要的轻量代理文件（只读原片，只往 -Out 新目录里写）。
# 产物：<Out>\<id>\proxy.mp4（180x320、30fps、无音轨）+ audio.flac（单声道 22.05kHz）；最后打包成 <Out>.zip，盒上用 CopyToBox 取回。
# 用法: pwsh -NoProfile -ExecutionPolicy Bypass -File pc_proxy.ps1 -List jobs.csv -Out C:\Users\<you>\Downloads\review_proxy_YYYYMMDD
# jobs.csv: id,path（UTF-8，无表头），与 pc_frames.ps1 共用。PC 不在线 → 盒上 lib/cutquality.py / lib/bgmfit.py 直接读原片（自动回退）。
param([string]$List, [string]$Out, [int]$Throttle = 4)
$ErrorActionPreference = 'Stop'
if (Test-Path $Out) { throw "Out 目录已存在，请换一个新目录名：$Out" }
New-Item -ItemType Directory -Path $Out | Out-Null
$sw = [Diagnostics.Stopwatch]::StartNew()
Get-Content -Encoding UTF8 $List | Where-Object { $_.Trim() } | ForEach-Object -Parallel {
  $id, $path = $_.Split(',', 2)
  $d = Join-Path $using:Out $id; New-Item -ItemType Directory -Force -Path $d | Out-Null
  & ffmpeg -v error -y -i $path -vf "fps=30,scale=180:320:flags=area" -an -c:v libx264 -preset veryfast -crf 20 -pix_fmt yuv420p (Join-Path $d 'proxy.mp4')
  & ffmpeg -v error -y -i $path -vn -ac 1 -ar 22050 -c:a flac (Join-Path $d 'audio.flac')
  $dur = & ffprobe -v error -show_entries format=duration -of csv=p=0 $path
  "$id,$dur" | Out-File -Encoding utf8 (Join-Path $d 'duration.txt')
} -ThrottleLimit $Throttle
"elapsed_s={0:0.0}" -f $sw.Elapsed.TotalSeconds | Out-File -Encoding utf8 (Join-Path $Out 'timing.txt')
Compress-Archive -Path (Join-Path $Out '*') -DestinationPath ($Out.TrimEnd('\') + '.zip')
Get-Content (Join-Path $Out 'timing.txt')
