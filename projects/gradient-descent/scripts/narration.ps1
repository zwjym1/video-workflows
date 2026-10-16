$ErrorActionPreference = 'Stop'
Add-Type -AssemblyName System.Speech
$synth = New-Object System.Speech.Synthesis.SpeechSynthesizer
$synth.SelectVoice('Microsoft Huihui Desktop')
$synth.Rate = 2
$segments = @(
  '和 AI 改作品，你是不是也说过：再高级一点？',
  '把感觉拆成四件事。位置，哪里要改？问题，哪里不好？目标，改成什么？限制，保留什么？',
  '比如这个页面。标题太小，重点不清。把标题放大，说明弱化；按钮保留原来的青色。每一条，都能检查。',
  '再看前后对比。把模糊的不满意，写成看得见的变化。'
)
$timings = @()
$start = 0
for ($i = 0; $i -lt $segments.Count; $i++) {
  $path = Join-Path $PWD "public/voice-$i.wav"
  $synth.SetOutputToWaveFile($path)
  $synth.Speak($segments[$i])
  $synth.SetOutputToNull()
  $duration = [double](& ffprobe -v error -show_entries format=duration -of default=noprint_wrappers=1:nokey=1 $path)
  $frames = [int][Math]::Ceiling(($duration + 0.65) * 30)
  $timings += @{start=$start; frames=$frames; text=$segments[$i]; duration=$duration}
  $start += $frames
}
$timings | ConvertTo-Json | Set-Content -Encoding UTF8 src/timings.json
$synth.Dispose()

