// 自制像素道具库：所有道具都是 16–32 格的像素网格，按格着色（带描边/高光/暗部），不是几何大块
import React from 'react';
import {} from 'remotion';
import {useDesignFrame} from './timeline/fps';
import {m} from './theme/mat';

type Fn = (x: number, y: number) => string | null;
export const PixGrid: React.FC<{w: number; h: number; px: number; fn: Fn; style?: React.CSSProperties}> = ({w, h, px, fn, style}) => {
  const rects: React.ReactNode[] = [];
  for (let y = 0; y < h; y++) {
    // 合并同色横向连续格，减少节点
    let x = 0;
    while (x < w) {
      const c = fn(x, y);
      let x2 = x + 1;
      while (x2 < w && fn(x2, y) === c) x2++;
      if (c) rects.push(<rect key={`${x}-${y}`} x={x * px} y={y * px} width={(x2 - x) * px + 0.3} height={px + 0.3} fill={c} />);
      x = x2;
    }
  }
  return <svg width={w * px} height={h * px} shapeRendering="crispEdges" style={{display: 'block', overflow: 'visible', filter: 'drop-shadow(5px 5px 0 rgba(20,18,26,.22))', ...style}}>{rects}</svg>;
};

/** 字符画转像素：每个字符查调色板，'.' 透明 */
export const fromMap = (rows: string[], pal: Record<string, string>): Fn => (x, y) => {
  const ch = rows[y]?.[x];
  return !ch || ch === '.' ? null : pal[ch] ?? null;
};

const K = m('ink');

/** 显卡 32×14：双风扇（叶片随帧旋转）、金手指、指示灯、散热鳍片 */
export const GpuSprite: React.FC<{px?: number; spin?: number; hot?: boolean}> = ({px = 8, spin = 1, hot}) => {
  const f = useDesignFrame();
  const fans = [[9, 6.5], [22, 6.5]];
  const fn: Fn = (x, y) => {
    if (y === 13) return x >= 4 && x <= 27 ? (x % 2 ? m('gold') : m('gold-dark')) : null; // 金手指
    if (x === 0 || x === 31 || y === 0 || y === 12) return K;
    if (y === 1) return m('metal-dark');
    if (x === 1) return m('gpu-edge');
    for (const [cx, cy] of fans) {
      const dx = x - cx, dy = y - cy, r = Math.hypot(dx, dy);
      if (r <= 5.2) {
        if (r > 4.4) return K;
        if (r < 1.3) return hot ? m('orange') : m('grey-light');
        const a = (Math.atan2(dy, dx) + f * 0.25 * spin) % (Math.PI * 2);
        const sector = Math.floor(((a + Math.PI * 4) % (Math.PI * 2)) / (Math.PI / 3));
        return sector % 2 ? m('ink-2') : m('metal-light');
      }
    }
    if (x >= 15 && x <= 16 && y >= 2 && y <= 10) return y % 2 ? m('ink-2') : m('metal'); // 中间鳍片
    if (y === 11) return x > 26 && x < 30 ? (f % 30 < 20 ? m('green') : m('green-dark')) : m('gpu-dark');
    if (y === 2 && x > 25 && x < 30) return m('orange'); // 品牌贴条
    return m('panel');
  };
  return <PixGrid w={32} h={14} px={px} fn={fn} />;
};

/** 机柜 16×32：外框倒角、4 层服务器、通风横纹、闪烁 LED */
export const RackSprite: React.FC<{px?: number; seed?: number}> = ({px = 6, seed = 0}) => {
  const f = useDesignFrame();
  const fn: Fn = (x, y) => {
    if (x === 0 || x === 15 || y === 0 || y === 31) return m('rack-frame');
    if (x === 1 || y === 1) return m('rack-hi');
    if (x === 14 || y === 30) return m('rack-lo');
    const slot = Math.floor((y - 2) / 7), sy = (y - 2) % 7;
    if (sy === 0 || sy === 6 || slot > 3) return m('rack-line');
    if (x === 2 || x === 13) return m('rack-line');
    if (x === 3 || sy === 1 || sy === 5) return m('dark-surface');
    if (sy >= 2 && sy <= 4 && x >= 4 && x <= 8) return sy === 3 ? m('metal') : m('panel'); // 通风纹
    if (sy === 3 && x === 11) return (f + seed * 7 + slot * 11) % 24 < 14 ? m('green') : m('green-dark');
    if (sy === 3 && x === 12) return slot % 2 ? m('orange') : m('dark-surface');
    return m('rack-body');
  };
  return <PixGrid w={16} h={32} px={px} fn={fn} />;
};

