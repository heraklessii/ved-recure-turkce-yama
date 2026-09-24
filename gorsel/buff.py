"""Buff başlığı görselleri (buffTitle_*_English): yazıyı sil, noktalı paneli onar, Türkçesini çiz."""
import numpy as np, sys
from PIL import Image
from scipy import ndimage
from metin import render_supersampled
FONT = "C:/Windows/Fonts/seguibli.ttf"
def lum(a): return a[..., :3].astype(float).mean(-1)
def text_mask(a, xmax, y0=62, y1=160):
    L = lum(a); al = a[..., 3] > 100
    dark = (L < 110) & al
    zone = np.zeros(dark.shape, bool); zone[y0:y1, :xmax] = True
    m = dark & zone
    m = ndimage.binary_closing(m, np.ones((3, 3)))
    m = ndimage.binary_fill_holes(m)
    m = ndimage.binary_dilation(m, iterations=2) & zone & al
    # bölgede kalan küçük koyu kırıntılar (eski harf kenarları) da silinir; simgeler büyük bağlı parçalardır
    rest = (L < 170) & zone & al & ~m
    lab, k = ndimage.label(rest, np.ones((3, 3)))
    if k:
        sizes = ndimage.sum(rest, lab, range(1, k + 1))
        small = np.isin(lab, 1 + np.nonzero(sizes < 250)[0])
        m |= ndimage.binary_dilation(small, iterations=1) & zone & al
    return m
def period(a, m):
    """noktalı desenin periyodunu (dx,dy) otokorelasyonla bul"""
    L = lum(a); H, W = L.shape
    best = None
    for dy in range(0, 14):
        for dx in range(-13, 14):
            if (dy, dx) <= (0, 3) and dy == 0 and dx <= 3: continue
            if dy == 0 and dx < 0: continue
            if abs(dx) + dy < 4: continue
            A = L[max(0, -dy):H - max(0, dy), max(0, -dx):W - max(0, dx)]
            B = L[max(0, dy):H - max(0, -dy) if dy < 0 else H, max(0, dx):W - max(0, -dx) if dx < 0 else W]
            MA = (~m)[max(0, -dy):H - max(0, dy), max(0, -dx):W - max(0, dx)] & (a[..., 3] > 250)[max(0, -dy):H - max(0, dy), max(0, -dx):W - max(0, dx)]
            h = min(A.shape[0], B.shape[0]); w = min(A.shape[1], B.shape[1])
            A, B, MA = A[:h, :w], B[:h, :w], MA[:h, :w]
            sel = MA & (A > 150) & (B > 150)
            if sel.sum() < 500: continue
            e = np.abs(A[sel] - B[sel]).mean()
            if best is None or e < best[0]: best = (e, dx, dy)
    return best
def fill_periodic(a, m, vecs, panel):
    """maskeli pikselleri, desen periyodu kadar kaydırılmış en yakın temiz panel pikseliyle doldur"""
    out = a.copy(); H, W = m.shape
    ys, xs = np.nonzero(m)
    cands = sorted({(i * vecs[0][0] + j * vecs[1][0], i * vecs[0][1] + j * vecs[1][1]) for i in range(-12, 13) for j in range(-12, 13)} - {(0, 0)},
                   key=lambda v: v[0] ** 2 + v[1] ** 2)
    ok = (~m) & panel
    for y, x in zip(ys, xs):
        for dx, dy in cands:
            yy, xx = y + dy, x + dx
            if 0 <= yy < H and 0 <= xx < W and ok[yy, xx]:
                out[y, x] = a[yy, xx]; break
    return out

