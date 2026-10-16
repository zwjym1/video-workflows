"""Edge Yunxi narration for the gradient descent demonstration."""
import asyncio, json, math, subprocess
from pathlib import Path
import edge_tts
ROOT=Path(__file__).resolve().parents[1]
TEXTS=[
 "AI学习，到底在改什么？把两个参数，画成一张地图。位置代表参数，高度代表误差。",
 "根据当前位置的坡度，朝误差减小的方向，调整一步。再计算，再调整，这就是梯度下降。",
 "步子也有讲究。太小，走得慢；太大，可能来回跳。换回合适的步长，更稳地降低误差。",
 "这是两参数示意，真实模型维度更高。球表示参数位置，不是自己滚下山。"
]
async def main():
 result=[]; start=0
 for i,text in enumerate(TEXTS):
  raw=ROOT/f'public/gradient-{i}-raw.mp3'; audio=ROOT/f'public/gradient-{i}.mp3'; meta=ROOT/f'public/gradient-{i}.jsonl'
  await edge_tts.Communicate(text,'zh-CN-YunxiNeural',rate='+10%',boundary='WordBoundary').save(str(raw),str(meta))
  subprocess.run(['ffmpeg','-y','-v','error','-i',str(raw),'-af',f'apad=pad_dur={0.35 if i<3 else 0.7}','-c:a','libmp3lame','-b:a','128k',str(audio)],check=True)
  duration=float(subprocess.check_output(['ffprobe','-v','error','-show_entries','format=duration','-of','default=noprint_wrappers=1:nokey=1',str(audio)],text=True))
  bounds=[]
  for line in meta.read_text(encoding='utf8').splitlines():
   b=json.loads(line);bounds.append({'text':b['text'],'offset':b['offset']/1e7,'duration':b['duration']/1e7})
  item={'audio':audio.name,'text':text,'start':start,'duration':duration,'frames':math.ceil(duration*30),'boundaries':bounds};result.append(item);start+=item['frames']
  print(json.dumps({'segment':i,'start':item['start'],'frames':item['frames'],'duration':duration}),flush=True)
 (ROOT/'src/gradient/timing.json').write_text(json.dumps(result,ensure_ascii=False,indent=2),encoding='utf8')
 print(f'{start} frames / {start/30:.3f}s')
if __name__=='__main__':asyncio.run(main())
