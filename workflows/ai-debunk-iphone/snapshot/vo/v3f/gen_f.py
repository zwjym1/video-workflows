"""V3f：去品牌/平台词，重生成 6 个单元。同 v3c/v3d 设置：cfd828…、s2.1-pro-free、temperature 0.65、speed 1.25，无情绪标记。密钥只在 tts.py 里读环境变量，不打印。"""
import sys, os, re
sys.path.insert(0, "/workspace/iphone-fake/v2/vo")
from tts import synth
from concurrent.futures import ThreadPoolExecutor
NEW = {"04": "但那艘船，是真的。", "09": "有人问 AI：这是真的吗？", "18": "专业机构一查，有隐形水印，", "19": "是 AI 工具做的。",
       "28": "检测工具一测，", "29": "AI 概率九成九以上。", "30": "不少账号也信了。", "31": "这波，转发的人也被 AI 骗了。"}
UNITS = {"04": ["04"], "09": ["09"], "18-19": ["18", "19"], "28-29": ["28", "29"], "30": ["30"], "31": ["31"]}
def tt(t): return re.sub(r"(?<![A-Za-z])AI(?![A-Za-z])", "A I", t)
def job(a):
    u, k = a; p = f"takes/{u}_f{k}"
    if os.path.exists(p + ".wav"): return
    text = tt("".join(NEW[s] for s in UNITS[u]))
    for i in range(3):
        try: synth(text, p, "cfd828bdf120410c923fac0056c687c2", 1.25); print(u, k, "ok", flush=True); return
        except Exception as e: print(u, k, "ERR", str(e).replace(os.environ.get("FISH_API_KEY", "\0"), "***")[:150], flush=True)
if __name__ == "__main__":
    with ThreadPoolExecutor(4) as ex: list(ex.map(job, [(u, k) for u in UNITS for k in (1, 2, 3)]))
