import re,json
t=open('/workspace/pi/step3-script-final.md').read()
chs=[c for c in re.split(r'\n## ',t)[1:] if c.startswith('第')]
S=[]
for ci,c in enumerate(chs):
  buf=[]
  lines=[l.strip() for l in c.split('\n')[1:] if l.strip() and not l.startswith('[画面]') and not l.startswith('[衔接画面]')]
  lines=[l for l in lines if not l.startswith(('|','---','说明','>'))]
  for k,l in enumerate(lines):
    if l=='[停顿2秒]':
      S[-1]['pause']=2.0;continue
    buf.append(l)
    nxt=lines[k+1] if k+1<len(lines) else None
    if l[-1] in '。？！：' or nxt=='[停顿2秒]' or nxt is None:
      txt=''.join(buf);buf=[]
      S.append(dict(ch=ci,text=txt,pause=0.35))
  S[-1]['pause']=1.0
for s in S:
  x=s['text']; s['tts']=x.replace('π','派')
  s['cue']='[warm, friendly, like explaining to a classmate] ';s['speed']=1.0
  if x.endswith('？'): s['cue']='[curious, warm] ';s['speed']=0.96
  if x.startswith('想一想') or x.startswith('再想一想'): s['cue']='[gently asking, inviting the listener to think] ';s['speed']=0.94
  if '割之弥细' in x: s['cue']='[slow, reciting an ancient line] ';s['speed']=0.88
  if any(k in x for k in ['不会','七位','一千年','三百一十四万亿','一粒沙子']): s['cue']='[a little excited, with emphasis] '
  if x.endswith('：') : s['pause']=0.25
json.dump(S,open('/workspace/pi/voice/sentences.json','w'),ensure_ascii=False,indent=1)
print(len(S));[print(i,s['ch'],s['pause'],s['text']) for i,s in enumerate(S)]
