import {BoltSprite, Cell, NeuralNet, Dust} from './sprites';
import {Sprite, SpriteBg} from './Sprite';
import {DarkGridBg} from './kit';
import {MotionPreview, MOTION_SEGS} from './Motion';
import {Cover} from './Cover';
import {ThemeProvider} from './theme/ThemeProvider';
import {Texture} from './kit';
import {SkinId} from './theme/skins';
import {BeatProvider} from './components/BeatSync';
import {Bgm, DEFAULT_BGM, bgmBeatProps} from './Audio';
import {Final, FINAL_TOTAL, FinalUngridded, UNGRIDDED_TOTAL} from './Chapters';
import React from 'react';
import {AbsoluteFill, Composition} from 'remotion';
import {useDesignFrame} from './timeline/fps';
import {Frame, FontFace, Label, P, PaperBg, Pop, StarBg, Sub, FONT, m} from './kit';
import {prog, easeOut, easeOutBack} from './lib/anim';

// K 统一用 token_k_green 的主色
const K_GREEN = m('green');
const SKIN_LIST: SkinId[] = ['pixel', 'neon', 'paper'];
const NAME = '显存不够'; // 账号名（用户 11-04 定）
// K1 v5：中心=信息（标题牌 + 网络图 + 显存98%），显卡/人物/机柜压小且降饱和
const K1: React.FC = () => {
  const f = useDesignFrame();
  return (
  <AbsoluteFill><FontFace /><SpriteBg name="bg_paper" fallback={<PaperBg />} /><Dust n={8} />
    <Pop at={0} x={500} y={100}><div style={{display: 'flex', gap: 24, alignItems: 'center', background: P.plate, padding: '16px 40px', boxShadow: 'var(--t-shadow-8-a20)'}}><BoltSprite px={8} /><span style={{fontFamily: FONT, fontSize: 100, color: P.gold}}>FlashAttention</span></div></Pop>
    <Pop at={6} x={1340} y={110}><Sprite name="qblock" w={128} /></Pop>
    <Pop at={10} x={620} y={300}><NeuralNet cols={[4, 6, 6, 6, 4]} w={680} h={400} /></Pop>
    <Pop at={14} x={440} y={380}><div style={{display: 'flex', flexDirection: 'column', gap: 16}}>{['token_q', 'token_k', 'token_v'].map((n, i) => <div key={i} style={{display: 'flex', alignItems: 'center', gap: 10}}><span style={{fontFamily: FONT, fontSize: 32, color: P.text}}>{'QKV'[i]}</span><Sprite name={n} w={64} /></div>)}</div></Pop>
    <Pop at={20} x={1340} y={380}><div style={{background: P.tokenBg, border: `5px solid ${P.stroke}`, padding: '14px 20px', boxShadow: 'var(--t-shadow-6)'}}>
      <div style={{fontFamily: FONT, fontSize: 32, color: P.text}}>显存</div>
      <div style={{fontFamily: FONT, fontSize: 80, color: P.heart, lineHeight: 1}}>98%</div>
      <div style={{width: 220, height: 22, background: m('panel'), marginTop: 8}}><div style={{width: 216 * Math.min(1, 0.6 + f / 150), height: 22, background: P.heart}} /></div>
    </div></Pop>
    <Pop at={26} x={1360} y={640}><Sprite name="gpu" w={288} mute /></Pop>
    <Pop at={30} x={1700} y={680}><div style={{display: 'flex', gap: 6}}>{[0, 1].map((i) => <Sprite key={i} name="rack" w={54} mute />)}</div></Pop>
    <Pop at={12} x={190} y={660}><Sprite name="kid_think" w={124} /></Pop>
    <Pop at={36} x={110} y={610}><div style={{background: P.bubble, border: `4px solid ${P.stroke}`, padding: '4px 12px', fontFamily: FONT, fontSize: 24}}>又爆显存了？</div></Pop>
    <Frame progress={0.004} count={0} name={NAME} />
    <Sub text="FlashAttention是什么？" keys={['FlashAttention']} />
  </AbsoluteFill>);
};

