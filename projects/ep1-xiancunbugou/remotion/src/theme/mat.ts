/** 最小的画材变量引用工具。单独成文件，避免 sprites.tsx ↔ kit.tsx 循环依赖。 */
export const m = (token: string) => `var(--m-${token})`;
export const sv = (token: string) => `var(--t-${token})`;
