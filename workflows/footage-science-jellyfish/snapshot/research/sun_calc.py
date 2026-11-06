"""F4/F5 复算：NOAA 近似太阳高度 + 地影高度 h = R(1/cos d − 1)。python3 research/sun_calc.py"""
import math, datetime as dt
def sun_alt(lat, lon, t_utc):
    n = t_utc.timetuple().tm_yday; hr = t_utc.hour + t_utc.minute / 60 + t_utc.second / 3600
    g = 2 * math.pi / 365 * (n - 1 + (hr - 12) / 24)
    eqt = 229.18 * (0.000075 + 0.001868 * math.cos(g) - 0.032077 * math.sin(g) - 0.014615 * math.cos(2 * g) - 0.040849 * math.sin(2 * g))
    dec = 0.006918 - 0.399912 * math.cos(g) + 0.070257 * math.sin(g) - 0.006758 * math.cos(2 * g) + 0.000907 * math.sin(2 * g) - 0.002697 * math.cos(3 * g) + 0.00148 * math.sin(3 * g)
    ha = math.radians((hr * 60 + eqt + 4 * lon) / 4 - 180); la = math.radians(lat)
    return math.degrees(math.asin(math.sin(la) * math.sin(dec) + math.cos(la) * math.cos(dec) * math.cos(ha)))
R = 6371.0
for name, lat, lon, hh, mm in (('太原发射', 37.87, 112.55, 18, 15), ('济南观测', 36.65, 117.12, 18, 20)):
    t = dt.datetime(2026, 10, 23, hh - 8, mm)
    a = sun_alt(lat, lon, t); d = -a
    # 日落（几何中心 −0.833°）
    s = t
    while sun_alt(lat, lon, s) < -0.833: s -= dt.timedelta(minutes=1)
    print(f"{name} {hh}:{mm:02d}  太阳高度 {a:.1f}°  日落约 {(s + dt.timedelta(hours=8)):%H:%M}  落山后 {(t - s).seconds // 60} 分钟  头顶地影高度 {R * (1 / math.cos(math.radians(d)) - 1):.0f} km")
for d in (7.2, 10, 11.6): print(f"d={d}° → 地影高度 {R * (1 / math.cos(math.radians(d)) - 1):.0f} km")