// K2 v5：加粗搬运通道 + 多个货块流动；人物移到右下角不挡路
const K2: React.FC = () => {
  const f = useDesignFrame();
  const n = (7.6 * prog(f, 30, 30, easeOut)).toFixed(1);
  const L = 820, R = 1250, Y = 600;
  return (
    <AbsoluteFill><FontFace /><SpriteBg name="bg_paper" fallback={<PaperBg />} /><Dust n={8} seed={3} />
      <Pop at={4} x={620} y={100}><div style={{display: 'flex', gap: 16, alignItems: 'center'}}><Label text="算得慢？" size={44} bg="var(--m-slate)" /><span style={{fontFamily: FONT, fontSize: 48, color: P.heart}}>✕</span><Label text="搬得慢！" size={44} bg={P.orange} /></div></Pop>
      <Pop at={0} x={100} y={340}><Sprite name="warehouse" w={720} mute /></Pop>
      <Pop at={6} x={200} y={720}><Label text="HBM 显存 · 40–80GB · 大但远" size={30} /></Pop>
      <Pop at={10} x={1250} y={470}><Sprite name="bench" w={460} clipTop={0.3} mute /></Pop>
      <Pop at={14} x={1270} y={720}><Label text="SRAM 片上 · 192KB · 快但小" size={30} bg={P.teal} /></Pop>
      <svg style={{position: 'absolute', left: L, top: Y}} width={R - L} height={40} shapeRendering="crispEdges">
        <rect x={0} y={4} width={R - L} height={32} fill="var(--m-rail)" /><rect x={0} y={0} width={R - L} height={4} fill={P.stroke} /><rect x={0} y={36} width={R - L} height={4} fill={P.stroke} />
        {Array.from({length: 14}).map((_, i) => <rect key={i} x={((i * 34 + f * 4) % (R - L))} y={18} width={16} height={4} fill="var(--m-wood-dark)" />)}
      </svg>
      {Array.from({length: 5}).map((_, i) => { const t = ((f / 70 + i / 5) % 1); const name = ['token_q', 'token_k', 'token_v'][i % 3]; return <div key={i} style={{position: 'absolute', left: L + t * (R - L - 52), top: Y - 44}}><Sprite name={name} w={52} /></div>; })}
      <Pop at={18} x={940} y={660}><span style={{fontFamily: FONT, fontSize: 30, color: P.orange}}>来回搬 N 趟</span></Pop>
      <Pop at={24} x={1560} y={140}><div style={{background: P.tokenBg, border: `4px solid ${P.stroke}`, padding: '8px 16px', boxShadow: 'var(--t-shadow-6)'}}>
        <div style={{fontFamily: FONT, fontSize: 20, color: m('muted')}}>注意力 · GPT-2</div>
        <div style={{fontFamily: FONT, fontSize: 64, color: P.heart, lineHeight: 1}}>{n}×</div>
        <div style={{fontFamily: FONT, fontSize: 16, color: m('muted')}}>arXiv:2205.14135</div>
      </div></Pop>
      <Pop at={30} x={1480} y={740}><Sprite name="kid_point" w={196} flip /></Pop>
      <Frame progress={0.03} count={0} name={NAME} />
      <Sub text="很多时候不是算得慢，是搬得慢" keys={['算得慢', '搬得慢']} />
    </AbsoluteFill>
  );
};

// K3 章节卡 STAGE 4（按对标 4:04.8 校正：星座进度线、下方标题框、橙色 STAGE、白色大字、字幕常驻）
const K3: React.FC = () => {
  const f = useDesignFrame();
  const p = prog(f, 0, 12, easeOutBack);
  const stars = [[200, 600], [380, 470], [560, 520], [760, 380], [960, 300], [1180, 330]];
  const lit = 4; // 第 4 章：前 4 颗点亮
  return (
    <AbsoluteFill><FontFace /><StarBg />
      <div style={{position: 'absolute', left: 0, right: 0, top: 760, height: 320, background: 'rgba(40,44,80,.55)'}} />
      <svg style={{position: 'absolute', left: 0, top: 0}} width={1920} height={1080} shapeRendering="crispEdges">
        {stars.slice(0, lit).map(([x, y], i) => i < lit - 1 ? Array.from({length: 12}).map((_, k) => { const [x2, y2] = stars[i + 1]; return <rect key={`${i}-${k}`} x={x + (x2 - x) * k / 12} y={y + (y2 - y) * k / 12} width={6} height={6} fill={P.gold} />; }) : null)}
        {stars.map(([x, y], i) => <g key={i}><rect x={x - 12} y={y - 4} width={24} height={8} fill={i < lit ? P.gold : m('night')} /><rect x={x - 4} y={y - 12} width={8} height={24} fill={i < lit ? P.gold : m('night')} /></g>)}
        <circle cx={stars[lit - 1][0]} cy={stars[lit - 1][1]} r={34} fill={P.gold} opacity={0.18} />
      </svg>
      <div style={{position: 'absolute', left: 0, right: 0, top: 640, textAlign: 'center', opacity: p}}>
        <div style={{display: 'inline-block', padding: '14px 70px 18px', border: `4px solid ${P.gold}`, background: 'rgba(30,27,37,.92)', fontFamily: FONT, transform: `scale(${0.8 + 0.2 * p})`}}>
          <div style={{fontSize: 40, color: P.orange}}>STAGE 4</div>
          <div style={{fontSize: 104, color: P.white, lineHeight: 1.05}}>分块</div>
        </div>
      </div>
      <Frame progress={0.46} count={3} name={NAME} dark />
      <Sub text="分块是什么？" keys={['分块']} />
    </AbsoluteFill>
  );
};

