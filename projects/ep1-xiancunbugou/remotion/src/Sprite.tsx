// 素材接口：优先加载 public/sprites/<name>.png（codex 生成），缺图时用代码占位
import React from 'react';
import {getStaticFiles, Img, staticFile} from 'remotion';
import {useTheme} from './theme/ThemeProvider';
import {GpuSprite, RackSprite, WarehouseSprite, BenchSprite, BoltSprite, ClockSprite, KidSprite} from './sprites';

/** 约定的文件名 → 占位组件。codex 按这些名字出 PNG（透明底，像素原尺寸或整数倍放大均可） */
export const SPRITES = {
  gpu: () => <GpuSprite px={8} />,
  rack: () => <RackSprite px={6} />,
  warehouse: () => <WarehouseSprite px={10} />,
  bench: () => <BenchSprite px={10} />,
  bolt: () => <BoltSprite px={6} />,
  clock: () => <ClockSprite px={5} />,
  kid: () => <KidSprite px={8} />,
  kid_wave: () => <KidSprite px={8} wave />,
  bg_dark_grid: () => null,
  bg_paper: () => null,
} as const;
export type SpriteName = keyof typeof SPRITES | string;

/** 约定名 → codex 实际文件名（public/sprites/FILELIST.txt） */
export const ALIAS: Record<string, string> = {
  gpu: 'gpu_card_v2', rack: 'server_rack', gpu_row: 'gpu_row', warehouse: 'warehouse_hbm_v2', bench: 'workbench_sram',
  matrix: 'matrix_score_grid', token_q: 'token_q_orange', token_k: 'token_k_green', token_v: 'token_v_gold',
  kid: 'hero_stand', kid_point: 'hero_point_v2', kid_think: 'hero_think_v2', kid_wave: 'hero_point_v2', qblock: 'question_block',
  bg_dark_grid: 'bg_compute_grid_1920x1080',
};
const file = (name: string) => ALIAS[name] ?? name;
export const hasSprite = (name: string) => getStaticFiles().some((f) => f.name === `sprites/${file(name)}.png`);

/**
 * 道具调色。
 * PNG 是烘焙好的像素画，颜色改不了，所以其它皮肤靠 CSS filter 把它拉到同一调性：
 *   霓虹：降饱和 + 提高亮度 + 青色相旋转，让它像自己发光的全息板
 *   纸本：去色 + 加深，让它像印在纸上的单色版画
 * 像素皮肤返回空串，保证逐像素和改造前一致。
 */
const tintFilter = (skin: string) => {
  if (skin === 'neon') return 'saturate(0.55) hue-rotate(-18deg) brightness(1.18) contrast(1.06)';
  if (skin === 'paper') return 'saturate(0.18) contrast(1.35) brightness(0.82)';
  return '';
};

export const Sprite: React.FC<{name: SpriteName; w: number; style?: React.CSSProperties; outline?: number; clipTop?: number; flip?: boolean; mute?: boolean}> = ({name, w, style, outline, clipTop, flip, mute}) => {
  const {theme, pixel} = useTheme();
  const ink = 'var(--m-ink)';
  const shadowCol = 'rgba(20,18,26,.22)';
  const OUTLINE = (n: number) => [`${n}px 0 0 ${ink}`, `-${n}px 0 0 ${ink}`, `0 ${n}px 0 ${ink}`, `0 -${n}px 0 ${ink}`].map((d) => `drop-shadow(${d})`).join(' ') + ` drop-shadow(6px 6px 0 ${shadowCol})`;
  if (hasSprite(name)) {
    const img = <Img src={staticFile(`sprites/${file(name)}.png`)} style={{width: w, height: 'auto', imageRendering: pixel ? 'pixelated' : 'auto', display: 'block', transform: flip ? 'scaleX(-1)' : undefined, marginTop: clipTop ? `-${clipTop * 100}%` : undefined}} />;
    const base = outline ? OUTLINE(outline) : `drop-shadow(6px 6px 0 ${shadowCol})`;
    const muteFx = mute ? 'saturate(0.12) sepia(0.28) brightness(1.04) ' : '';
    const tint = tintFilter(theme.id);
    return <div style={{width: w, overflow: clipTop ? 'hidden' : undefined, filter: `${muteFx}${tint} ${base}`.trim(), ...style}}>{img}</div>;
  }
  const Ph = (SPRITES as any)[name];
  return (
    <div style={{width: w, display: 'flex', justifyContent: 'center', ...style}}>
      {Ph ? <div style={{transformOrigin: 'top left'}}>{Ph()}</div>
          : <div style={{width: w, height: w * 0.6, border: '4px dashed var(--m-orange)', fontFamily: 'monospace', fontSize: 20, color: 'var(--m-orange)', display: 'flex', alignItems: 'center', justifyContent: 'center'}}>{name}.png</div>}
    </div>
  );
};

/**
 * 背景：像素皮肤走烘焙的 PNG（保证 diff = 0），其它皮肤走主题背景，
 * 否则深色皮肤上会突然出现一块米白像素网格。
 */
export const SpriteBg: React.FC<{name: 'bg_dark_grid' | 'bg_paper'; fallback: React.ReactNode}> = ({name, fallback}) => {
  const {pixel} = useTheme();
  if (!pixel) return <>{fallback}</>;
  return hasSprite(name)
    ? <Img src={staticFile(`sprites/${file(name)}.png`)} style={{position: 'absolute', inset: 0, width: '100%', height: '100%', objectFit: 'cover', imageRendering: 'pixelated'}} />
    : <>{fallback}</>;
};
