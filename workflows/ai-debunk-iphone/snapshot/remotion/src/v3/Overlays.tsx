import React from 'react';
import {Img, interpolate, spring, staticFile, Easing} from 'remotion';
import {FONT, GREEN, INK, PAPER, RED, YELLOW, clamp} from './theme';

export type O = Record<string, any>;
export type Ctx = {t: number; fps: number; shotEnd: number};
const F = `${FONT}, "Noto Sans CJK SC", sans-serif`;
const ease = Easing.bezier(0.22, 1, 0.36, 1);
const lf = (o: O, c: Ctx) => (c.t - o.t) * c.fps; // 出现后的帧数
const sp = (f: number, fps: number, damping = 11, stiffness = 260) => spring({frame: f, fps, config: {damping, stiffness}});
const colorOf = (c: string) => (c === 'red' ? RED : c === 'green' ? GREEN : c === 'yellow' ? YELLOW : c === 'gray' ? '#8A8A8A' : c === 'white' ? '#FFFFFF' : c);

// 世界坐标里的叠加层（跟摄像机一起推拉）
export const WORLD_KINDS = new Set(['img', 'dash', 'ring', 'cursor', 'hl', 'underline', 'leader', 'wavy', 'dashrect', 'waves', 'sparkle', 'penring', 'bubbles', 'cross', 'search', 'stamp']);

const Ellipse: React.FC<{cx: number; cy: number; rx: number; ry: number; rot?: number; stroke: string; w: number; dash?: string; offset?: number; draw?: number; glow?: boolean}> = ({cx, cy, rx, ry, rot = 0, stroke, w, dash, offset = 0, draw = 1, glow = true}) => {
  const L = Math.PI * (3 * (rx + ry) - Math.sqrt((3 * rx + ry) * (rx + 3 * ry)));
  const pad = w * 2 + 8;
  return (
    <svg style={{position: 'absolute', left: cx - rx - pad, top: cy - ry - pad, overflow: 'visible', filter: glow ? 'drop-shadow(0 0 4px rgba(0,0,0,.6))' : undefined}} width={2 * (rx + pad)} height={2 * (ry + pad)}>
      <g transform={`rotate(${rot} ${rx + pad} ${ry + pad})`}>
        {dash ? (
          <ellipse cx={rx + pad} cy={ry + pad} rx={rx} ry={ry} fill="none" stroke={stroke} strokeWidth={w} strokeDasharray={dash} strokeDashoffset={offset} strokeLinecap="round" opacity={draw < 1 ? draw : 1} />
        ) : (
          <ellipse cx={rx + pad} cy={ry + pad} rx={rx} ry={ry} fill="none" stroke={stroke} strokeWidth={w} strokeDasharray={`${L * draw} ${L}`} strokeLinecap="round" />
        )}
      </g>
    </svg>
  );
};

const Cursor: React.FC<{x: number; y: number; press?: number}> = ({x, y, press = 0}) => (
  <svg style={{position: 'absolute', left: x - 4, top: y - 2, overflow: 'visible', transform: `scale(${1 - press * 0.12})`, transformOrigin: '4px 2px', filter: 'drop-shadow(0 3px 5px rgba(0,0,0,.55))'}} width={46} height={62}>
    <path d="M4 2 L4 50 L16 39 L25 58 L33 54 L24 36 L40 36 Z" fill="#FFFFFF" stroke="#111" strokeWidth={3} strokeLinejoin="round" />
  </svg>
);

const lerpPath = (path: number[][], t: number): [number, number] => {
  if (t <= path[0][0]) return [path[0][1], path[0][2]];
  for (let i = 0; i < path.length - 1; i++) {
    const [t0, x0, y0] = path[i], [t1, x1, y1] = path[i + 1];
    if (t <= t1) {
      const k = ease((t - t0) / Math.max(1e-3, t1 - t0));
      return [x0 + (x1 - x0) * k, y0 + (y1 - y0) * k];
    }
  }
  const l = path[path.length - 1];
  return [l[1], l[2]];
};

