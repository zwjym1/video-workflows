#!/bin/bash
# usage: stills-v2.sh  -> renders keyframes for RoadsterShortV2
cd "$(dirname "$0")/.." && mkdir -p frames-v2
declare -a K=(
S01_hook_fly:1.3 S01_semi_tag:2.3 S02_not_vfx:3.9 S02_not_ai:5.3
S03_danmaku_scroll:7.2 S03_danmaku_highlight:9.0 S04_two_systems:12.2
TA_live_climb_start:13.5 TA_live_climb_wall:15.6 TA_live_topdown:16.6
TA_freeze:17.3 TA_crossfade:17.95 TA_fan_callout:18.5 TA_rotate_mid:19.8 TA_rotate_end:21.4 TA_lowpressure:22.0 TA_press:24.2 TA_2x:27.0
TB_live_start:28.3 TB_live_leap:29.9 TB_freeze:30.6 TB_crossfade:31.15 TB_tank:31.9 TB_rotate_mid:33.0 TB_valve:33.2 TB_jet:34.4 TB_arrows:37.3 TB_balloon:39.4 TB_side_jets:43.0 TB_spacex:45.8
S08_summary_left:48.8 S08_summary_both:50.4
S09_ask:52.2 S09_2028:54.3 S09_closed:57.5 S09_price:58.8 S09_deposit:60.4 S10_ending:62.8)
for kv in "${K[@]}"; do n=${kv%%:*}; s=${kv##*:}; f=$(python3 -c "print(round($s*30))")
  ./node_modules/.bin/remotion still src/index.tsx RoadsterShortV2 frames-v2/$n.jpg --frame=$f --image-format=jpeg --jpeg-quality=85 --gl=angle --log=error || echo FAIL $n
done
