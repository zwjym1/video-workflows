# v3.2+: BGM/voice/SFX levels, BGM envelope and ducking are rendered by the composition
# (values from src/v3/footage-timeline.json "audio"). This step only normalizes loudness.
import json,subprocess,sys
src,out=sys.argv[1],sys.argv[2]
tl=json.load(open('src/v3/footage-timeline.json'));lufs=(tl.get('audio') or {}).get('lufs',-16)
subprocess.run(['ffmpeg','-v','error','-y','-i',src,'-map','0:v','-map','0:a','-c:v','copy','-af',f'loudnorm=I={lufs}:TP=-1.5:LRA=11','-c:a','aac','-b:a','160k','-ar','44100',out],check=True)