# satır stilleri: (x, büyük harf üstü, taban) ve bölgeler
L1 = dict(x=14, top=90, base=114)
L2 = dict(x=38, top=129, base=151)
STIL1 = [(0, (28, 28, 28, 255)), (2.2, (255, 255, 255, 255))]
STIL2 = [(0, (255, 255, 255, 255)), (2.6, (20, 20, 20, 255)), (4.0, (255, 255, 255, 255))]
COMBO = ("Kombo", "Bitirici", 125, 160)
BASLIKLAR = {  # ad: (satır1, satır2, satır1 sağ sınır, satır2 sağ sınır)
    "buffTitle_1": ("Kaçınma", "Karşılığı", 125, 160),
    "buffTitle_2": ("Özel", "Saldırı", 131, 160),
    "buffTitle_3": ("Ek", "Saldırı", 98, 160),
    "buffTitle_4": (None, "Savuşturma", 0, 170),
    "buffTitle_5": ("Engelleme/", "Yaralanma", 150, 165),
    **{f"buffTitle_{k}": COMBO for k in (1001, 1002, 1003, 1005, 1006, 1008, 1009)},
}
ESKI_SAG = {"buffTitle_1": (122, 160), "buffTitle_2": (131, 108), "buffTitle_3": (98, 108), "buffTitle_4": (0, 125),
            "buffTitle_5": (128, 112)}
def isle(n, out_dir="tr", italic=0.18, sx=0.95):
    a = np.array(Image.open(f"en/{n}_English.png").convert("RGBA"))
    t1, t2, r1, r2 = BASLIKLAR[n]
    e1, e2 = ESKI_SAG.get(n, (126, 152))
    zone = np.zeros(a.shape[:2], bool)
    if e1: zone[74:121, 4:e1] = True
    zone[121:160, 30:e2] = True
    L = lum(a); al = a[..., 3] > 100
    # İngilizce yazı pikseli: diğer üç dil sürümünün HİÇBİRİNE benzemez (arka plan/simge en az birinde aynıdır)
    difs = [np.abs(np.array(Image.open(f"en/{n}_{lang}.png").convert("RGBA")).astype(int) - a.astype(int)).max(-1)
            for lang in ("Chinese", "ChineseTraditional", "Japanese")]
    var = np.max(difs, 0); mind = np.min(difs, 0)
    m = (mind > 35) & al & zone
    m = ndimage.binary_opening(m, np.ones((2, 2)))
    m = ndimage.binary_closing(m, np.ones((3, 3)))
    m = ndimage.binary_fill_holes(m)
    m = ndimage.binary_dilation(m, iterations=2) & zone & al
    # bölgede kalan küçük koyu kırıntılar (eski harf kenarları) da silinir; simgeler büyük bağlı parçalardır
    rest = (L < 170) & zone & al & ~m
    lab, k = ndimage.label(rest, np.ones((3, 3)))
    if k:
        sizes = ndimage.sum(rest, lab, range(1, k + 1))
        small = np.isin(lab, 1 + np.nonzero(sizes < 250)[0])
        m |= ndimage.binary_dilation(small, iterations=1) & zone & al
    # panelin sol kenarı ve alt kenarı (yazısız satır/sütundan)
    left = int(np.nonzero(a[70, :, 3] > 200)[0].min())
    bottom = int(np.nonzero(a[:, 27, 3] > 200)[0].max())
    panel = al & (L > 120) & (var < 20)
    src = panel & ~zone; src[:, 100:] = False     # kaynak: yalnızca soldaki noktalı panel (simgeden kopyalama olmasın)
    b = fill_periodic(a, m, [(11, 0), (0, 11)], src)
    out = np.zeros_like(a[..., 3], bool); out[:, :left] = True; out[bottom + 1:, :] = True
    b[zone & out] = 0
    res = Image.fromarray(b)
    for t, Lx, st, r in ((t1, L1, STIL1, r1), (t2, L2, STIL2, r2)):
        if not t: continue
        cap = Lx["base"] - Lx["top"]
        lay, lb, inkl, capr = render_supersampled(t, FONT, cap, st, sx=sx, italic=italic, max_w=r - Lx["x"] + 6, ref_char="H")
        res.alpha_composite(Image.fromarray((np.clip(lay, 0, 1) * 255).astype(np.uint8), "RGBA"), (int(round(Lx["x"] - inkl)), int(round(Lx["base"] - lb))))
    res.save(f"{out_dir}/{n}_English.png")
if __name__ == "__main__":
    for n in BASLIKLAR: isle(n)
