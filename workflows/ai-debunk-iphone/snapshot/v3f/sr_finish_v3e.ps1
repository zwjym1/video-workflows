$ErrorActionPreference = 'Stop'
$R = 'D:\编程\项目\视频制作\作品\2026-10-18_iPhone假货\remotion'
$S = "$R\out\_staging_v3e"
$log = "$S\finish_log.txt"
function L($m){ $line = "$(Get-Date -Format HH:mm:ss) $m"; Add-Content $log $line; Write-Output $line }
if (Test-Path C:\Users\Administrator\v3e_finish.ps1) { Move-Item -Force C:\Users\Administrator\v3e_finish.ps1 "$S\v3e_finish.ps1" }
L "start g1_out=$((Get-ChildItem "$S\g1_out" -EA SilentlyContinue|Measure).Count)"
# wait for g1 SR (existing process or restart if dead)
while ($true) {
  $n = (Get-ChildItem "$S\g1_out" -EA SilentlyContinue | Measure).Count
  $alive = Get-Process realesrgan-ncnn-vulkan -EA SilentlyContinue
  L "g1_out=$n alive=$([bool]$alive)"
  if ($n -ge 192) { break }
  if (-not $alive -and $n -lt 192) {
    L "restart g1 SR from $n"
    $ErrorActionPreference = 'Continue'
    Start-Process -WindowStyle Hidden -FilePath "$S\realesrgan\realesrgan-ncnn-vulkan.exe" -ArgumentList @('-i',"$S\g1_in",'-o',"$S\g1_out",'-n','realesrgan-x4plus','-s','4','-f','jpg','-m',"$S\realesrgan\models") -WorkingDirectory $S
    $ErrorActionPreference = 'Stop'
    Start-Sleep 5
  }
  Start-Sleep 30
}
L "g1 SR done"
$FF = (Get-ChildItem "$R\node_modules\@remotion" -Directory | Where-Object Name -like 'compositor*')[0].FullName + '\ffmpeg.exe'
if (-not (Test-Path "$S\g1_sr1440.mp4")) {
  & $FF -v error -y -framerate 24 -i "$S\g1_out\%04d.jpg" -vf "scale=1440:2560:flags=lanczos,unsharp=5:5:0.4" -c:v libx264 -crf 17 -preset slow -pix_fmt yuv420p "$S\g1_sr1440.mp4"
  L "g1 encoded $((Get-Item "$S\g1_sr1440.mp4").Length)"
}
# still for s19: frame 145 = 6.0s at 24fps (1-indexed 0145.jpg)
Copy-Item -Force "$S\g1_out\0145.jpg" "$S\g1_0145_x4.jpg"
L "still ok"
# beach
if (-not (Test-Path "$S\beach_in\0001.jpg")) {
  New-Item -ItemType Directory -Force -Path "$S\beach_in","$S\beach_out" | Out-Null
  & $FF -v error -y -i "$S\beach.mp4" -q:v 1 "$S\beach_in\%04d.jpg"
  L "beach frames $((Get-ChildItem "$S\beach_in"|Measure).Count)"
}
$bn = (Get-ChildItem "$S\beach_out" -EA SilentlyContinue | Measure).Count
$bt = (Get-ChildItem "$S\beach_in" | Measure).Count
if ($bn -lt $bt) {
  L "start beach SR have=$bn need=$bt"
  # clear partial? keep and let realesrgan skip existing by writing into out; if restart, existing files stay
  $ErrorActionPreference = 'Continue'
  & "$S\realesrgan\realesrgan-ncnn-vulkan.exe" -i "$S\beach_in" -o "$S\beach_out" -n realesrgan-x4plus -s 4 -f jpg -m "$S\realesrgan\models" 2>$null
  $ErrorActionPreference = 'Stop'
  L "beach SR done count=$((Get-ChildItem "$S\beach_out"|Measure).Count)"
}
if (-not (Test-Path "$S\beach_sr1440.mp4")) {
  & $FF -v error -y -framerate 24 -i "$S\beach_out\%04d.jpg" -vf "scale=1440:2560:flags=lanczos,unsharp=5:5:0.4" -c:v libx264 -crf 17 -preset slow -pix_fmt yuv420p "$S\beach_sr1440.mp4"
  L "beach encoded $((Get-Item "$S\beach_sr1440.mp4").Length)"
}
# stage for CopyToBox (Administrator root only)
Copy-Item -Force "$S\g1_sr1440.mp4","$S\beach_sr1440.mp4","$S\g1_0145_x4.jpg" C:\Users\Administrator\
L "FINISH_OK"
