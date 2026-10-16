import json,sys
# collapse Fish phoneme-tag tokens (phoneme/start/<py>/phoneme/end) into the original character
def fix(path,ch='量'):
    b=json.load(open(path));out=[];k=0
    while k<len(b):
        if b[k]['text']=='phoneme' and k+4<len(b) and b[k+1]['text']=='start':
            s=b[k]['offset'];e=max(x['offset']+x['duration'] for x in b[k:k+5]);out.append({'text':ch,'offset':s,'duration':max(.08,e-s)});k+=5
        else: out.append(b[k]);k+=1
    for j in range(len(out)-1):  # no zero/negative spans
        if out[j]['offset']+out[j]['duration']>out[j+1]['offset']+1e-6: out[j]['duration']=max(.04,out[j+1]['offset']-out[j]['offset'])
    json.dump(out,open(path,'w'),ensure_ascii=False)
    return ''.join(x['text'] for x in out)
if __name__=='__main__':
    for f in sys.argv[1:]: print(f,fix(f))
