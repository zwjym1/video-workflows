import React, {useCallback, useEffect, useMemo, useRef, useState} from 'react';
import {createRoot} from 'react-dom/client';
import {Player, PlayerRef} from '@remotion/player';
import {project as P} from 'align-project';
import type {Shot, Timeline} from './types';

const FPS = P.fps, DUR = P.durationInFrames / FPS;
const LABEL_W = 170;
const r3 = (x: number) => Math.round(x * 1000) / 1000;
const fmt = (t: number) => { const m = Math.floor(t / 60), s = t - m * 60; return `${m}:${s.toFixed(2).padStart(5, '0')}`; };
const clamp = (x: number, a: number, b: number) => Math.max(a, Math.min(b, x));
const outOf = (s: Shot) => s.in + (s.end - s.start) * s.rate;
const WORDS = P.sentences.flatMap((s) => s.words.map((w) => ({...w, si: s.i})));
const SNAPS = [...new Set([...WORDS.flatMap((w) => [w.start, w.end]), ...P.sentences.flatMap((s) => [s.start, s.end])])].sort((a, b) => a - b);
const COLORS = ['#4fd1ff', '#ffb347', '#ff6b81', '#7ee787', '#c39bff', '#ffd25a', '#5eead4', '#f0abfc'];

/* ---------- waveform ---------- */
const usePeaks = (src: string) => { const [peaks, set] = useState<Float32Array | null>(null);
  useEffect(() => { (async () => { const buf = await (await fetch('/' + src)).arrayBuffer(); const ac = new AudioContext(); const a = await ac.decodeAudioData(buf);
    const d = a.getChannelData(0), hop = Math.floor(a.sampleRate / 100), n = Math.ceil(d.length / hop), p = new Float32Array(n);
    for (let i = 0; i < n; i++) { let m = 0; for (let j = i * hop; j < Math.min(d.length, (i + 1) * hop); j++) m = Math.max(m, Math.abs(d[j])); p[i] = m; } set(p); ac.close(); })(); }, [src]);
  return peaks; };
const Wave: React.FC<{peaks: Float32Array | null; pps: number; h: number}> = ({peaks, pps, h}) => { const ref = useRef<HTMLCanvasElement>(null);
  useEffect(() => { const c = ref.current; if (!c || !peaks) return; const w = Math.min(32000, Math.ceil(DUR * pps)); c.width = w; c.height = h; const g = c.getContext('2d')!;
    g.clearRect(0, 0, w, h); g.fillStyle = '#3b82f6'; for (let x = 0; x < w; x++) { const i0 = Math.floor((x / pps) * 100), i1 = Math.floor(((x + 1) / pps) * 100); let m = 0; for (let i = i0; i <= i1 && i < peaks.length; i++) m = Math.max(m, peaks[i]); const y = m * h * 0.95; g.fillRect(x, (h - y) / 2, 1, Math.max(1, y)); } }, [peaks, pps, h]);
  return <canvas ref={ref} style={{display: 'block', height: h}} />; };

