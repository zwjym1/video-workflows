"""音效时间表（按 words.json 落在对应字上）→ src/data/sfx.json"""
import json
W = json.load(open("/workspace/iphone-fake/v2/vo/words.json"))
def wt(sid, ch, occ=1):
    n = 0
    for w in W["words"]:
        if w["id"] == sid and w["text"] == ch:
            n += 1
            if n == occ: return w["start"]
    raise KeyError((sid, ch))
S = [
    (0.10, "message_ping", 0.35),
    (wt("02", "放"), "thud_dong", 0.5),
    (wt("03", "A"), "thud_dong", 0.8), (wt("03", "A") + 0.05, "alarm_short", 0.25),
    (14.95, "shutter_burst", 0.35),
    (17.75, "message_ping", 0.35), (20.62, "message_ping", 0.3),
    (wt("10", "泡"), "bubble_gudu", 0.45),
    (wt("12", "两"), "thud_dong", 0.7), (wt("12", "两") + 0.05, "alarm_short", 0.2),
    (wt("13", "扭"), "thud_dong", 0.45),
    (wt("14", "隐"), "counter_beep", 0.35),
    (wt("16", "也"), "stamp_seal", 0.55),
    (wt("18", "人"), "thud_dong", 0.6),
    (wt("21", "自"), "stamp_seal", 0.4),
    (58.60, "counter_beep", 0.35), (wt("22", "九"), "thud_dong", 0.55),
    (wt("24", "被"), "plane_whoosh", 0.45),
    (wt("27", "空"), "plane_whoosh", 0.35), (wt("27", "海", 1), "thud_dong", 0.5),
    (79.0, "typing_clicks", 0.25),
    (83.0, "thud_dong", 0.5),
]
json.dump([{"t": round(t, 3), "file": f"sfx/{f}.wav", "vol": v} for t, f, v in S], open("src/data/sfx.json", "w"), indent=1)
print(len(S))