/** 仓库 32×24：坡屋顶、砖墙、卷帘门、货架上的数据箱 */
export const WarehouseSprite: React.FC<{px?: number}> = ({px = 10}) => {
  const fn: Fn = (x, y) => {
    if (y < 8) {
      const half = 16 - (y + 1) * 2;
      if (x < half - 1 || x > 31 - half + 1) return null;
      if (x === half - 1 || x === 31 - half + 1 || y === 7) return K;
      return y % 2 ? m('roof') : m('orange');
    }
    if (x === 0 || x === 31 || y === 23) return K;
    if (y === 8) return m('wood');
    if (x >= 9 && x <= 22 && y >= 11) { // 卷帘门开口，露出货架
      if (x === 9 || x === 22 || y === 11) return K;
      if (y === 12) return m('metal-light');
      const bx = (x - 10) % 4, by = (y - 13) % 3;
      if (by === 2) return m('wood');
      if (bx === 3) return m('panel');
      return (x + y) % 3 ? m('gold') : m('orange');
    }
    if ((y - 9) % 3 === 2) return m('brick-light');
    return ((x + Math.floor((y - 9) / 3) * 2) % 6) === 0 ? m('brick-light') : m('wall');
  };
  return <PixGrid w={32} h={24} px={px} fn={fn} />;
};

/** 工作台 24×14：木桌面高光、桌腿、台上的小芯片和扳手 */
export const BenchSprite: React.FC<{px?: number}> = ({px = 10}) => {
  const fn: Fn = (x, y) => {
    if (y <= 4) { // 台上芯片 x 3..8，扳手 x 16..21
      if (x >= 3 && x <= 8 && y >= 1) { if (y === 1 || x === 3 || x === 8) return K; return x % 2 && y === 3 ? m('gold') : m('teal'); }
      if (y >= 2 && y <= 3 && x >= 15 && x <= 21) return x === 15 || x === 21 ? m('metal-dark') : m('slate');
      if (y === 4 && x >= 2 && x <= 9 && x % 2 === 0) return m('gold-dark');
      return null;
    }
    if (y === 5) return K;
    if (y === 6) return x === 0 || x === 23 ? K : m('bench-hi');
    if (y === 7) return x === 0 || x === 23 ? K : m('bench-mid');
    if (y === 8) return K;
    if ((x >= 2 && x <= 4) || (x >= 19 && x <= 21)) return x === 2 || x === 19 ? K : (x === 3 || x === 20 ? m('wood-dark2') : m('bench-dark'));
    if (y === 11 && x > 4 && x < 19) return m('wood-dark2');
    return null;
  };
  return <PixGrid w={24} h={14} px={px} fn={fn} />;
};

/** 闪电图标 8×12（自制栏目图标） */
export const BoltSprite: React.FC<{px?: number}> = ({px = 6}) => (
  <PixGrid w={8} h={12} px={px} fn={fromMap([
    '....kkkk', '...kyyyk', '..kyyyk.', '.kyyyk..', 'kyyyykkk', 'kyyyyyyk', 'kkkkyyyk', '...kyyk.', '..kyyk..', '..kyk...', '.kyk....', '.kk.....',
  ], {k: K, y: m('gold')})} />
);

/** 时钟 10×10 */
export const ClockSprite: React.FC<{px?: number}> = ({px = 5}) => {
  const f = useDesignFrame();
  const a = f * 0.2;
  return <PixGrid w={10} h={10} px={px} fn={(x, y) => {
    const r = Math.hypot(x - 4.5, y - 4.5);
    if (r > 4.9) return null; if (r > 3.9) return K;
    const hx = Math.round(4.5 + Math.cos(a) * 2), hy = Math.round(4.5 + Math.sin(a) * 2);
    if ((x === 4 || x === 5) && y >= 2 && y <= 5) return K;
    if (x === hx && y === hy) return m('orange');
    return m('token-bg');
  }} />;
};

/** 自制角色 16×20：戴耳机和眼镜的卫衣学生，会眨眼 */
export const KidSprite: React.FC<{px?: number; wave?: boolean}> = ({px = 9, wave}) => {
  const f = useDesignFrame();
  const blink = f % 75 < 4;
  const up = wave && Math.floor(f / 8) % 2 === 0;
  const rows = [
    '....kkkkkkkk....', '...khhhhhhhhk...', '..khhhhhhhhhhk..', '.yykhhhhhhhhkyy.',
    '.yyksssssssskyy.', blink ? '.yykgggssgggkyy.' : '.yykgwgssgwgkyy.', '..kssssssssssk..', '..ksssskksssssk.',
    '...kSSSSSSSSk...', '..kkttttttttkk..', '.kttttwwwwttttk.', 'kttttttwwtttttTk',
    up ? 'kskttttttttttsk.' : 'ksktttttttttTksk', 'kssktttyytttTkss', '.kkktttttttTTkk.', '...kTTTTTTTTk...',
    '...kppppppppk...', '...kppk..kppk...', '...kppk..kppk...', '..keeek..keeek..',
  ];
  return <PixGrid w={16} h={20} px={px} fn={fromMap(rows, {k: K, h: m('hair'), y: m('gold'), s: m('face'), S: m('face-shadow'), g: m('ink'), w: m('white'), t: m('teal'), T: m('shirt-dark'), p: m('panel'), e: m('ink')})} />;
};

