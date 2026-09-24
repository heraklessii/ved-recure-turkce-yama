"""Düz zeminli arayüz görselleri (oyun içi sahte mağaza/kütüphane ekranı)."""
import numpy as np
from PIL import Image
from metin import render_supersampled
YAHEI = "C:/Windows/Fonts/msyh.ttc"; YAHEI_B = "C:/Windows/Fonts/msyhbd.ttc"
def load(n): return np.array(Image.open(f"en/{n}.png").convert("RGBA"))
def clear(a, x0, y0, x1, y1):
    """kutuyu satır satır sol/sağ kenar renkleri arasında doğrusal doldur (gradyan korunur)"""
    for y in range(y0, y1):
        l = a[y, x0 - 1].astype(float); r = a[y, x1].astype(float)
        t = np.linspace(0, 1, x1 - x0)[:, None]
        a[y, x0:x1] = (l * (1 - t) + r * t).round().astype(np.uint8)
def ink_color(a, x0, y0, x1, y1, bright=True):
    sub = a[y0:y1, x0:x1, :3].reshape(-1, 3).astype(int); L = sub.mean(-1)
    sel = sub[L >= np.percentile(L, 97)] if bright else sub[L <= np.percentile(L, 3)]
    return tuple(int(v) for v in np.median(sel, 0))
def put(a, text, font, cap, base, x=None, cx=None, color=(255, 255, 255), max_w=None, ref="H", sx=1.0):
    lay, b, inkl, _ = render_supersampled(text, font, cap, [(0, (*color, 255))], sx=sx, max_w=max_w, ref_char=ref)
    im = Image.fromarray(a, "RGBA")
    if cx is not None:
        # mürekkep genişliğine göre ortala
        cols = np.nonzero(lay[..., 3].max(0) > 0.05)[0]; x = cx - (cols.min() + cols.max()) / 2 + inkl
    im.alpha_composite(Image.fromarray((np.clip(lay, 0, 1) * 255).astype(np.uint8), "RGBA"), (int(round(x - inkl)), int(round(base - b))))
    return np.array(im)
# ad: [(silinecek kutu), metin, font, cap, taban, sol x | None, orta x | None, azami genişlik, parlak mürekkep mi]
IS = {
    "buy_English": [((40, 4, 112, 39), "SATIN AL", YAHEI, 27, 35, None, 75, 140, True)],
    "playNow_English": [((26, 12, 132, 42), "Şimdi Oyna", YAHEI_B, 19, 34, None, 79, 146, True)],
    "goStoreHouse_English": [((115, 12, 336, 42), "Depoya Git", YAHEI, 21, 37, None, 225, 420, True)],
    "smallFrame_n_English": [((64, 31, 172, 66), "Sonra oynarım...", YAHEI, 21, 57, None, 117, 190, True)],
    "smallFrame_s_English": [((50, 16, 158, 51), "Sonra oynarım...", YAHEI, 21, 41, None, 103, 190, False)],
    "bigFrame_s_English": [((20, 14, 110, 45), "Ekle", YAHEI, 20, 39, 24, None, 110, False)],
    "bigFrame_n_English": [((34, 28, 214, 60), "Favorilere Ekle...", YAHEI, 21, 54, 39, None, 175, True),
                           ((34, 87, 140, 120), "Ekle", YAHEI, 21, 114, 38, None, 100, True),
                           ((34, 148, 140, 180), "Yönet", YAHEI, 21, 174, 39, None, 100, True),
                           ((34, 209, 214, 243), "Özellikler", YAHEI, 21, 235, 39, None, 175, True)],
    "1000_English": [((30, 0, 400, 25), "Sonra oynarım...（1000）", YAHEI_B, 20, 21, 33, None, 365, True)],
    "999_English": [((30, 0, 400, 25), "Sonra oynarım...（999）", YAHEI_B, 20, 21, 33, None, 365, True)],
    "999add1_English": [((30, 0, 400, 25), "Sonra oynarım...（999+1）", YAHEI_B, 20, 21, 33, None, 365, True)],
    "num0_English": [((30, 0, 400, 25), "Kategorisiz（0）", YAHEI_B, 20, 21, 33, None, 365, True)],
    "num1_English": [((30, 0, 400, 25), "Kategorisiz（1）", YAHEI_B, 20, 21, 33, None, 365, True)],
    "purchaseSuccess_English": [((290, 66, 735, 120), "Satın alma başarılı", YAHEI_B, 29, 105, None, 512, 440, True)],
}
if __name__ == "__main__":
    for n, jobs in IS.items():
        a = load(n)
        for (x0, y0, x1, y1), text, font, cap, base, x, cx, mw, bright in jobs:
            col = ink_color(a, x0, y0, x1, y1, bright)
            if x1 >= a.shape[1]: x1 = a.shape[1] - 1
            clear(a, x0, y0, x1, y1)
            a = put(a, text, font, cap, base, x=x, cx=cx, color=col, max_w=mw)
        Image.fromarray(a, "RGBA").save(f"tr/{n}.png"); print(n, "ok")