/* ---------- source preview ---------- */
const SourcePanel: React.FC<{shot: Shot | null; t: number; cursor: number; setCursor: (x: number) => void; update: (p: Partial<Shot>, label?: string) => void; keepDur: boolean; setKeepDur: (b: boolean) => void; onPreview: () => void; onReset: () => void; srcs: string[]}> =
  ({shot, t, cursor, setCursor, update, keepDur, setKeepDur, onPreview, onReset, srcs}) => {
  const v = useRef<HTMLVideoElement>(null); const [dur, setDur] = useState(0);
  useEffect(() => { if (v.current && Math.abs(v.current.currentTime - cursor) > 0.02) v.current.currentTime = cursor; }, [cursor, shot?.src]);
  if (!shot) return <div className="src empty">在下方时间线点选一个实拍镜头<br />（彩色条）开始对齐</div>;
  const out = outOf(shot); const inShot = t >= shot.start && t < shot.end;
  const num = (k: 'start' | 'end' | 'in' | 'rate', step: number) => <label className="num"><span>{({start: '时间线开始', end: '时间线结束', in: '素材入点', rate: '速度'} as any)[k]}</span>
    <button onClick={() => update({[k]: r3(shot[k] - step)} as any, k)}>−</button>
    <input type="number" step={step} value={shot[k]} onChange={(e) => update({[k]: r3(+e.target.value)} as any, k)} />
    <button onClick={() => update({[k]: r3(shot[k] + step)} as any, k)}>+</button></label>;
  const setOut = (o: number) => { if (o <= shot.in + 0.03) return; if (keepDur) update({rate: r3((o - shot.in) / (shot.end - shot.start))}, 'out'); else update({end: r3(shot.start + (o - shot.in) / shot.rate)}, 'out'); };
  return <div className="src">
    <div className="srchead"><b style={{color: shot.__color}}>{shot.label ?? shot.id}</b> <select value={shot.src} onChange={(e) => update({src: e.target.value}, 'src')}>{srcs.map((s) => <option key={s}>{s}</option>)}</select></div>
    <video ref={v} src={'/' + shot.src} muted preload="auto" onLoadedMetadata={(e) => setDur((e.target as HTMLVideoElement).duration)} />
    <div className="srcinfo">素材时间 <b>{fmt(cursor)}</b> {inShot ? <span className="ok">● 跟随播放头</span> : <span className="dim">播放头不在此镜头内</span>}</div>
    <div className="scrub" onPointerDown={(e) => { const el = e.currentTarget; const go = (x: number) => { const r = el.getBoundingClientRect(); setCursor(clamp(((x - r.left) / r.width) * dur, 0, dur)); }; go(e.clientX); el.setPointerCapture(e.pointerId); el.onpointermove = (ev) => go(ev.clientX); el.onpointerup = () => (el.onpointermove = null); }}>
      {dur > 0 && <><div className="used" style={{left: `${(shot.in / dur) * 100}%`, width: `${((out - shot.in) / dur) * 100}%`}} />
        <div className="cur" style={{left: `${(cursor / dur) * 100}%`}} /></>}
    </div>
    <div className="srcrow"><span>入点 {fmt(shot.in)}</span><span>出点 {fmt(out)}</span><span>素材总长 {fmt(dur)}</span></div>
    <div className="btns">
      <button onClick={() => setCursor(clamp(cursor - 1 / 30, 0, dur))}>◀ 1帧</button><button onClick={() => setCursor(clamp(cursor + 1 / 30, 0, dur))}>1帧 ▶</button>
      <button className="pri" title="I" onClick={() => update({in: r3(cursor)}, 'in')}>设为入点 (I)</button>
      <button className="pri" title="O" onClick={() => setOut(cursor)}>设为出点 (O)</button>
      <button className="pri" title="A" onClick={() => update({in: r3(cursor - (t - shot.start) * shot.rate)}, 'in')}>这一帧对准播放头 (A)</button>
    </div>
    <label className="chk"><input type="checkbox" checked={keepDur} onChange={(e) => setKeepDur(e.target.checked)} /> 设出点时保持镜头时长（改变速度）</label>
    <div className="nums">{num('start', 1 / FPS)}{num('end', 1 / FPS)}{num('in', 1 / FPS)}{num('rate', 0.05)}</div>
    <div className="btns"><button onClick={onPreview}>▶ 从镜头开头预览</button><button onClick={onReset}>恢复此镜头默认</button></div>
    {out > dur + 0.05 && dur > 0 && <div className="warn">⚠ 出点超出素材长度，结尾会黑屏/停帧</div>}
  </div>; };

