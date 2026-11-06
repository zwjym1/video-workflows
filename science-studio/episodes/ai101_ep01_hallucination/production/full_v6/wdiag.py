import sys,cv2,numpy as np
f0=int(float(sys.argv[1])*30);cap=cv2.VideoCapture(f'part_{f0:05d}.mp4');F=[]
while True:
    ok,f=cap.read()
    if not ok:break
    F.append(cv2.cvtColor(cv2.resize(f,(480,270)),cv2.COLOR_BGR2GRAY).astype(int))
for t in map(float,sys.argv[2:]):
    i=int(round(t*30))-f0;d=np.abs(F[i]-F[i-1])>15;ys,xs=np.where(d)
    print(t,(xs.min()*4,ys.min()*4,xs.max()*4,ys.max()*4) if len(xs) else None,d.sum())
