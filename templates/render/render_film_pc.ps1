<#
  opto_film_v1 - full-film render on the Windows PC (RTX 3080).
  Put this script next to opto_film_v1_src.zip, then:
    powershell -ExecutionPolicy Bypass -File .\render_film_pc.ps1                 # 1080x1920 final (default, H.264 ~14 Mbps, AAC 320k)
    powershell -ExecutionPolicy Bypass -File .\render_film_pc.ps1 -Mode 720       # 720p preview
    powershell -ExecutionPolicy Bypass -File .\render_film_pc.ps1 -Mode both
  Options:
    -Concurrency N     override auto (default = 75% of logical cores, min 2)
    -Frames 2254-3457  render only a frame range (segment re-render); audio is trimmed to match
    -Force             re-render even if an up-to-date silent render exists
    -Browser shell     skip desktop Chrome and use Remotion's pinned Chrome Headless Shell
    -ZipPath / -Root   override locations
  Idempotent: re-extract only when the zip changes, npm ci only when package-lock changes,
  skip a render whose output already matches the current zip + frame range.
  Logs: <Root>\out\*.log
#>
param(
  [ValidateSet('720','1080','both')][string]$Mode = '1080',
  [int]$Concurrency = 0,
  [string]$Frames = '',
  [switch]$Force,
  [ValidateSet('chrome','shell')][string]$Browser = 'chrome',
  [string]$ZipPath = (Join-Path $PSScriptRoot 'opto_film_v1_src.zip'),
  [Parameter(Mandatory=$true)][string]$Root,  # must be a D: drive project folder (video works dir)
  [string]$ChromePath = 'C:\Program Files\Google\Chrome\Application\chrome.exe'
)
$ErrorActionPreference = 'Stop'
$sw = [Diagnostics.Stopwatch]::StartNew()
function Step($n, $msg) { Write-Host ("[{0}/7] {1}  (t+{2:mm\:ss})" -f $n, $msg, $sw.Elapsed) -ForegroundColor Cyan }
function Info($msg) { Write-Host "      $msg" }
function Run($log, [string]$cmdline) {
  # run through cmd so stderr is merged without PowerShell NativeCommandError; tee to console + log
  Info "> $cmdline"
  cmd /c "$cmdline 2>&1" | Tee-Object -FilePath $log -Append | Out-Host
  return $LASTEXITCODE
}

# ---------- 1. tools ----------
Step 1 'Checking node / npm / ffmpeg'
foreach ($t in 'node','npm.cmd','npx.cmd','ffmpeg') {
  if (-not (Get-Command $t -ErrorAction SilentlyContinue)) { throw "Missing tool: $t (install it / add to PATH)" }
}
Info ("node {0} | npm {1} | {2}" -f (node -v), (cmd /c "npm.cmd -v"), ((cmd /c "ffmpeg -hide_banner -version 2>&1") | Select-Object -First 1))
$hasProbe = [bool](Get-Command ffprobe -ErrorAction SilentlyContinue)
if (-not (Test-Path $ZipPath)) { throw "Zip not found: $ZipPath" }

# ---------- 2. extract ----------
Step 2 "Extracting $ZipPath -> $Root"
New-Item -ItemType Directory -Force $Root | Out-Null
$zipHash = (Get-FileHash $ZipPath -Algorithm SHA256).Hash
$stamp = Join-Path $Root '.zip_sha256'
if ((Test-Path $stamp) -and ((Get-Content $stamp -Raw).Trim() -eq $zipHash) -and (Test-Path (Join-Path $Root 'package.json'))) {
  Info 'Already extracted (zip unchanged) - skip'
} else {
  foreach ($d in 'src','public','audio') { $p = Join-Path $Root $d; if (Test-Path $p) { Remove-Item -Recurse -Force $p } }
  Expand-Archive -Path $ZipPath -DestinationPath $Root -Force
  Set-Content -Path $stamp -Value $zipHash -Encoding ascii
  Info 'Extracted (node_modules and out\ kept)'
}
Set-Location $Root
New-Item -ItemType Directory -Force out | Out-Null

# ---------- 3. npm ----------
Step 3 'Installing npm dependencies'
$lockHash = (Get-FileHash package-lock.json -Algorithm SHA256).Hash
$lockStamp = 'node_modules\.lock_sha256'
if ((Test-Path $lockStamp) -and ((Get-Content $lockStamp -Raw).Trim() -eq $lockHash)) {
  Info 'node_modules up to date - skip'
} else {
  $rc = Run 'out\npm.log' 'npm.cmd ci --no-audit --no-fund'
  if ($rc -ne 0) {
    Info "npm ci failed ($rc), falling back to npm install"
    $rc = Run 'out\npm.log' 'npm.cmd install --no-audit --no-fund'
    if ($rc -ne 0) { throw "npm install failed ($rc), see out\npm.log" }
  }
  Set-Content -Path $lockStamp -Value $lockHash -Encoding ascii
}