/** 斜面小格（矩阵/显存单元）：描边 + 左上高光 + 右下暗部 */
export const Cell: React.FC<{c: string; s?: number}> = ({c, s = 40}) => (
  <svg width={s} height={s} shapeRendering="crispEdges" style={{display: 'block'}}>
    <rect width={s} height={s} fill={K} />
    <rect x={4} y={4} width={s - 8} height={s - 8} fill={c} />
    <rect x={4} y={4} width={s - 8} height={4} fill="rgba(255,255,255,.35)" />
    <rect x={4} y={s - 8} width={s - 8} height={4} fill="rgba(0,0,0,.18)" />
  </svg>
);

/** 神经网络：分色层柱 + 节点 + 连线 */
export const NeuralNet: React.FC<{cols?: number[]; w?: number; h?: number}> = ({cols = [4, 6, 6, 6, 4], w = 520, h = 300}) => {
  const tints = [m('tint-1'), m('tint-2'), m('tint-3'), m('tint-4'), m('tint-5'), m('tint-3')];
  const xs = cols.map((_, i) => 30 + i * (w - 60) / (cols.length - 1));
  const pos = cols.map((n, i) => Array.from({length: n}).map((_, k) => [xs[i], 30 + (k + 0.5) * (h - 60) / n]));
  return (
    <svg width={w} height={h} shapeRendering="crispEdges" style={{display: 'block', overflow: 'visible'}}>
      {xs.map((x, i) => <rect key={i} x={x - 18} y={10} width={36} height={h - 20} fill={tints[i % tints.length]} />)}
      {pos.slice(0, -1).map((col, i) => col.map(([x1, y1], a) => pos[i + 1].map(([x2, y2], b) => <line key={`${i}${a}${b}`} x1={x1} y1={y1} x2={x2} y2={y2} stroke="var(--m-net-line)" strokeWidth={1.5} shapeRendering="auto" />)))}
      {pos.flat().map(([x, y], i) => <g key={i}><rect x={x - 11} y={y - 11} width={22} height={22} fill={K} /><rect x={x - 7} y={y - 7} width={14} height={14} fill="var(--m-gold)" /><rect x={x - 7} y={y - 7} width={14} height={3} fill="var(--m-node-hi)" /></g>)}
    </svg>
  );
};

/** 漂浮像素尘：小方块 + 十字星 */
export const Dust: React.FC<{n?: number; dark?: boolean; seed?: number}> = ({n = 14, dark, seed = 1}) => {
  const f = useDesignFrame();
  const r = (i: number) => { const v = Math.sin(i * 12.9898 + seed * 78.233) * 43758.5453; return v - Math.floor(v); };
  const cols = dark ? [m('metal'), m('night'), m('dust-dark')] : [m('dust-1'), m('dust-2'), m('dust-3'), m('dot')];
  return (
    <svg width={1920} height={1080} style={{position: 'absolute', left: 0, top: 0}} shapeRendering="crispEdges">
      {Array.from({length: n}).map((_, i) => {
        // v4：尘埃从「原地 ±6px 微动」改成「缓慢下落 + 侧向漂移 + 循环回卷」。
        // 原来的幅度在 256×144 质检尺度下完全不可见（1px 都不到），
        // 现在每个颗粒每秒走 ~45px，整屏十几颗一起走，是真能看见的「空气在动」。
        const sp = 0.9 + r(i + 70) * 0.6;                       // 各自速度不同
        // 2026-11-04 去掉 ±9px / 0.87s 的横向抖动（那是「晃」不是「飘」），只留极慢的下落
        const x = ((r(i) * 1800 + 60 + f * 0.18 * sp + 1800) % 1800) + 60;
        const y = ((r(i + 50) * 900 + 90 + f * 1.15 * sp + 900) % 900) + 90;
        const c = cols[i % cols.length];
        return i % 3 === 0
          ? <g key={i}><rect x={x} y={y} width={8} height={8} fill={c} /><rect x={x + 10} y={y + 10} width={6} height={6} fill={c} /></g>
          : <rect key={i} x={x} y={y} width={10} height={10} fill={c} />;
      })}
    </svg>
  );
};