/* ---------- app ---------- */
const App: React.FC = () => {
  const player = useRef<PlayerRef>(null);
  const [shots, setShots] = useState<Shot[]>(() => P.mergeShots(null));
  const [hist, setHist] = useState<{past: Shot[][]; fut: Shot[][]}>({past: [], fut: []});
  const [sel, setSel] = useState<string | null>(null);
  const [frame, setFrame] = useState(0); const [playing, setPlaying] = useState(false);
  const [pps, setPps] = useState(60); const [snap, setSnap] = useState(true); const [keepDur, setKeepDur] = useState(false);
  const [cursor, setCursor] = useState(0); const [dirty, setDirty] = useState(false); const [msg, setMsg] = useState('');
  const peaks = usePeaks(P.audio);
  const t = frame / FPS;
  const colored = useMemo(() => shots.map((s, i) => ({...s, __color: COLORS[i % COLORS.length]})) as (Shot & {__color: string})[], [shots]);
  const shot = colored.find((s) => s.id === sel) ?? null;
  const timeline: Timeline = useMemo(() => ({version: 1, composition: P.composition, fps: FPS, shots}), [shots]);
  const inputProps = useMemo(() => P.inputProps(timeline), [timeline]);
  const srcs = useMemo(() => [...new Set(P.defaultShots().map((s) => s.src).concat(shots.map((s) => s.src)))], [shots]);

  useEffect(() => { fetch('/api/timeline').then((r) => r.json()).then((j) => { setShots(P.mergeShots(j)); setMsg('已载入 ' + (j.shots?.length ?? 0) + ' 个镜头的保存值'); }).catch(() => setMsg('未找到时间线文件，使用默认值')); }, []);
  useEffect(() => { const p = player.current; if (!p) return; const f = (e: any) => setFrame(e.detail.frame); const pl = () => setPlaying(true), pa = () => setPlaying(false);
    p.addEventListener('frameupdate', f); p.addEventListener('seeked', f); p.addEventListener('play', pl); p.addEventListener('pause', pa);
    return () => { p.removeEventListener('frameupdate', f); p.removeEventListener('seeked', f); p.removeEventListener('play', pl); p.removeEventListener('pause', pa); }; }, []);
  // source cursor follows playhead inside the selected shot
  useEffect(() => { if (shot && t >= shot.start && t < shot.end) setCursor(r3(shot.in + (t - shot.start) * shot.rate)); }, [frame, sel, shot?.in, shot?.start, shot?.rate]);
  useEffect(() => { if (shot && !(t >= shot.start && t < shot.end)) setCursor(shot.in); }, [sel]);

  const commit = useCallback((next: Shot[]) => { setHist((h) => ({past: [...h.past.slice(-99), shots], fut: []})); setShots(next); setDirty(true); }, [shots]);
  const update = useCallback((id: string, p: Partial<Shot>) => commit(shots.map((s) => (s.id === id ? {...s, ...p, start: Math.max(0, p.start ?? s.start)} : s))), [shots, commit]);
  const undo = () => setHist((h) => { if (!h.past.length) return h; const prev = h.past[h.past.length - 1]; const cur = shots; setShots(prev); setDirty(true); return {past: h.past.slice(0, -1), fut: [cur, ...h.fut]}; });
  const redo = () => setHist((h) => { if (!h.fut.length) return h; const nx = h.fut[0]; const cur = shots; setShots(nx); setDirty(true); return {past: [...h.past, cur], fut: h.fut.slice(1)}; });
  const seek = (sec: number) => player.current?.seekTo(clamp(Math.round(sec * FPS), 0, P.durationInFrames - 1));
  const save = async () => { const r = await fetch('/api/timeline', {method: 'POST', body: JSON.stringify({...timeline, savedAt: new Date().toISOString()}, null, 2)}); setMsg(r.ok ? '✔ 已保存到项目（渲染会直接读取）' : '✖ 保存失败：' + (await r.text())); if (r.ok) setDirty(false); };
  const exportJson = () => { const a = document.createElement('a'); a.href = URL.createObjectURL(new Blob([JSON.stringify(timeline, null, 2)], {type: 'application/json'})); a.download = 'footage-timeline.json'; a.click(); };
  const importJson = (f: File) => f.text().then((s) => { commit(P.mergeShots(JSON.parse(s))); setMsg('已导入 ' + f.name); });

  // keyboard
  useEffect(() => { const k = (e: KeyboardEvent) => { if ((e.target as HTMLElement).tagName === 'INPUT' || (e.target as HTMLElement).tagName === 'SELECT') return;
    const p = player.current; const ctrl = e.ctrlKey || e.metaKey;
    if (ctrl && e.key.toLowerCase() === 's') { e.preventDefault(); save(); }
    else if (ctrl && (e.key.toLowerCase() === 'y' || (e.shiftKey && e.key.toLowerCase() === 'z'))) { e.preventDefault(); redo(); }
    else if (ctrl && e.key.toLowerCase() === 'z') { e.preventDefault(); undo(); }
    else if (e.code === 'Space') { e.preventDefault(); p?.toggle(); }
    else if (e.key === 'ArrowLeft') { e.preventDefault(); seek(t - (e.shiftKey ? 1 : 1 / FPS)); }
    else if (e.key === 'ArrowRight') { e.preventDefault(); seek(t + (e.shiftKey ? 1 : 1 / FPS)); }
    else if (shot && e.key.toLowerCase() === 'i') update(shot.id, {in: r3(cursor)});
    else if (shot && e.key.toLowerCase() === 'a') update(shot.id, {in: r3(cursor - (t - shot.start) * shot.rate)});
    else if (shot && e.key.toLowerCase() === 'o') { const o = cursor; if (o > shot.in) update(shot.id, keepDur ? {rate: r3((o - shot.in) / (shot.end - shot.start))} : {end: r3(shot.start + (o - shot.in) / shot.rate)}); }
    else if (e.key === 'Escape') setSel(null); };
    window.addEventListener('keydown', k); return () => window.removeEventListener('keydown', k); });
  useEffect(() => { const b = (e: BeforeUnloadEvent) => { if (dirty) { e.preventDefault(); e.returnValue = ''; } }; window.addEventListener('beforeunload', b); return () => window.removeEventListener('beforeunload', b); }, [dirty]);

  /* ---------- drag on lanes ---------- */
  const snapT = (x: number, ex: number[] = []) => { if (!snap) return x; const th = 8 / pps; let best = x, bd = th; for (const c of [...SNAPS, t, ...ex]) { const d = Math.abs(c - x); if (d < bd) { bd = d; best = c; } } return best; };
  const drag = (e: React.PointerEvent, s: Shot, mode: 'move' | 'l' | 'r') => { e.stopPropagation(); e.preventDefault(); setSel(s.id);
    const x0 = e.clientX, o = {...s}; const others = shots.filter((q) => q.id !== s.id).flatMap((q) => [q.start, q.end]); const slip = e.shiftKey && mode === 'move', alt = e.altKey;
    let moved = false; const before = shots;
    const mv = (ev: PointerEvent) => { const d = (ev.clientX - x0) / pps; if (Math.abs(ev.clientX - x0) > 2) moved = true; if (!moved) return; let p: Partial<Shot>;
      if (slip) p = {in: r3(Math.max(0, o.in - d * o.rate))};
      else if (mode === 'move') { const ns = snapT(o.start + d, others); const ne = snapT(o.end + d, others); const dd = Math.abs(ns - (o.start + d)) <= Math.abs(ne - (o.end + d)) ? ns - o.start : ne - o.end; p = {start: r3(o.start + dd), end: r3(o.end + dd)}; }
      else if (mode === 'l') { const ns = Math.min(snapT(o.start + d, others), o.end - 0.1); p = alt ? {start: r3(ns)} : {start: r3(ns), in: r3(Math.max(0, o.in + (ns - o.start) * o.rate))}; }
      else p = {end: r3(Math.max(snapT(o.end + d, others), o.start + 0.1))};
      setShots(before.map((q) => (q.id === s.id ? {...q, ...p, start: Math.max(0, p.start ?? q.start)} : q))); };
    const up = () => { window.removeEventListener('pointermove', mv); window.removeEventListener('pointerup', up); if (moved) { setHist((h) => ({past: [...h.past.slice(-99), before], fut: []})); setDirty(true); } };
    window.addEventListener('pointermove', mv); window.addEventListener('pointerup', up); };
  const seekDrag = (e: React.PointerEvent) => { const el = e.currentTarget as HTMLElement; const go = (x: number) => { const r = el.getBoundingClientRect(); seek((x - r.left) / pps); }; go(e.clientX);
    const mv = (ev: PointerEvent) => go(ev.clientX); const up = () => { window.removeEventListener('pointermove', mv); window.removeEventListener('pointerup', up); }; window.addEventListener('pointermove', mv); window.addEventListener('pointerup', up); };

  const W = DUR * pps; const scroller = useRef<HTMLDivElement>(null);
  useEffect(() => { const sc = scroller.current; if (!sc || !playing) return; const x = t * pps; if (x < sc.scrollLeft + 40 || x > sc.scrollLeft + sc.clientWidth - LABEL_W - 80) sc.scrollLeft = x - 200; }, [frame, playing]);
  const overl = (s: Shot) => shots.some((q) => q.id !== s.id && q.start < s.end - 0.02 && q.end > s.start + 0.02);
  const ticks = []; const step = pps >= 120 ? 0.5 : pps >= 40 ? 1 : 5; for (let x = 0; x <= DUR; x += step) ticks.push(x);
  const curWord = WORDS.find((w) => t >= w.start && t < w.end);

  return <div className="app">
    <header><b>素材对齐工具</b><span className="dim">{P.title} · {P.composition}</span>
      <button className={'pri' + (dirty ? ' dirty' : '')} onClick={save}>💾 保存 (Ctrl+S)</button>
      <button onClick={undo} disabled={!hist.past.length}>↶ 撤销</button><button onClick={redo} disabled={!hist.fut.length}>↷ 重做</button>
      <button onClick={exportJson}>导出 JSON</button>
      <label className="filebtn">导入 JSON<input type="file" accept=".json" onChange={(e) => e.target.files?.[0] && importJson(e.target.files[0])} /></label>
      <button onClick={() => { if (confirm('把所有镜头恢复成默认值？（可撤销）')) commit(P.defaultShots()); }}>全部恢复默认</button>
      <span className="msg">{dirty ? '● 有未保存的修改  ' : ''}{msg}</span>
    </header>
    <div className="top">
      <div className="playerwrap">
        <Player ref={player} component={P.component} inputProps={inputProps} durationInFrames={P.durationInFrames} fps={FPS} compositionWidth={P.width} compositionHeight={P.height}
          style={{width: '100%', aspectRatio: `${P.width}/${P.height}`}} controls clickToPlay={false} acknowledgeRemotionLicense />
        <div className="now"><b>{fmt(t)}</b>　第 {frame} 帧　{curWord ? <>当前字：<b className="word">{curWord.text}</b>（第 {curWord.si + 1} 句）</> : ''}</div>
      </div>
      <SourcePanel shot={shot} t={t} cursor={cursor} setCursor={setCursor} update={(p) => shot && update(shot.id, p)} keepDur={keepDur} setKeepDur={setKeepDur} srcs={srcs}
        onPreview={() => { if (shot) { seek(shot.start); player.current?.play(); } }} onReset={() => { const d = P.defaultShots().find((q) => q.id === shot?.id); if (d) update(d.id, d); }} />
    </div>
    <div className="tlbar"><span>缩放</span><input type="range" min={15} max={300} value={pps} onChange={(e) => setPps(+e.target.value)} />
      <label className="chk"><input type="checkbox" checked={snap} onChange={(e) => setSnap(e.target.checked)} /> 吸附到字/句/播放头</label>
      <span className="dim">拖动色条＝移动 · 拖左/右边缘＝裁剪 · Shift+拖色条＝换素材片段（时间线位置不变）· Alt+拖左边缘＝只改开始 · 空格播放 · ←/→ 逐帧</span></div>
    <div className="tl" ref={scroller}>
      <div className="labels" style={{width: LABEL_W}}>
        <div className="lh ruler">时间</div><div className="lh sent">句子</div><div className="lh words">逐字</div><div className="lh wave">配音波形</div><div className="lh gfx">图形段（锁定）</div>
        {colored.map((s) => <div key={s.id} className={'lh lane' + (s.id === sel ? ' sel' : '')} onClick={() => { setSel(s.id); seek(s.start); }} style={{borderLeft: `4px solid ${s.__color}`}}>{s.label ?? s.id}</div>)}
      </div>
      <div className="tracks" style={{width: W + 40}}>
        <div className="row ruler" onPointerDown={seekDrag}>{ticks.map((x) => <div key={x} className="tick" style={{left: x * pps}}>{Number.isInteger(x) ? fmt(x).replace(/\.00$/, '') : ''}</div>)}</div>
        <div className="row sent" onPointerDown={seekDrag}>{P.sentences.map((s) => <div key={s.i} className="sentb" title={s.text} style={{left: s.start * pps, width: (s.end - s.start) * pps}}>{s.i + 1}. {s.text}</div>)}</div>
        <div className="row words" onPointerDown={seekDrag}>{WORDS.map((w, k) => <div key={k} className={'wd' + (curWord === w ? ' on' : '')} style={{left: w.start * pps, width: Math.max(2, (w.end - w.start) * pps)}}>{pps > 35 ? w.text : ''}</div>)}</div>
        <div className="row wave" onPointerDown={seekDrag}><Wave peaks={peaks} pps={pps} h={56} /></div>
        <div className="row gfx">{P.graphicSegments().map((g) => <div key={g.id} className="gfxb" style={{left: g.start * pps, width: (g.end - g.start) * pps}}>{g.label}</div>)}</div>
        {colored.map((s) => <div key={s.id} className="row lane" onPointerDown={() => setSel(null)}>
          <div className={'bar' + (s.id === sel ? ' sel' : '') + (overl(s) ? ' ovl' : '')} style={{left: s.start * pps, width: Math.max(6, (s.end - s.start) * pps), background: s.__color + (s.id === sel ? 'ee' : '99')}}
            onPointerDown={(e) => drag(e, s, 'move')} onDoubleClick={() => { seek(s.start); player.current?.play(); }} title={`${s.src}\n入点 ${s.in.toFixed(2)}s → 出点 ${outOf(s).toFixed(2)}s  速度 ${s.rate}×`}>
            <div className="hl" onPointerDown={(e) => drag(e, s, 'l')} /><span>{s.src.replace(/\.mp4$/, '')} · {s.in.toFixed(2)}→{outOf(s).toFixed(2)}{s.rate !== 1 ? ` · ${s.rate}×` : ''}</span><div className="hr" onPointerDown={(e) => drag(e, s, 'r')} />
          </div></div>)}
        <div className="playhead" style={{left: t * pps}} />
      </div>
    </div>
  </div>; };

createRoot(document.getElementById('root')!).render(<App />);
