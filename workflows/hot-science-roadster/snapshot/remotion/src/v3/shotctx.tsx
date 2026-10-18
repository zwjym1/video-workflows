import React, {createContext, useContext} from 'react';
export type Shot = {id: string; label?: string; src: string; start: number; end: number; in: number; rate: number};
export type Timeline = {version: number; composition?: string; fps?: number; shots: Shot[]; audio?: any};
const Ctx = createContext<Record<string, Shot>>({});
export const ShotProvider: React.FC<{shots: Shot[]; children: React.ReactNode}> = ({shots, children}) =>
  <Ctx.Provider value={Object.fromEntries(shots.map((s) => [s.id, s]))}>{children}</Ctx.Provider>;
export const useShot = (id?: string): Shot | undefined => { const m = useContext(Ctx); return id ? m[id] : undefined; };
