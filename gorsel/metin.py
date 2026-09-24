"""Görsel üzerine katmanlı konturlu metin çizimi (düğmeler, başlıklar)."""
import numpy as np
from PIL import Image, ImageDraw, ImageFont, ImageFilter
from scipy import ndimage

def text_mask(text, font_path, size, sx=1.0, italic=0.0, spacing=0, line_gap=0.0, align='left'):
    """Metnin alfa maskesi (float 0..1) ve ilk satırın taban çizgisi (y). Satırlar '\n' ile."""
    f = ImageFont.truetype(font_path, size)
    lines = text.split('\n')
    asc, desc = f.getmetrics()
    lh = int((asc + desc) * (1 + line_gap))
    widths = [sum(f.getlength(c) for c in l) + spacing * max(0, len(l) - 1) for l in lines]
    W = int(max(widths) + size); H = lh * len(lines) + size
    im = Image.new('L', (W, H), 0); d = ImageDraw.Draw(im)
    for i, l in enumerate(lines):
        x = size // 2 + (0 if align == 'left' else (max(widths) - widths[i]) / (2 if align == 'center' else 1))
        for ch in l:
            d.text((x, size // 2 + i * lh), ch, font=f, fill=255); x += f.getlength(ch) + spacing
    base = size // 2 + asc
    a = np.asarray(im).astype(np.float32) / 255
    if sx != 1.0 or italic:
        # x' = sx*x + italic*(base - y)  (taban çizgisinde kayma yok)
        nw = int(W * sx + H * abs(italic)) + 2
        off = italic * base if italic < 0 else 0
        im2 = Image.fromarray((a * 255).astype(np.uint8))
        # ters dönüşüm: x = (x' - italic*(base-y) + off... ) / sx
        shift = H * abs(italic) if italic > 0 else 0
        im2 = im2.transform((nw, H), Image.AFFINE, (1 / sx, italic / sx, -(italic * H) / sx if italic > 0 else 0, 0, 1, 0), Image.BICUBIC)
        a = np.asarray(im2).astype(np.float32) / 255
    return a, base

def crop_ink(a, thr=0.02):
    ys, xs = np.nonzero(a > thr)
    return a[ys.min():ys.max() + 1, xs.min():xs.max() + 1]

def grow(a, r):
    """alfa maskesini r piksel genişlet (yuvarlak)"""
    if r <= 0: return a
    inside = a > 0.5
    dist = ndimage.distance_transform_edt(~inside)
    return np.clip(r + 0.5 - dist, 0, 1).astype(np.float32)

def layered(a, layers, pad=None):
    """a: harf maskesi (dolgu). layers: [(genişlik, RGBA)] içten dışa kontur; ilk öğe dolgu rengi (genişlik 0).
    Dönüş: RGBA float dizi (premultiplied olmayan)."""
    if pad is None: pad = int(max(w for w, _ in layers)) + 2
    a = np.pad(a, pad)
    H, W = a.shape
    out = np.zeros((H, W, 4), np.float32)
    # dıştan içe boya
    for w, col in sorted(layers, key=lambda t: -t[0]):
        m = grow(a, w) if w > 0 else a
        c = np.array(col, np.float32) / 255
        al = m * c[3]
        out[..., :3] = out[..., :3] * (1 - al[..., None]) + c[:3] * al[..., None]
        out[..., 3] = out[..., 3] * (1 - al) + al
    return out

def paste(base, layer, x, y):
    """base: PIL RGBA; layer: float RGBA (0..1) -> alpha composite at (x,y)"""
    L = Image.fromarray((np.clip(layer, 0, 1) * 255).astype(np.uint8), 'RGBA')
    base.alpha_composite(L, (int(round(x)), int(round(y))))
    return base

def render_supersampled(text, font_path, cap_px, layers, ss=4, sx=1.0, italic=0.0, max_w=None, spacing=0, line_gap=0.0, align='left', ref_char='H', min_sx=0.78):
    """cap_px: hedef büyük harf yüksekliği (px). max_w: kontur dahil azami genişlik (sığmazsa önce sx, sonra boyut küçülür).
    Dönüş: (RGBA float dizi, taban çizgisi y, dolgunun sol mürekkep x'i, gerçek cap)"""
    fr = ImageFont.truetype(font_path, 200); bb = fr.getbbox(ref_char); capr = (bb[3] - bb[1]) / 200
    def build(cap, sxx):
        size = int(round(cap * ss / capr))
        a, base = text_mask(text, font_path, size, sxx, italic, spacing * ss, line_gap, align)
        ys, xs = np.nonzero(a > 0.02)
        pad = int(max(w for w, _ in layers) * ss) + 2 + ss
        y0, x0 = max(0, ys.min() - pad), max(0, xs.min() - pad)
        a = a[y0:ys.max() + 1 + pad, x0:xs.max() + 1 + pad]
        inkl = xs.min() - x0; base -= y0
        # boyutları ss'nin katına yuvarla
        H = -(-a.shape[0] // ss) * ss; W = -(-a.shape[1] // ss) * ss
        a = np.pad(a, ((0, H - a.shape[0]), (0, W - a.shape[1])))
        lay = layered(a, [(w * ss, c) for w, c in layers], pad=0)
        im = Image.fromarray((np.clip(lay, 0, 1) * 255).astype(np.uint8), 'RGBA')
        # premultiply ile küçült (kenar hâleleri olmasın)
        arr = np.asarray(im).astype(np.float32) / 255
        pm = arr.copy(); pm[..., :3] *= pm[..., 3:4]
        pm = pm.reshape(H // ss, ss, W // ss, ss, 4).mean((1, 3))
        al = pm[..., 3:4]; rgb = np.where(al > 1e-4, pm[..., :3] / np.maximum(al, 1e-4), 0)
        return np.concatenate([rgb, al], -1), base / ss, inkl / ss
    cap = cap_px; sxx = sx
    lay, base, inkl = build(cap, sxx)
    if max_w:
        while lay.shape[1] > max_w and sxx > sx * min_sx:
            sxx *= 0.97; lay, base, inkl = build(cap, sxx)
        while lay.shape[1] > max_w:
            cap *= 0.97; lay, base, inkl = build(cap, sxx)
    return lay, base, inkl, cap
