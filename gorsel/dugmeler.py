"""Düğme görselleri (btn_*_English vb.): İngilizce yazıyı sil, Türkçesini aynı stilde çiz."""
import numpy as np, sys
from PIL import Image
from scipy import ndimage
from metin import render_supersampled, grow
FONT = "C:/Windows/Fonts/seguibl.ttf"
# ad, türkçe, yazının bulunduğu satır aralığı (y0,y1) — alttaki fiyat etiketini korumak için
# ad, türkçe, satır aralığı (y0,y1), ilk harfin sol x'i, büyük harf üstü, taban çizgisi (orijinalden ölçüldü)
DUGMELER = [
    ("btn_buy_English", "Satın Al", (0, 80), 101, 19, 59),
    ("btn_cancel_English", "İptal", (0, 125), 93, 48, 84),
    ("btn_equip_English", "Kuşan", (0, 125), 104, 48, 83),
    ("btn_equipped_English", "Kuşanıldı", (0, 125), 78, 41, 79),
    ("btn_replace_English", "Değiştir", (0, 125), 91, 44, 83),
    ("btn_sell_English", "Seç", (0, 125), 92, 45, 83),
    ("btn_strengthen_English", "Güçlendir", (0, 125), 86, 44, 82),
    ("btn_unmount_English", "Çıkar", (0, 125), 101, 46, 78),
    ("refresh_English", "Yenile", (0, 78), 95, 29, 65),
    ("lockFrame_n_English", "Kilitle", (0, 156), 79, 45, 80),
]
def analiz(a, y0, y1):
    al = a[..., 3] > 128; lum = a[..., :3].astype(int).sum(-1) / 3
    dark = al & (lum < 90); ext = ~al
    extn = ndimage.binary_dilation(ext, np.ones((3, 3)))
    lab, n = ndimage.label(dark, np.ones((3, 3)))
    core = []
    for k, sl in enumerate(ndimage.find_objects(lab), 1):
        if sl[0].start < y0 or sl[0].stop > y1: continue
        m = lab[sl] == k
        if (extn[sl] & m).any(): continue          # dış siyah kontur
        if m.sum() < 15: continue
        core.append((sl[1].start, sl[1].stop, sl[0].start, sl[0].stop, k))
    core.sort()
    return core, lab
def isle(name, text, yr, left, cap_top, base, out_dir="tr", font=FONT, sx=0.9, w_white=4.0, w_black=9.0):
    im = Image.open(f"en/{name}.png").convert("RGBA"); a = np.array(im)
    H, W = a.shape[:2]
    core, lab = analiz(a, *yr)
    grp = [c for c in core if c[0] >= left - 2]
    letters = np.isin(lab, [g[4] for g in grp])
    blob = grow(letters.astype(np.float32), w_black + 5) > 0
    # simgeyi ve kendi konturunu koru (simge bileşenleri + renkli pikseller, delikleri doldurulmuş)
    icon = np.isin(lab, [c[4] for c in core if c[1] <= left - 2])
    col = (a[..., 3] > 128) & (np.ptp(a[..., :3].astype(int), -1) > 40)
    col[:, left - 4:] = False
    icon = ndimage.binary_fill_holes(icon | col)
    blob &= ~(grow(icon.astype(np.float32), w_black + 1.0) > 0)
    blob[:, :left - int(w_black) - 14] = False
    a2 = a.copy(); a2[blob, 3] = 0; a2[blob, :3] = 0
    cap = base - cap_top
    lay, lb, inkl, capr = render_supersampled(text, font, cap, [(0, (0, 0, 0, 255)), (w_white, (255, 255, 255, 255)), (w_black, (0, 0, 0, 255))],
                                              sx=sx, max_w=W - 1 - (left - int(w_black) - 2), ref_char="H")
    x = left - inkl; y = base - lb
    res = Image.fromarray(a2); L = Image.fromarray((np.clip(lay, 0, 1) * 255).astype(np.uint8), "RGBA")
    res.alpha_composite(L, (int(round(x)), int(round(y))))
    res.save(f"{out_dir}/{name}.png")
    print(f"{name:24} {text!r:12} cap={cap} çizilen={capr:.1f} genişlik={lay.shape[1]}")
if __name__ == "__main__":
    for d in DUGMELER: isle(*d)
