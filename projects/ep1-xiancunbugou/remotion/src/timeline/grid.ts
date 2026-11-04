/**
 * 120 BPM 硬卡点网格
 * ------------------------------------------------------------------
 * BGM = We Never (Hi Noise remix)，已拉伸到精确 120 BPM：
 *   1 拍 = 0.5s = 15 设计帧（30fps 基准）
 *   1 小节 = 4 拍 = 2.0s = 60 设计帧
 *
 * 两条硬约束：
 *   1) 章节卡必须落在小节线（整 60 帧）上 —— 观众听到的「咚」和标题出现必须同一帧。
 *   2) 所有镜头起点必须落在拍子（整 15 帧）上 —— 换镜头的「嚓」要踩着拍走。
 *
 * 配音长度是固定的（不能裁），所以只能往后补：
 *   - 镜头：向上取整到 15 的整数倍（最多补 14 帧 = 0.47s）
 *   - 章节卡：向上取整到 60 的整数倍，最小 120 帧（2 小节）
 *   - 章节卡之前那一串镜头的总长必须凑够整小节，否则卡片会从小节中间开始。
 *     差额按 15 帧为单位，平均摊给这一串里的镜头（零头落在靠后的镜头上，
 *     读起来像「进章节前的一口气」），每镜最多多补 1 小格，不会出现长定格。
 *
 * BGM 相位：拍点相对整帧网格偏 0.03s。Audio.tsx 会裁掉音频开头这 0.03s
 * （见下面的 BGM_PHASE_SEC），于是拍点正好落在整 15 / 60 帧上，画面和音乐零误差。
 */
export const BEAT_FRAMES = 15;
export const BAR_FRAMES = 4 * BEAT_FRAMES; // 60
export const CARD_MIN_FRAMES = 2 * BAR_FRAMES; // 120

export type GridInput = {dur: number};

/** 只算时长，不改内容。返回与输入等长的最终时长数组。 */
export const gridDurations = (segs: (GridInput & {isCard?: boolean})[]): number[] => {
  const n = segs.length;
  // 1) 单段对齐：卡对小节，镜头对拍
  const dur = segs.map((s) =>
    s.isCard
      ? Math.max(CARD_MIN_FRAMES, Math.ceil(s.dur / BAR_FRAMES) * BAR_FRAMES)
      : Math.ceil(s.dur / BEAT_FRAMES) * BEAT_FRAMES);

  // 2) 每串「连续镜头」的总长补到整小节，保证下一张卡的起点在小节线上
  let i = 0;
  while (i < n) {
    if (segs[i].isCard) { i++; continue; }
    let j = i;
    while (j < n && !segs[j].isCard) j++;
    const cnt = j - i;
    let tot = 0;
    for (let k = i; k < j; k++) tot += dur[k];
    const units = ((BAR_FRAMES - (tot % BAR_FRAMES)) % BAR_FRAMES) / BEAT_FRAMES;
    for (let k = 0; k < cnt; k++) {
      // 均摊：第 k 段拿到第 k+1 与第 k 个累计台阶之差，零头自然落到后面
      const add = Math.floor(((k + 1) * units) / cnt) - Math.floor((k * units) / cnt);
      dur[i + k] += add * BEAT_FRAMES;
    }
    i = j;
  }
  return dur;
};

/** 就地套网格，返回新的 segs 数组 */
export const gridSegs = <T extends GridInput>(segs: T[], isCard: (s: T) => boolean): T[] => {
  const dur = gridDurations(segs.map((s) => ({dur: s.dur, isCard: isCard(s)})));
  return segs.map((s, k) => ({...s, dur: dur[k]}));
};

/**
 * 音频相位（秒）：beats json 的 offset。
 * 拍点都落在「整 15 帧 + 0.9 帧」上，0.9 帧没法用整帧对齐，
 * 所以反过来裁掉音频开头的 0.03s（30fps 下正好 1 帧，60fps 下 2 帧），
 * 拍点就落到整帧网格上。残余 -3.3ms（-0.1 设计帧），两档帧率完全一致。
 * 裁掉的是静音前奏，听不出差别。
 */
export const BGM_PHASE_SEC = 0.03;
