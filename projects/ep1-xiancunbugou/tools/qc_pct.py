import subprocess,sys,numpy as np
p=sys.argv[1];w,h=480,270
raw=subprocess.run(['ffmpeg','-v','error','-i',p,'-vf',f'fps=2,scale={w}:{h},format=gray','-f','rawvideo','-'],capture_output=True).stdout
F=np.frombuffer(raw,np.uint8).reshape(-1,h,w).astype(np.float32)
o=np.array([np.mean(np.abs(f-np.median(f))>12) for f in F])
print('n',len(o),'P10 %.3f P50 %.3f P75 %.3f P90 %.3f P99 %.3f max %.3f'%tuple(np.percentile(o,[10,50,75,90,99]).tolist()+[o.max()]))
hi=o>=0.85;i=0;r=[]
while i<len(o):
  if hi[i]:
    j=i
    while j<len(o) and hi[j]: j+=1
    r.append((i/2,j/2));i=j
  else:i+=1
print('>=0.85 区间',r)
for k in range(0,len(o),40): print('%5ds occ=%.3f'%(k//2,o[k:k+40].mean()))