// K4 v5：分时出场，同一时刻 2–3 个主元素
// 时刻A（0–70帧）：HBM 显存 + 虚线 N×N 表；时刻B（70帧起）：SRAM 大格 + 三步算子 + 「分块」
const Win: React.FC<{from: number; to?: number; children: React.ReactNode}> = ({from, to = 1e9, children}) => {
  const f = useDesignFrame();
  if (f < from || f >= to) return null;
  return <>{children}</>;
};
const K4: React.FC = () => {
  const f = useDesignFrame();
  const fly = prog(f, 72, 18, easeOut);
  const hbm = Array.from({length: 24}).map((_, i) => (i * 7) % 3 === 0 ? m('hbm-dark') : i === 2 ? m('hbm-light') : m('cream-dark'));
  const step = Math.floor((f - 100) / 10);
  return (
    <AbsoluteFill><FontFace /><SpriteBg name="bg_dark_grid" fallback={<DarkGridBg />} />
      <Pop at={0} x={150} y={140}><span style={{fontFamily: FONT, fontSize: 60, color: m('dark-text')}}>GPU</span></Pop>
      <Win from={0} to={70}>
        <Pop at={2} x={180} y={260}><div style={{display: 'grid', gridTemplateColumns: 'repeat(6, 80px)', gap: 12}}>{hbm.map((c, i) => <Cell key={i} c={i < 3 ? [P.orange, K_GREEN, P.gold][i] : c} s={80} />)}</div></Pop>
        <Pop at={8} x={300} y={650}><Label text="HBM 显存 · 放 Q K V" size={40} /></Pop>
        <Pop at={20} x={1050} y={240}><div style={{opacity: 0.45, filter: 'grayscale(1)'}}><Sprite name="matrix" w={420} /></div><div style={{position: 'absolute', inset: -10, border: '6px dashed var(--m-grey-light)'}} /></Pop>
        <Pop at={26} x={1060} y={700}><Label text="N×N 打分表：不落显存" size={36} bg="var(--m-panel)" /></Pop>
      </Win>
      <Win from={70}>
        <Pop at={70} x={560} y={220}><div style={{width: 800, height: 520, background: m('dark-surface'), border: `6px solid ${P.stroke}`, padding: 30, boxSizing: 'border-box', boxShadow: 'var(--t-shadow-deep-10)'}}>
          <div style={{fontFamily: FONT, fontSize: 36, color: P.gold}}>SRAM 片上 · 每单元 192KB</div>
          <div style={{display: 'grid', gridTemplateColumns: 'repeat(4, 140px)', gap: 24, marginTop: 30}}>{Array.from({length: 8}).map((_, i) => <Cell key={i} c={i < 3 && f > 90 ? [P.orange, K_GREEN, P.gold][i] : m('metal')} s={140} />)}</div>
        </div></Pop>
        <div style={{position: 'absolute', left: 300 + fly * 320, top: 520 - fly * 180, display: 'flex', gap: 10, opacity: f > 90 ? 0 : 1}}>{['token_q', 'token_k', 'token_v'].map((n) => <Sprite key={n} name={n} w={72} />)}</div>
        <Pop at={100} x={600} y={770}><div style={{display: 'flex', gap: 14, alignItems: 'center'}}>{['打分', 'softmax', '×V'].map((t, i) => <div key={i} style={{fontFamily: FONT, fontSize: 34, color: P.white, background: i <= step ? P.teal : m('panel'), padding: '8px 18px', border: `3px solid ${P.stroke}`}}>{t}</div>)}<div style={{fontFamily: FONT, fontSize: 34, color: P.gold}}>→ 1 个算子</div></div></Pop>
        <Pop at={130} x={1420} y={260}><Label text="分块" size={72} bg={P.plate} color={P.gold} /></Pop>
      </Win>
      <Frame progress={0.49} count={4} name={NAME} dark />
      <Sub text={f < 70 ? '一次只从显存拿一小块Q和一小块K、V' : '在SRAM里把打分、softmax、乘V一口气做完'} keys={f < 70 ? ['一小块'] : ['SRAM', '一口气做完']} />
    </AbsoluteFill>
  );
};

