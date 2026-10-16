import json,subprocess,sys
src,out=sys.argv[1],sys.argv[2];extra=sys.argv[3:] 
A=json.load(open('src/v3/align.json'))['sentences'];q=A[11]['start']-0.1;end=A[-1]['end']+1.6
v='public/v3/voice-v3.wav'
fc=(f"[2:a]atrim=0:{q+0.35},afade=t=out:st={q-0.05}:d=0.4,volume=0.85[a];"
    f"[3:a]atrim=0:{end-q+0.1},afade=t=in:d=0.25,adelay={int((q-0.05)*1000)}|{int((q-0.05)*1000)}[b];"
    f"[a][b]amix=inputs=2:normalize=0,atrim=0:{end},afade=t=out:st={end-1.4}:d=1.4,volume=0.22[bg];"
    f"[bg][1:a]sidechaincompress=threshold=0.02:ratio=8:attack=15:release=350:makeup=1[duck];"
    f"[0:a][duck]amix=inputs=2:normalize=0,loudnorm=I=-16:TP=-1.5:LRA=11[m]")
subprocess.run(['ffmpeg','-v','error','-y','-i',src,'-i',v,'-i','public/v3/bgm_A.wav','-i','public/v3/bgm_B.wav','-filter_complex',fc,'-map','0:v','-map','[m]','-c:v','copy','-c:a','aac','-b:a','160k','-ar','44100',*extra,out],check=True)
