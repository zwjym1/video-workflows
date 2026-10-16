// Frame-driven event table (30fps). Sound effects use the same frames.
export const FPS=30,DURATION=360;
export const T={
 planeIn:[0,14],axes:[6,22],target:[16,28],point:[24,34],guides:[32,46],
 tilt:[70,100],rise:[78,108],proj:[100,112],labels:[104,116],bar:[108,126],
 cut:160,compA:[170,184],compB:[190,204],para:[210,222],result:[218,234],fadeComp:[240,250],
 move:[252,272],side:[276,300],delta:[296,310],
} as const;
export const sfx=[
 {frame:24,audio:'sync-tap.wav',volume:.5},
 {frame:78,audio:'sync-sweep.wav',volume:.45},
 {frame:110,audio:'sync-tap.wav',volume:.4},
 {frame:170,audio:'sync-arrow.wav',volume:.45},
 {frame:190,audio:'sync-arrow.wav',volume:.45},
 {frame:218,audio:'sync-arrow.wav',volume:.5},
 {frame:252,audio:'sync-paper.wav',volume:.5},
];
