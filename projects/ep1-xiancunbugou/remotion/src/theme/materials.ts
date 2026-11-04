/**
 * 画材派生：从 pixelDark 的原始画材推导出其它皮肤的同一套色。
 * 目的是「换皮不换构图，也不丢画材的明暗层次」——显卡还是显卡，
 * 只是从米白纸上的橙金块，变成深蓝底上的青紫发光块 / 纸上的墨与朱红。
 */
import {BASE_MATERIALS} from './tokens';
import {remap, RemapSpec} from './color';

export const deriveMaterials = (spec: RemapSpec, overrides: Record<string, string> = {}): Record<string, string> => {
  const out: Record<string, string> = {};
  for (const [k, v] of Object.entries(BASE_MATERIALS)) {
    out[k] = remap(v, spec);
  }
  return {...out, ...overrides};
};

/** 把画材表导出成 CSS 变量（--m-<token>） */
export const materialVars = (m: Record<string, string>) => {
  const vars: Record<string, string> = {};
  for (const [k, v] of Object.entries(m)) vars[`--m-${k}`] = v;
  return vars;
};

/** 取某个画材的 CSS 变量引用 */
export const mat = (token: string) => `var(--m-${token})`;