# ---------- 4. browser + smoke test ----------
Step 4 'Browser smoke test (1 still at the seg3/seg4 join, frame 2255)'
$gl = 'angle'
function Smoke() {
  if (Test-Path out\smoke.jpg) { Remove-Item out\smoke.jpg -Force }
  $rc = Run 'out\smoke.log' "npx.cmd remotion still src/index.tsx OptoFilm out/smoke.jpg --frame=2255 --scale=0.25 --gl=$gl"
  return (($rc -eq 0) -and (Test-Path out\smoke.jpg))
}
$ok = $false
if ($Browser -eq 'chrome' -and (Test-Path $ChromePath)) {
  $env:REMOTION_BROWSER_EXECUTABLE = $ChromePath
  Info "Trying desktop Chrome: $ChromePath"
  $ok = Smoke
  if (-not $ok) { Info 'Desktop Chrome failed (Chrome 132+ dropped old headless mode) - switching to Remotion Chrome Headless Shell' }
}
if (-not $ok) {
  Remove-Item Env:\REMOTION_BROWSER_EXECUTABLE -ErrorAction SilentlyContinue
  $rc = Run 'out\smoke.log' 'npx.cmd remotion browser ensure'
  $ok = Smoke
  if (-not $ok) { Info 'gl=angle failed, retrying with gl=swangle (CPU)'; $gl = 'swangle'; $ok = Smoke }
}
if (-not $ok) { throw 'Smoke test failed, see out\smoke.log' }
$browserUsed = if ($env:REMOTION_BROWSER_EXECUTABLE) { 'desktop Chrome' } else { 'Remotion Chrome Headless Shell' }
Info "OK: $browserUsed, gl=$gl -> out\smoke.jpg"

# ---------- 5/6/7 per mode ----------
if ($Concurrency -le 0) { $Concurrency = [Math]::Max(2, [int][Math]::Floor([Environment]::ProcessorCount * 0.75)) }
$fargs = ''; $suffix = ''; $aTrim = ''
if ($Frames) {
  if ($Frames -notmatch '^(\d+)-(\d+)$') { throw "-Frames must look like 2254-3457" }
  $fa = [int]$Matches[1]; $fb = [int]$Matches[2]
  $fargs = " --frames=$Frames"; $suffix = "_f$fa-$fb"
  $aTrim = [string]::Format([Globalization.CultureInfo]::InvariantCulture, '-ss {0:0.######} -t {1:0.######} ', ($fa / 30.0), (($fb - $fa + 1) / 30.0))
}
$modes = if ($Mode -eq 'both') { @('720','1080') } else { @($Mode) }
foreach ($m in $modes) {
  if ($m -eq '720') { $tag = '720p'; $q = '--scale=0.6666666666666666 --crf=18' } else { $tag = '1080'; $q = '--codec=h264 --video-bitrate=14M --pixel-format=yuv420p --jpeg-quality=92' }
  $silent = "out\opto_film_v1_${tag}${suffix}_silent.mp4"
  $final  = "out\opto_film_v1_${tag}${suffix}.mp4"
  $rstamp = "$silent.stamp"; $want = "$zipHash|$Frames|$q"
  Step 5 "Rendering OptoFilm $tag$suffix (5246 frames full film, concurrency $Concurrency, $browserUsed)"
  if (-not $Force -and (Test-Path $silent) -and (Test-Path $rstamp) -and ((Get-Content $rstamp -Raw).Trim() -eq $want)) {
    Info "$silent already up to date - skip (use -Force to redo)"
  } else {
    $t0 = $sw.Elapsed
    $rc = Run "out\render_$tag$suffix.log" "npx.cmd remotion render src/index.tsx OptoFilm $silent --gl=$gl $q --concurrency=$Concurrency$fargs"
    if ($rc -ne 0 -or -not (Test-Path $silent)) { throw "Render failed ($rc), see out\render_$tag$suffix.log" }
    Set-Content -Path $rstamp -Value $want -Encoding ascii
    Info ("Render took {0:hh\:mm\:ss}" -f ($sw.Elapsed - $t0))
  }
  Step 6 "Muxing audio\film_mix_v1.wav -> $final"
  $rc = Run "out\mux_$tag$suffix.log" "ffmpeg -hide_banner -loglevel warning -stats -y -i $silent ${aTrim}-i audio\film_mix_v1.wav -map 0:v:0 -map 1:a:0 -c:v copy -c:a aac -b:a 320k -ar 48000 -shortest -movflags +faststart $final"
  if ($rc -ne 0) { throw "ffmpeg mux failed ($rc)" }
  Step 7 "Verifying $final"
  if ($hasProbe) {
    $info = cmd /c "ffprobe -v error -show_entries stream=codec_type,width,height,nb_frames,duration -of compact=p=0:nk=1 $final 2>&1"
    $info | ForEach-Object { Info $_ }
  }
  Info ("Size {0:N1} MB -> {1}" -f ((Get-Item $final).Length / 1MB), (Resolve-Path $final))
}
Write-Host ("DONE in {0:hh\:mm\:ss}" -f $sw.Elapsed) -ForegroundColor Green
