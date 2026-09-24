"""phoneVX_English: sohbet baloncuklarının metni (baloncuk şekilleri korunur)."""
import numpy as np
from PIL import Image
from metin import render_supersampled
MONO = "C:/Windows/Fonts/consolab.ttf"
# (kutu x0,x1,y0,y1), satırlar, yazı rengi (None = otomatik koyu), emoji taşınsın mı
BALONCUK = [
    ((218, 466, 170, 226), ["Oyun oynayalım mı?"]),
    ((132, 470, 258, 314), ["Fazla mesaiye boğuldum"]),
    ((132, 424, 346, 431), ["Yarın! Yarın", "mesai yok!"]),
    ((166, 466, 464, 549), ["VED çıkmak üzere!", "Birlikte alalım mı?"]),
    ((131, 440, 581, 664), ["Tabii! Çıkınca", "hemen oynarız!"]),
    ((237, 467, 790, 846), ["Oyuna var mısın?"]),
    ((131, 440, 897, 979), ["Bu akşam çocuğa", "bakmam lazım."]),
]
ETIKET = ((186, 418, 708, 736), "Geçen Salı 23:59")
CAP, PITCH = 15.5, 30
def main():
    a = np.array(Image.open("en/phoneVX_English.png").convert("RGBA"))
    im = Image.fromarray(a, "RGBA")
    for (x0, x1, y0, y1), lines in BALONCUK:
        bg = tuple(int(v) for v in np.median(a[y0 + 8:y1 - 8, x0 + 8:x1 - 8, :3].reshape(-1, 3), 0))
        sub = a[y0 + 6:y1 - 6, x0 + 10:x1 - 10]
        # emoji (renkli pikseller) varsa sakla
        sat = np.ptp(sub[..., :3].astype(int), -1) > 60
        emoji = None
        if bg == (255, 255, 255) and sat.sum() > 30:
            ys, xs = np.nonzero(sat)
            e = (x0 + 10 + xs.min() - 1, y0 + 6 + ys.min() - 1, x0 + 10 + xs.max() + 2, y0 + 6 + ys.max() + 2)
            emoji = im.crop(e)
        Image.Image.paste(im, bg, (x0 + 10, y0 + 6, x1 - 10, y1 - 6))
        col = (8, 26, 31) if bg != (255, 255, 255) else (0, 0, 0)
        cy = (y0 + y1) / 2
        bases = [cy + CAP / 2] if len(lines) == 1 else [cy - PITCH / 2 + CAP / 2, cy + PITCH / 2 + CAP / 2]
        endx = 0
        for t, b in zip(lines, bases):
            lay, lb, inkl, _ = render_supersampled(t, MONO, CAP, [(0, (*col, 255))], max_w=x1 - x0 - 44, ref_char="H")
            x = x0 + 24 - inkl
            im.alpha_composite(Image.fromarray((np.clip(lay, 0, 1) * 255).astype(np.uint8), "RGBA"), (int(round(x)), int(round(b - lb))))
            endx = x + lay.shape[1]; lastb = b
        if emoji is not None:
            im.paste(emoji, (int(endx + 2), int(lastb - emoji.height + 5)))
    (x0, x1, y0, y1), t = ETIKET
    pill = tuple(int(v) for v in a[(y0 + y1) // 2, x0 + 14, :3])
    Image.Image.paste(im, pill, (x0 + 8, y0 + 2, x1 - 8, y1 - 1))
    lay, lb, inkl, _ = render_supersampled(t, MONO, CAP - 1.5, [(0, (255, 255, 255, 255))], max_w=x1 - x0 - 24, ref_char="H")
    cols = np.nonzero(lay[..., 3].max(0) > 0.05)[0]
    x = (x0 + x1) / 2 - (cols.min() + cols.max()) / 2
    im.alpha_composite(Image.fromarray((np.clip(lay, 0, 1) * 255).astype(np.uint8), "RGBA"), (int(round(x)), int(round((y0 + y1) / 2 + (CAP - 1.5) / 2 - lb))))
    im.save("tr/phoneVX_English.png")
if __name__ == "__main__": main()
