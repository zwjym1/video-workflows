# -*- coding: utf-8 -*-
"""实拍素材裁切：每个镜头预先裁成 1080x1920@30（已含变速/调色），Remotion 只做单向慢推。"""
import subprocess, json, sys
from pathlib import Path
ROOT=Path(__file__).resolve().parent; V=ROOT.parent/'research/field/v'
SRC={'jn':'7699974715628178738','am':'7699839721425390882','ws':'7699893173379690105','tl':'7699881476779184315','cc':'7700520059432602943'}
# name: (src, ss, out_dur, speed, cx0, cx1, y0, y1, gamma, credit)
C={
 'c01_am_open':  ('am',9.0,1.35,1.0, 2080,2120, 0,2160, 1.2,'画面：Atumu（山西忻州）','delogo=x=100:y=1650:w=1580:h=240'),  # 原片左下自带字幕在夜空上，delogo 抹掉
 'c02_jn_city':  ('jn',1.05,1.25,0.68, 2110,2110, 0,1990, 1.15,'画面：AlphaStar（济南千佛山）'),
 'c03_jn_ufo':   ('jn',9.40,0.95,1.0, 2700,2650, 0,2160, 1.0,'画面：AlphaStar（尼康600mm）'),
 'c04_am_rocket':('am',5.40,1.07,1.8, 3070,3070, 0,2160, 1.9,'画面：Atumu（山西忻州）'),
 'c05_cc_lift':  ('cc',102.3,1.18,1.55, 1000,1000, 0,780, 0.9,'画面：央视 CCTV-13',"curves=all='0/0 0.5/0.46 0.85/0.74 1/0.86'"),  # v6e：源入点 101.0→102.3（101–102 是雾里光团、箭体几乎不动；102.3 起箭体上升、喷焰清楚），倍速 2.2→1.55，可见源 102.3–104.76（<104.97 内切）；高光恢复 v6c（顶 0.86）
 'c06b_cc_ty':   ('cc',105.4,1.20,1.6, 1005,1005, 170,820, 1.0,'画面：央视 CCTV-13（太原网友拍摄）',"curves=all='0/0 0.35/0.35 0.55/0.67 0.8/0.95 1/1'"),  # v6g：尾迹提亮实测 17%→约 20.5%（天空 −1.6%）；v6f：去掉 1010→1000 微摇（固定 1005）；尾迹（亮于天空的部分）提亮约 20%，天空不动  # v6 新增：太原网友拍的尾迹，配「从太原起飞」；裁掉台标/字幕条/角标
 'c06_am_rise':  ('am',2.10,1.61,1.2, 1900,1720, 0,1790, 1.35,'画面：Atumu（山西忻州）'),
 'c07_cc_bj':    ('cc',63.5,0.84,2.4, 990,990, 150,840, 1.0,'画面：央视 CCTV-13（北京网友拍摄）'),
 'c08_tl_sx':    ('tl',25.5,0.84,1.5, 820,820, 0,1080, 1.35,'画面：玻纤轻木（太原理工大学）','unsharp=5:5:0.7'),  # v6h：取景固定（不摇）框住尾迹头部（片内头部实测 ≈375,270→295,300，推中心取 340,275），源分辨率适度锐化；推由 Shots PUSH 做
 'c09_jn_sd':    ('jn',7.25,0.84,1.0, 2800,2760, 560,2160, 1.15,'画面：AlphaStar（济南千佛山）'),
 'c10_tl_climb': ('tl',30.0,1.34,6.0, 1100,1180, 0,900, 1.1,'画面：玻纤轻木（太原理工大学）'),
 'c11_ws_lit':   ('ws',60.0,2.50,5.0, 1950,1700, 0,2160, 1.15,'画面：Windsky'),
 'c12_ws_why':   ('ws',99.0,1.75,3.0, 1500,1450, 0,2160, 1.1,'画面：Windsky'),
 'c13_am_burst': ('am',8.40,3.35,2.0, 2950,1950, 0,2160, 1.25,'画面：Atumu（山西忻州）'),
 'c14_ws_ice':   ('ws',125.0,3.00,4.5, 2100,2150, 0,2160, 1.05,'画面：Windsky'),
 'c15_am_jelly': ('am',23.4,3.40,1.7, 2650,2550, 0,2160, 1.25,'画面：Atumu（山西忻州）'),
 'c16_tl_campus':('tl',16.0,2.10,1.0, 1300,1250, 0,1080, 1.15,'画面：玻纤轻木（太原理工大学）'),
 'c17_ws_clear': ('ws',30.0,3.70,4.0, 1550,1750, 0,2160, 1.1,'画面：Windsky'),
 'c18_ws_empty': ('ws',0.5,2.80,2.5, 1900,1900, 0,2160, 1.1,'画面：Windsky'),
 'c19_jn_end':   ('jn',5.3,2.70,1.0, 2600,2500, 0,1990, 1.1,'画面：AlphaStar（济南千佛山）'),
}
import json as _j
_cj=_j.load(open(ROOT.parent/'sfx/cuts_v2.json'));_cu=_cj['cuts']
DUR={n:round(((_cu[i+1][1] if i+1<len(_cu) else _cj['total'])-t)+0.25,3) for i,(n,t) in enumerate(_cu)}
def run(name):
    k,ss,_d,sp,cx0,cx1,y0,y1,gam,_=C[name][:10]; pre=(C[name][10]+',') if len(C[name])>10 else ''
    dur=DUR[name]
    h=y1-y0; w=round(h*9/16/2)*2; T=dur*sp
    x=f"min(max(0,({cx0}+({cx1}-{cx0})*t/{T})-{w}/2),iw-{w})"
    vf=(f"{pre}crop={w}:{h}:'{x}':{y0},scale=1080:1920:flags=lanczos,setpts=(PTS-STARTPTS)/{sp},fps=30,"
        f"eq=gamma={gam}:saturation=1.08,format=yuv420p")
    out=ROOT/f'{name}.mp4'
    subprocess.run(['ffmpeg','-v','error','-y','-ss',str(ss),'-t',str(T+0.2),'-i',str(V/f'douyin_{SRC[k]}'/'video.mp4'),'-vf',vf,'-an','-t',str(dur+0.1),'-c:v','libx264','-crf','15','-preset','fast',str(out)],check=True)
    r=subprocess.run(['ffmpeg','-v','error','-i',str(out),'-vf','scale=108:192,signalstats,metadata=print:key=lavfi.signalstats.YAVG:file=-','-f','null','-'],capture_output=True,text=True).stdout
    ys=[float(l.split('=')[1]) for l in r.splitlines() if 'YAVG' in l]
    return dict(name=name,min=round(min(ys),1),mean=round(sum(ys)/len(ys),1))
if __name__=='__main__':
    from concurrent.futures import ThreadPoolExecutor
    names=sys.argv[1:] or list(C)
    with ThreadPoolExecutor(6) as ex:
        for r in ex.map(run,names): print(r)
    json.dump({k:dict(src=SRC[v[0]],ss=v[1],dur=v[2],speed=v[3],credit=v[9],pre=(v[10] if len(v)>10 else '')) for k,v in C.items()},open(ROOT/'clips_meta.json','w'),ensure_ascii=False,indent=1)