export const Overlay: React.FC<{o: O; c: Ctx}> = ({o, c}) => {
  const f = lf(o, c);
  const {fps, t} = c;
  switch (o.k) {
    case 'img': {
      let tx = 0, ty = 0, sc = 1, op = 1, rot = o.rot ?? 0;
      const e = o.enter ?? 'pop';
      if (e === 'pop') { const s = sp(f, fps); sc = interpolate(s, [0, 1], [0.6, 1]); op = Math.min(1, f / 3 + 0.2); }
      else if (e === 'drop') { const k = interpolate(f, [0, 6], [1, 0], {...clamp, easing: ease}); ty = -90 * k; sc = 1 + 0.15 * k; op = 1 - k * 0.7; }
      else if (e === 'slam') { const k = interpolate(f, [0, 5], [1, 0], {...clamp, easing: ease}); sc = 1 + 0.7 * k; rot += 8 * k; op = Math.min(1, f / 2 + 0.3); }
      else if (e === 'slideRight') { const k = interpolate(f, [0, 8], [1, 0], {...clamp, easing: ease}); tx = 700 * k; }
      else if (e === 'slideLeft') { const k = interpolate(f, [0, 8], [1, 0], {...clamp, easing: ease}); tx = -700 * k; }
      if (o.dropAt !== undefined && t >= o.dropAt) { const s = sp((t - o.dropAt) * fps, fps, 9, 200); ty += 46 * s; rot += 9 * s; }
      return (
        <div style={{position: 'absolute', left: o.x, top: o.y, width: o.w, opacity: op, transform: `translate(${tx}px, ${ty}px) scale(${sc}) rotate(${rot}deg)`, transformOrigin: 'center'}}>
          <Img src={staticFile(o.src)} style={{width: o.w, display: 'block', borderRadius: o.frame ? 10 : 0, border: o.frame ? '8px solid #FFFFFF' : undefined, boxSizing: 'border-box',
            filter: o.shadow || o.frame ? 'drop-shadow(0 14px 22px rgba(0,0,0,.55))' : 'drop-shadow(0 8px 14px rgba(0,0,0,.45))'}} />
        </div>
      );
    }
    case 'danmaku': {
      const x = 1760 - f * 10;
      return <div style={{position: 'absolute', left: x, top: o.y, whiteSpace: 'nowrap', fontFamily: F, fontWeight: 700, fontSize: 44, color: '#fff', textShadow: '0 0 4px #000, 2px 2px 0 #000, -2px 2px 0 #000, 2px -2px 0 #000, -2px -2px 0 #000'}}>{o.text}</div>;
    }
    case 'cap': {
      const s = sp(f, fps, 9, 300);
      const sc = interpolate(s, [0, 1], [1.9, 1]);
      const col = colorOf(o.color);
      return (
        <div style={{position: 'absolute', left: o.x, top: o.y, transform: `translate(-50%, -50%) scale(${sc}) rotate(${o.rot ?? 0}deg)`, opacity: Math.min(1, f / 2 + 0.4)}}>
          <div style={{whiteSpace: 'nowrap', fontFamily: F, fontWeight: 700, fontSize: o.size ?? 60, lineHeight: 1.18, padding: '10px 34px 14px', borderRadius: 999, background: col, color: o.color === 'yellow' ? INK : '#FFFFFF',
            boxShadow: '0 10px 24px rgba(0,0,0,.45), inset 0 -5px 0 rgba(0,0,0,.18)', border: '4px solid rgba(255,255,255,.92)'}}>{o.text}</div>
        </div>
      );
    }
    case 'tag': {
      const k = o.popin ? interpolate(sp(f, fps, 10, 280), [0, 1], [1.6, 1]) : interpolate(f, [0, 6], [0, 1], {...clamp, easing: ease});
      const col = colorOf(o.color);
      return (
        <div style={{position: 'absolute', left: o.x, top: o.y, transformOrigin: 'left center', transform: o.popin ? `scale(${k})` : `translateX(${(1 - k) * -40}px)`, opacity: o.popin ? 1 : k,
          display: 'flex', alignItems: 'center', gap: 12, padding: '8px 22px 10px 16px', borderRadius: 10, background: 'rgba(12,12,14,.78)', borderLeft: `8px solid ${col}`,
          fontFamily: F, fontWeight: 700, fontSize: 36, color: '#FFFFFF', whiteSpace: 'nowrap'}}>
          <span style={{width: 16, height: 16, borderRadius: 8, background: col, display: 'inline-block'}} />
          {o.text}
        </div>
      );
    }
    case 'chip': {
      const k = interpolate(f, [0, 6], [0, 1], {...clamp, easing: ease});
      return (
        <div style={{position: 'absolute', left: o.x, top: o.y, opacity: k, transform: `translateY(${(1 - k) * 16}px)`, padding: '6px 16px 8px', borderRadius: 8,
          background: o.light ? 'rgba(255,255,255,.94)' : 'rgba(12,12,14,.78)', color: o.light ? INK : '#FFFFFF', border: o.light ? `3px solid ${GREEN}` : '2px solid rgba(255,255,255,.35)',
          fontFamily: F, fontWeight: 700, fontSize: o.light ? 34 : 28, whiteSpace: 'nowrap'}}>{o.text}</div>
      );
    }
    case 'stamp': {
      const k = o.still ? 0 : interpolate(f, [0, 4], [1, 0], {...clamp, easing: Easing.in(Easing.quad)});
      const sc = 1 + 1.6 * k;
      const size = o.size ?? 140;
      return (
        <div style={{position: 'absolute', left: o.x, top: o.y, transform: `translate(-50%, -50%) rotate(${o.rot ?? -10}deg) scale(${sc})`, opacity: o.still ? 0.92 : interpolate(f, [0, 2], [0.2, 1], clamp)}}>
          <div style={{whiteSpace: 'nowrap', fontFamily: F, fontWeight: 700, fontSize: size, lineHeight: 1, color: RED, padding: `${size * 0.14}px ${size * 0.28}px ${size * 0.2}px`,
            border: `${Math.round(size * 0.075)}px solid ${RED}`, borderRadius: size * 0.16, background: 'rgba(255,255,255,.88)', letterSpacing: size * 0.04,
            boxShadow: `0 0 0 ${Math.round(size * 0.035)}px rgba(255,255,255,.88), 0 18px 40px rgba(0,0,0,.5)`}}>{o.text}</div>
        </div>
      );
    }
    case 'split': {
      const k = interpolate(f, [0, 5], [0, 1], {...clamp, easing: ease});
      return <div style={{position: 'absolute', left: 954, top: 0, width: 12, height: 896, background: '#FFFFFF', transform: `scaleY(${k})`, transformOrigin: 'top', boxShadow: '0 0 18px rgba(0,0,0,.7)'}} />;
    }
    case 'quote': {
      const s = sp(f, fps, 12, 260);
      const acc = o.accent === 'gray' ? '#8A8A8A' : o.accent === 'red' ? RED : GREEN;
      return (
        <div style={{position: 'absolute', left: o.x, top: o.y, width: o.w ?? 620, transform: `scale(${interpolate(s, [0, 1], [0.7, 1])})`, transformOrigin: 'left center', opacity: Math.min(1, f / 3 + 0.3),
          background: PAPER, borderRadius: 18, borderLeft: `16px solid ${acc}`, padding: '22px 34px 26px', boxShadow: '0 14px 30px rgba(0,0,0,.5)', fontFamily: F, fontWeight: 700}}>
          {o.title ? <div style={{fontSize: 30, color: '#555', marginBottom: 8}}>{o.title}</div> : null}
          <div style={{fontSize: o.big ? 72 : 60, color: o.accent === 'red' ? RED : INK, whiteSpace: 'nowrap'}}>{o.text}</div>
        </div>
      );
    }
    case 'cursor': {
      const end = o.t1 ?? c.shotEnd;
      if (t >= end) return null;
      let [x, y] = lerpPath(o.path, t);
      let ring: React.ReactNode = null, press = 0, ripple: React.ReactNode = null;
      if (o.click !== undefined && t >= o.click - 0.05 && t < o.click + 0.25) {
        press = t < o.click + 0.08 ? 1 : 0;
        const rf = (t - o.click) * fps;
        if (rf >= 0) ripple = <div style={{position: 'absolute', left: x - 30 - rf * 4, top: y - 30 - rf * 4, width: 60 + rf * 8, height: 60 + rf * 8, borderRadius: '50%', border: `5px solid ${YELLOW}`, opacity: 1 - rf / 8}} />;
      }
      const cc = o.circle;
      if (cc && t >= cc.t) {
        const k = Math.min(1, (t - cc.t) / cc.dur);
        const a = ease(k) * Math.PI * 2 * 1.06;
        if (k < 1) { x = cc.cx + cc.rx * Math.cos(a - 0.2); y = cc.cy + cc.ry * Math.sin(a - 0.2); }
        else { x = cc.cx + cc.rx * Math.cos(-0.2) + 24; y = cc.cy + cc.ry * Math.sin(-0.2) + 30; }
        if (t < (cc.t1 ?? end)) ring = <Ellipse cx={cc.cx} cy={cc.cy} rx={cc.rx} ry={cc.ry} rot={-3} stroke={RED} w={8} draw={ease(k) * 1.0} />;
      }
      return <>{ring}{ripple}<Cursor x={x} y={y} press={press} /></>;
    }
    case 'penring':
      return <Ellipse cx={o.cx} cy={o.cy} rx={o.rx} ry={o.ry} rot={-3} stroke={RED} w={8} />;
    case 'hl': {
      const k = interpolate(f, [0, 5], [0, 1], {...clamp, easing: ease});
      return <div style={{position: 'absolute', left: o.x, top: o.y, width: o.w * k, height: o.h, background: 'rgba(255,216,74,.55)', mixBlendMode: 'multiply', borderRadius: 4}} />;
    }
    case 'underline': {
      const k = interpolate(t, [o.t, o.t1 ?? o.t + 0.3], [0, 1], {...clamp, easing: ease});
      return <div style={{position: 'absolute', left: o.x, top: o.y, width: o.w * k, height: 9, borderRadius: 5, background: colorOf(o.color), boxShadow: '0 2px 6px rgba(0,0,0,.4)'}} />;
    }
    case 'dash': {
      if (o.t1 !== undefined && t >= o.t1) return null;
      const k = o.noDraw ? 1 : interpolate(f, [0, 7], [0, 1], {...clamp, easing: ease});
      return <Ellipse cx={o.cx} cy={o.cy} rx={o.rx * (0.85 + 0.15 * k)} ry={o.ry * (0.85 + 0.15 * k)} rot={o.rot ?? 0} stroke={colorOf(o.color)} w={7} dash="22 14" offset={-f * 1.6} draw={k} />;
    }
    case 'ring': {
      const k = interpolate(f, [0, 6], [0, 1], {...clamp, easing: ease});
      const s = sp(f - 2, fps, 9, 300);
      const bx = o.cx + o.r * 0.75, by = o.cy - o.r * 0.95;
      return (
        <>
          <Ellipse cx={o.cx} cy={o.cy} rx={o.r} ry={o.r} stroke={RED} w={8} draw={k} />
          <div style={{position: 'absolute', left: bx - 30, top: by - 30, width: 60, height: 60, borderRadius: 30, background: RED, color: '#fff', fontFamily: F, fontWeight: 700, fontSize: 40,
            display: 'flex', alignItems: 'center', justifyContent: 'center', transform: `scale(${f < 2 ? 0 : s})`, border: '3px solid #fff'}}>{o.label}</div>
        </>
      );
    }
    case 'leader': {
      const k = interpolate(f, [0, 6], [0, 1], {...clamp, easing: ease});
      return (
        <svg style={{position: 'absolute', left: 0, top: 0, overflow: 'visible'}} width={1920} height={1080}>
          <circle cx={o.x0} cy={o.y0} r={o.r0} fill="none" stroke="#fff" strokeWidth={5} />
          <line x1={o.x0 + o.r0} y1={o.y0} x2={o.x0 + o.r0 + (o.x1 - o.x0 - o.r0) * k} y2={o.y0 + (o.y1 - o.y0) * k} stroke="rgba(255,255,255,.9)" strokeWidth={4} />
        </svg>
      );
    }
    case 'wavy': {
      const k = interpolate(f, [0, 6], [0, 1], {...clamp, easing: ease});
      let d = `M0 10`;
      for (let i = 1; i <= 12; i++) d += ` Q ${(i - 0.5) * (o.w / 12)} ${i % 2 ? -4 : 24} ${i * (o.w / 12)} 10`;
      return (
        <svg style={{position: 'absolute', left: o.x, top: o.y, overflow: 'visible', transform: `rotate(${o.rot ?? 0}deg)`, transformOrigin: 'center'}} width={o.w} height={30}>
          <path d={d} fill="none" stroke={RED} strokeWidth={8} strokeLinecap="round" strokeDasharray={`${o.w * 1.6 * k} ${o.w * 2}`} />
        </svg>
      );
    }
    case 'dashrect': {
      const k = interpolate(f, [0, 6], [0, 1], {...clamp, easing: ease});
      return (
        <div style={{position: 'absolute', left: o.x, top: o.y, width: o.w, height: o.h, border: `6px dashed ${colorOf(o.color)}`, borderRadius: 16, opacity: k, transform: `scale(${1.08 - 0.08 * k})`}}>
          {o.label ? <div style={{position: 'absolute', left: 10, top: -54, padding: '4px 14px', borderRadius: 8, background: colorOf(o.color), color: INK, fontFamily: F, fontWeight: 700, fontSize: 32, whiteSpace: 'nowrap'}}>{o.label}</div> : null}
        </div>
      );
    }
    case 'waves': {
      const k = interpolate(f, [0, 6], [0, 1], clamp);
      return (
        <svg style={{position: 'absolute', left: o.x - 200, top: o.y - 20, overflow: 'visible', opacity: k}} width={400} height={120}>
          {[0, 1, 2].map((i) => {
            let d = '';
            for (let x = 0; x <= 160; x += 8) d += `${x === 0 ? 'M' : 'L'} ${x + i * 30} ${i * 34 + 10 * Math.sin(x / 18 + f / 3 + i)}`;
            return <path key={i} d={d} fill="none" stroke="#fff" strokeWidth={7} strokeLinecap="round" style={{filter: 'drop-shadow(0 0 3px rgba(0,0,0,.8))'}} />;
          })}
        </svg>
      );
    }
    case 'sparkle':
      return (
        <>
          {o.pts.map(([x, y, s]: number[], i: number) => {
            const ff = f - i * 3;
            if (ff < 0) return null;
            const sc = interpolate(sp(ff, fps, 8, 260), [0, 1], [0, 1]) * (1 + 0.12 * Math.sin(ff / 3));
            return <Img key={i} src={staticFile('v3/img/sparkle.png')} style={{position: 'absolute', left: x - s / 2, top: y - s / 2, width: s, height: s, transform: `scale(${sc}) rotate(${ff * 3}deg)`}} />;
          })}
        </>
      );
    case 'bubbles':
      return (
        <>
          {[0, 1, 2, 3, 4, 5].map((i) => {
            const ff = f - i * 4;
            if (ff < 0) return null;
            const r = 14 + (i % 3) * 8;
            return <div key={i} style={{position: 'absolute', left: o.x + ((i * 53) % 140) - 70 + 10 * Math.sin(ff / 5 + i), top: o.y - ff * 6, width: r * 2, height: r * 2, borderRadius: r, border: '4px solid #8FD3FF', opacity: Math.max(0, 1 - ff / 40)}} />;
          })}
        </>
      );
    case 'cross': {
      const k1 = interpolate(f, [0, 4], [0, 1], clamp), k2 = interpolate(f, [3, 7], [0, 1], clamp);
      const h = o.size / 2;
      return (
        <svg style={{position: 'absolute', left: o.x - h, top: o.y - h, overflow: 'visible', filter: 'drop-shadow(0 4px 8px rgba(0,0,0,.6))'}} width={o.size} height={o.size}>
          <line x1={0} y1={0} x2={o.size * k1} y2={o.size * k1} stroke={RED} strokeWidth={30} strokeLinecap="round" />
          <line x1={o.size} y1={0} x2={o.size - o.size * k2} y2={o.size * k2} stroke={RED} strokeWidth={30} strokeLinecap="round" />
        </svg>
      );
    }
    case 'qmark': {
      if (o.t1 !== undefined && t >= o.t1) return null;
      const s = sp(f, fps, 7, 220);
      return (
        <div style={{position: 'absolute', left: o.x, top: o.y, transform: `translate(-50%, -50%) scale(${interpolate(s, [0, 1], [0.2, 1])}) rotate(${8 * Math.sin(f / 4)}deg)`,
          fontFamily: F, fontWeight: 700, fontSize: o.size ?? 200, lineHeight: 1, color: YELLOW, WebkitTextStroke: '10px #111', paintOrder: 'stroke fill', textShadow: '0 12px 24px rgba(0,0,0,.5)'}}>？</div>
      );
    }
    case 'text': {
      const s = sp(f, fps, 12, 260);
      return (
        <div style={{position: 'absolute', left: o.x, top: o.y, transform: `translate(-50%, -50%) scale(${interpolate(s, [0, 1], [0.7, 1])})`, opacity: Math.min(1, f / 3 + 0.2), textAlign: 'center', fontFamily: F, fontWeight: 700}}>
          <div style={{fontSize: o.size, color: colorOf(o.color), whiteSpace: 'nowrap', WebkitTextStroke: o.box ? undefined : '8px #111', paintOrder: 'stroke fill',
            ...(o.box ? {background: 'rgba(12,12,14,.82)', padding: '6px 40px 16px', borderRadius: 24, border: `5px solid ${YELLOW}`} : {})}}>{o.text}</div>
          {o.sub ? <div style={{fontSize: 24, color: '#EEE', marginTop: 4, textShadow: '0 0 4px #000, 0 0 2px #000'}}>{o.sub}</div> : null}
        </div>
      );
    }
    case 'counter': {
      const k = interpolate(t, [o.t, o.t2], [0, 1], {...clamp, easing: Easing.out(Easing.cubic)});
      const s = sp(f, fps, 9, 300);
      return (
        <div style={{position: 'absolute', left: o.x, top: o.y, transform: `translate(-50%, -50%) scale(${interpolate(s, [0, 1], [1.8, 1])})`}}>
          <div style={{whiteSpace: 'nowrap', fontFamily: F, fontWeight: 700, fontSize: o.size, padding: '8px 40px 14px', borderRadius: 999, background: RED, color: '#fff', border: '4px solid rgba(255,255,255,.92)', boxShadow: '0 10px 24px rgba(0,0,0,.45)'}}>
            {o.prefix}<span style={{display: 'inline-block', minWidth: o.size * 2.4, textAlign: 'right'}}>{(o.to * k).toFixed(1)}</span>{o.suffix}
          </div>
        </div>
      );
    }
    case 'dim':
      return <div style={{position: 'absolute', inset: 0, background: `rgba(0,0,0,${o.a})`}} />;
    case 'scroll': {
      const off = (t - o.t) * o.speed;
      let y = o.y0 - off;
      return (
        <div style={{position: 'absolute', left: o.x, top: 140, width: o.w, height: 740, overflow: 'hidden'}}>
          {o.items.map((src: string, i: number) => (
            <Img key={i} src={staticFile(src)} style={{position: 'absolute', left: 0, top: o.y0 - 140 - off + i * 290, width: o.w, filter: 'drop-shadow(0 8px 14px rgba(0,0,0,.5))'}} />
          ))}
        </div>
      );
    }
    case 'move': {
      let x: number;
      if (t < o.tmid) x = interpolate(t, [o.t, o.tmid], [o.x0, o.x1], {...clamp, easing: ease});
      else x = interpolate(t, [o.tmid + 0.15, o.t1], [o.x1, o.x2], {...clamp, easing: Easing.in(Easing.cubic)});
      const bob = Math.sin(f / 2.2) * 4;
      return <Img src={staticFile(o.src)} style={{position: 'absolute', left: x, top: o.y + bob, width: o.w, filter: 'drop-shadow(0 16px 20px rgba(0,0,0,.5))'}} />;
    }
    case 'search': {
      const n1 = Math.round(interpolate(t, [o.type0, o.type1], [0, o.text.length], clamp));
      const n2 = Math.round(interpolate(t, [o.add0, o.add1], [0, o.add.length], clamp));
      const caret = Math.floor(f / 8) % 2 === 0;
      return (
        <div style={{position: 'absolute', left: o.x, top: o.y, width: o.w, height: 120, borderRadius: 60, background: '#fff', boxShadow: '0 16px 30px rgba(0,0,0,.5)', display: 'flex', alignItems: 'center', padding: '0 40px', boxSizing: 'border-box', fontFamily: F, fontWeight: 700, fontSize: 54, color: INK, whiteSpace: 'nowrap', overflow: 'hidden'}}>
          <svg width={56} height={56} style={{marginRight: 22, flex: 'none'}}><circle cx={23} cy={23} r={16} fill="none" stroke="#888" strokeWidth={6} /><line x1={35} y1={35} x2={50} y2={50} stroke="#888" strokeWidth={7} strokeLinecap="round" /></svg>
          <span>{o.text.slice(0, n1)}</span>
          {n2 > 0 ? <span style={{background: YELLOW, borderRadius: 8, padding: '0 6px', marginLeft: 6}}>{o.add.slice(0, n2)}</span> : null}
          {caret ? <span style={{width: 4, height: 60, background: INK, marginLeft: 4, display: 'inline-block'}} /> : null}
        </div>
      );
    }
    default:
      return null;
  }
};
