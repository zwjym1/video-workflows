"""高清录屏：headless Chromium 逐帧截图(1280x720 CSS @DPR1.5 = 1920x1080)，注入可见光标，缓动移动，记录真实点击坐标，ffmpeg 合成 + fx_lib 点击波纹。"""
import subprocess,math,json,io,time
from playwright.sync_api import sync_playwright
RIP='/workspace/science-studio/assets/fx_lib/clips/click_ripple.webm'
CUR_JS=r'''(()=>{function mk(){if(document.getElementById('__cur'))return;const d=document.createElement('div');d.id='__cur';
d.innerHTML='<svg width="34" height="44" viewBox="0 0 34 44"><path d="M2 2 L2 36 L11 28 L17 42 L23 39 L17 26 L29 26 Z" fill="#fff" stroke="#111" stroke-width="2.5" stroke-linejoin="round"/></svg>';
d.style.cssText='position:fixed;left:-100px;top:-100px;z-index:2147483647;pointer-events:none;filter:drop-shadow(0 0 6px rgba(120,170,255,.95)) drop-shadow(0 2px 3px rgba(0,0,0,.5));transition:transform .08s';
document.documentElement.appendChild(d);}
window.__mv=(x,y,p)=>{mk();const d=document.getElementById('__cur');d.style.left=(x-3)+'px';d.style.top=(y-3)+'px';d.style.transform=p?'scale(.82)':'scale(1)';};
document.addEventListener('DOMContentLoaded',mk);})();'''
def ease(t):return t*t*(3-2*t) if t<1 else 1
class Rec:
    def __init__(s,out,url,fps=30,zoom=None,wait='networkidle',locale='zh-CN'):
        s.out,s.fps=out,fps;s.clicks=[];s.n=0;s.x,s.y=640,600
        s.pw=sync_playwright().start()
        s.br=s.pw.chromium.launch(executable_path='/usr/bin/google-chrome',headless=True,args=['--no-sandbox','--hide-scrollbars'])
        s.ctx=s.br.new_context(viewport={'width':1280,'height':720},device_scale_factor=1.5,locale=locale,
            user_agent='Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/130.0 Safari/537.36')
        s.ctx.add_init_script(CUR_JS);s.p=s.ctx.new_page()
        try:s.p.goto(url,wait_until=wait,timeout=60000)
        except Exception:
            s.br.close();s.pw.stop();raise
        s.p.wait_for_timeout(800)
        if zoom:s.p.evaluate(f'document.body.style.zoom={zoom}')
        s.ff=subprocess.Popen(['ffmpeg','-v','error','-y','-f','image2pipe','-framerate',str(fps),'-c:v','png','-i','-','-c:v','libx264','-crf','16','-preset','medium','-pix_fmt','yuv420p',out+'.raw.mp4'],stdin=subprocess.PIPE)
        s.cur(False)
    def cur(s,pressed):s.p.evaluate(f'window.__mv&&window.__mv({s.x},{s.y},{str(pressed).lower()})')
    def shot(s,k=1):
        img=s.p.screenshot(type='png')
        for _ in range(k):s.ff.stdin.write(img);s.n+=1
    def hold(s,sec,live=False):
        n=int(sec*s.fps)
        if live:
            for _ in range(n):s.shot()
        else:s.shot(max(n,1))
    def move(s,x,y,sec=0.7,arc=0.12):
        x0,y0=s.x,s.y;n=max(int(sec*s.fps),6);dx,dy=x-x0,y-y0;L=math.hypot(dx,dy)+1e-6
        for i in range(1,n+1):
            t=ease(i/n);off=math.sin(math.pi*t)*arc*L
            s.x=x0+dx*t-dy/L*off;s.y=y0+dy*t+dx/L*off
            s.p.mouse.move(s.x,s.y);s.cur(False);s.shot()
        s.x,s.y=x,y
    def click(s,hover=0.25):
        s.hold(hover);s.clicks.append((s.n/s.fps,s.x*1.5,s.y*1.5))
        s.p.mouse.down();s.cur(True);s.shot(3);s.p.mouse.up();s.cur(False);s.p.wait_for_timeout(120);s.shot(2)
    def to(s,sel,sec=0.7,dx=0,dy=0):
        b=s.p.locator(sel).first.bounding_box();s.move(b['x']+b['width']/2+dx,b['y']+b['height']/2+dy,sec)
    def type(s,text,cps=9):
        for ch in text:
            s.p.keyboard.type(ch);s.shot(max(1,int(s.fps/cps)))
    def range_box(s,text,nth=0):
        return s.p.evaluate('''([t,nth])=>{const w=document.createTreeWalker(document.body,NodeFilter.SHOW_TEXT);let n,c=0;
        while(n=w.nextNode()){let i=n.data.indexOf(t);if(i>=0){if(c++<nth)continue;const r=document.createRange();r.setStart(n,i);r.setEnd(n,i+t.length);
        const rs=r.getClientRects();const a=rs[0],b=rs[rs.length-1];return {x0:a.left,y0:a.top+a.height/2,x1:b.right,y1:b.top+b.height/2,top:a.top}}}return null}''',[text,nth])
    def scroll_to_text(s,text,frac=0.45,sec=1.0):
        r=s.range_box(text);
        if not r:raise Exception('text not found: '+text)
        dy=r['top']-720*frac;n=int(sec*s.fps);done=0
        for i in range(1,n+1):
            tgt=dy*ease(i/n);s.p.mouse.wheel(0,tgt-done);done=tgt;s.p.wait_for_timeout(15);s.cur(False);s.shot()
        s.p.wait_for_timeout(300);s.shot()
    def select(s,text,nth=0,sec=0.9):
        r=s.range_box(text,nth);s.move(r['x0']+1,r['y0'],0.8);s.hold(0.2)
        s.clicks.append((s.n/s.fps,s.x*1.5,s.y*1.5));s.p.mouse.down();n=int(sec*s.fps)
        x0=s.x
        for i in range(1,n+1):
            s.x=x0+(r['x1']+1-x0)*ease(i/n);s.y=r['y1'];s.p.mouse.move(s.x,s.y);s.cur(True);s.shot()
        s.p.mouse.up();s.cur(False);s.shot()
    def js(s,code):return s.p.evaluate(code)
    def close(s):
        s.ff.stdin.close();s.ff.wait();s.br.close();s.pw.stop()
        c=s.clicks;f=[];cur='0:v'
        if c:
            f.append(f'[1:v]format=yuva420p,split={len(c)}'+''.join(f'[r{i}]' for i in range(len(c))))
            for i,(t,x,y) in enumerate(c):
                f.append(f'[r{i}]setpts=PTS-STARTPTS+{t:.3f}/TB[q{i}]');f.append(f'[{cur}][q{i}]overlay={x-150:.0f}:{y-150:.0f}:eof_action=pass[v{i}]');cur=f'v{i}'
            subprocess.run(['ffmpeg','-v','error','-y','-i',s.out+'.raw.mp4','-c:v','libvpx-vp9','-i',RIP,'-filter_complex',';'.join(f),'-map',f'[{cur}]','-c:v','libx264','-crf','16','-pix_fmt','yuv420p',s.out],check=True)
        else:subprocess.run(['cp',s.out+'.raw.mp4',s.out])
        json.dump(c,open(s.out+'.clicks.json','w'));print(s.out,s.n/s.fps,'s clicks',len(c))
