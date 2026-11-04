import {pixelDark} from './pixelDark';
import {neonGlass} from './neonGlass';
import {paperEditorial} from './paperEditorial';

export const SKINS = {pixel: pixelDark, neon: neonGlass, paper: paperEditorial};
export type SkinId = keyof typeof SKINS;
export {pixelDark, neonGlass, paperEditorial};
