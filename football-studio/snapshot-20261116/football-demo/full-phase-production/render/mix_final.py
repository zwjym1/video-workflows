from pathlib import Path
import subprocess,numpy as np,json,wave
from scipy.ndimage import uniform_filter1d,maximum_filter1d
R=Path(__file__).resolve().parents[1];SR=48000;END=99.36;SW=78.96;N=round(END*SR)
def dec(p):return np.frombuffer(subprocess.check_output(['ffmpeg','-v','error','-i',str(p),'-ar',str(SR),'-ac','2','-f','f32le','-']),'<f4').reshape(-1,2).copy()
def write(p,a):
 with wave.open(str(p),'w') as w:w.setparams((2,2,SR,0,'NONE','not compressed'));w.writeframes((a.clip(-.999,.999)*32767).astype('<i2').tobytes())
p=Path('/workspace/football-demo/bgm-reference-research/separated_exports/Rookie_空间阅读者_参考混音分离版_no_vocals.wav');raw=dec(p);cuts=[]
def take(a,b):return raw[round(a*SR):round(b*SR)].copy()
def cross(a,b,d):
 n=round(d*SR);x=np.linspace(0,1,n)[:,None];return np.concatenate([a[:-n],a[-n:]*(1-x)+b[:n]*x,b[n:]])
# Only authorized substantial main-music regions, with one short reprise.
a=take(0,25);b=take(94,145);c=take(110,114.56)
main=cross(cross(a,b,.8),c,.8);assert len(main)==round(SW*SR)
tail=take(149,169.4);assert len(tail)==round(20.4*SR)
bed=np.concatenate([main,tail]);vo=dec(R/'audio/VOICE_ONLY_TIMED.wav');fx=dec(R/'audio/SFX_ONLY_TIMED.wav')
# Smooth attenuation only: never fill a damaged music region by excessive gain.
energy=np.mean(bed*bed,axis=1);en=np.sqrt(uniform_filter1d(energy,size=24000,mode='nearest')+1e-10)
voice_en=np.sqrt(uniform_filter1d(np.mean(vo*vo,axis=1),size=9600,mode='nearest')+1e-10)
voice_presence=uniform_filter1d((maximum_filter1d(voice_en,size=12001)>.012).astype(float),size=9600,mode='nearest')
gain=np.minimum(.15,.021/np.maximum(en,.055));gain*=1-.32*voice_presence
# At the new film's full-speed replay, switch to passion, not reference 147s.
j=round(SW*SR);tailgain=np.minimum(.38,.087/np.maximum(en[j:],.10));tailgain*=1-.60*voice_presence[j:];gain[j:]=tailgain
bed*=gain[:,None];bed[:19200]*=np.linspace(0,1,19200)[:,None];bed[-33600:]*=np.linspace(1,0,33600)[:,None]
# A 60ms outgoing fade and incoming rise at hard music change, with no silent gap.
k=2880;bed[j-k:j]*=np.linspace(1,.16,k)[:,None];bed[j:j+k]*=np.linspace(.16,1,k)[:,None]
mix=vo+bed+fx;scale=min(1,.90/(np.max(abs(mix))+1e-10));vo*=scale;bed*=scale;fx*=scale;mix=vo+bed+fx
for name,a in [('narration.wav',vo),('bgm.wav',bed),('sfx.wav',fx),('final_mix.wav',mix)]:write(R/'out'/name,a)
report={'duration_s':END,'music_switch_s':SW,'reference_separation_not_master':True,'main_music':'李富贵《人生志在一博》参考分离可用段；非新世界杯参考同款声明','tail_music':'passion，分离轨原速','source_cuts':[{'source':[0,25],'output':[0,25]},{'source':[94,145],'output':[24.2,75.2]},{'source':[110,114.56],'output':[74.4,78.96],'short_reprise':True},{'source':[149,169.4],'output':[78.96,99.36]}],'crossfades_s':.8,'music_source':str(p),'master_scale':float(scale),'peak_dbfs':float(20*np.log10(np.max(abs(mix))+1e-12)),'human_listening':False,'limitations':'分离配乐可能残余解说/空频段与原混音音效；已避开已知严重空洞段，未声称正版母带或彻底干净。'}
(R/'out/MUSIC_EDIT_AND_MIX.json').write_text(json.dumps(report,ensure_ascii=False,indent=2));print('FINAL_MIX',len(mix)/SR,'peak',report['peak_dbfs'],flush=True)
