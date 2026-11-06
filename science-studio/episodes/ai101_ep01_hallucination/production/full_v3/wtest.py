# 局部窗口快速检：python3 wtest.py t0 t1  → 渲染窗口并跑 final_check 的画面检测
import sys,subprocess,json,numpy as np,importlib.util
t0,t1=float(sys.argv[1]),float(sys.argv[2]);f0,f1=int(t0*30),int(t1*30)
subprocess.run(['python3','picture.py',str(f0),str(f1)],check=True)
spec=importlib.util.spec_from_file_location('fc','/workspace/science-studio/tools/qc/final_check.py');fc=importlib.util.module_from_spec(spec);spec.loader.exec_module(fc)
fc.BAND_REF=1080
vp=fc.video_pass(f'part_{f0:05d}.mp4',30,[],sub_band=(940,1070))
g=json.load(open('beat_grid.json'));B=g['offset']+g['period']*np.arange(400)
on=[o+t0 for o in fc.onsets(vp['d90'],30)]
hit=[o for o in on if np.min(np.abs(B-o))<=2/30+1e-6];print('onsets',[round(o,2) for o in on]);print('miss',[round(o,2) for o in on if o not in hit])
L=vp['L'];j=np.abs(L[2:]-L[:-2]);print('lumajump',round(j.max(),1),round(t0+(np.argmax(j)+2)/30,2))
print('flash',[round(x+t0,2) for x in fc.flashes(L,vp['white'],30)])
cut=(vp['H']>0.30)&(vp['A']>0.35);print('cut',[round(t0+(k+1)/30,2) for k in np.where(cut)[0]])