/**
 * 皮肤包装：ThemeProvider（颜色/字体/质感/动效） + BeatProvider（拍点） + BGM
 * 三者都在这一层注入，所以分镜代码完全不知道皮肤和 BGM 的存在。
 */
const makeEpisodeRaw = (skin: SkinId): React.FC => {
  const C: React.FC = () => (
    <ThemeProvider skin={skin}>
      <BeatProvider {...bgmBeatProps(DEFAULT_BGM)}>
        <FinalUngridded />
        <Texture />
      </BeatProvider>
    </ThemeProvider>
  );
  C.displayName = `Raw(${skin})`;
  return C;
};

const makeEpisode = (skin: SkinId): React.FC => {
  const C: React.FC = () => (
    <ThemeProvider skin={skin}>
      <BeatProvider {...bgmBeatProps(DEFAULT_BGM)}>
        <Final />
        <Texture />
        <Bgm />
      </BeatProvider>
    </ThemeProvider>
  );
  C.displayName = `Episode(${skin})`;
  return C;
};

const EpisodeNoBgm: React.FC = () => (
  <ThemeProvider skin="pixel"><BeatProvider {...bgmBeatProps(DEFAULT_BGM)}><Final /><Texture /></BeatProvider></ThemeProvider>
);
export const Root: React.FC = () => (
  <>
    <Composition id="EP1v3" component={EpisodeNoBgm} durationInFrames={FINAL_TOTAL} fps={30} width={1920} height={1080} />
    <Composition id="Cover916" component={Cover} defaultProps={{v: true}} durationInFrames={1} fps={30} width={1080} height={1920} />
    <Composition id="Cover43" component={Cover} defaultProps={{v: false}} durationInFrames={1} fps={30} width={1440} height={1080} />
    {/* 旧 id 保留，方便已有脚本继续用 */}
    <Composition id="Final" component={makeEpisode('pixel')} durationInFrames={FINAL_TOTAL} fps={30} width={1920} height={1080} />
    <Composition id="Episode" component={makeEpisode('pixel')} durationInFrames={FINAL_TOTAL} fps={30} width={1920} height={1080} />
    {/* 回归用：未上 120BPM 网格的时间轴。用来证明换皮没有改动任何画面内容。 */}
    <Composition id="Raw-pixel" component={makeEpisodeRaw('pixel')} durationInFrames={UNGRIDDED_TOTAL} fps={30} width={1920} height={1080} />
    <Composition id="Motion" component={MotionPreview} durationInFrames={MOTION_SEGS.reduce((a, s) => a + s.dur, 0)} fps={30} width={1920} height={1080} />
    {[['K1', K1], ['K2', K2], ['K3', K3], ['K4', K4]].map(([id, C]: any) => <Composition key={id} id={id} component={C} durationInFrames={160} fps={30} width={1920} height={1080} />)}

    {/* ---- 三套皮肤 × 两档帧率 = 6 个成片 composition ---- */}
    {SKIN_LIST.map((skin) => (
      <React.Fragment key={skin}>
        <Composition
          id={`EP1-${skin}`}
          component={makeEpisode(skin)}
          durationInFrames={FINAL_TOTAL}
          fps={30}
          width={1920}
          height={1080}
        />
        <Composition
          id={`EP1-${skin}-60fps`}
          component={makeEpisode(skin)}
          durationInFrames={FINAL_TOTAL * 2}
          fps={60}
          width={1920}
          height={1080}
        />
      </React.Fragment>
    ))}
  </>
);
