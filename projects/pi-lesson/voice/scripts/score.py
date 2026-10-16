import json,re,difflib,sys
from pypinyin import lazy_pinyin
from opencc import OpenCC
cc=OpenCC('t2s')
S=json.load(open('/workspace/pi/voice/sentences.json'))
D='零一二三四五六七八九'
def int2cn(n):
    if n==0: return '零'
    units=[(100000000,'亿'),(10000,'万'),(1000,'千'),(100,'百'),(10,'十')]
    def sub(n):
        s='';zero=False
        for v,u in [(1000,'千'),(100,'百'),(10,'十')]:
            q=n//v;n%=v
            if q: s+=('零' if zero else '')+D[q]+u;zero=False
            elif s: zero=True
        if n: s+=('零' if zero and s else '')+D[n]
        return s
    s=''
    for v,u in [(100000000,'亿'),(10000,'万')]:
        q=n//v;n%=v
        if q: s+=sub(q)+u
    s+=sub(n)
    if s.startswith('一十'): s=s[1:]
    return s.replace('二千','两千')
def norm(s):
    s=cc.convert(s).replace('π','派').replace('Π','派')
    s=s.replace('著','着');s=re.sub(r'(\d{4})年(?!前)',lambda m:''.join(D[int(c)] for c in m.group(1))+'年',s)
    s=re.sub(r'(\d+)\.(\d+)',lambda m:int2cn(int(m.group(1)))+'点'+''.join(D[int(c)] for c in m.group(2)),s)
    s=re.sub(r'\d+',lambda m:int2cn(int(m.group())),s)
    return re.sub(r'[^\u4e00-\u9fff]','',s)
def per(a,b):
    a,b=lazy_pinyin(a),lazy_pinyin(b);sm=difflib.SequenceMatcher(None,a,b)
    return sum(max(i2-i1,j2-j1) for op,i1,i2,j1,j2 in sm.get_opcodes() if op!='equal')/max(1,len(a))
if __name__=='__main__':
    rows=json.load(open(sys.argv[1]))
    for r in rows:
        r['asr_norm']=norm(r['asr']);r['pinyin_err']=round(per(norm(S[r['i']]['tts']),r['asr_norm']),3)
    json.dump(rows,open(sys.argv[1],'w'),ensure_ascii=False,indent=1)
    for r in rows:
        if r['pinyin_err']>0: print(r['file'],r['pinyin_err'],r['asr_norm'],'| ref',norm(S[r['i']]['tts']))
