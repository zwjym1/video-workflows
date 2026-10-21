# 在用户 PC 上执行（PowerShell）。$Root 为本地工具允许的工作目录下的版本文件夹，例如 $HOME\opto_hook2d_v4
$ErrorActionPreference = 'Stop'
Set-Location $PSScriptRoot
$env:REMOTION_BROWSER_EXECUTABLE = 'C:\Program Files\Google\Chrome\Application\chrome.exe'
if (!(Test-Path node_modules)) { npm install --no-audit --no-fund }
New-Item -ItemType Directory -Force out | Out-Null
npm run render:hook2d *> out\render.log
ffmpeg -y -i out\hook2d_v4_silent.mp4 -i audio\hook2d_v4_mix.wav -map 0:v -map 1:a -c:v copy -c:a aac -b:a 192k -shortest out\hook2d_v4_1080p.mp4 *>> out\render.log
