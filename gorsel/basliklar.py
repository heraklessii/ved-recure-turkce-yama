"""Tek parça başlık görselleri: TOPLAM HASAR, RASTGELE, EKİPMAN DEPOLANDI, DAVETİYE, Dil."""
import numpy as np, cv2
from PIL import Image
from scipy import ndimage
from metin import render_supersampled, text_mask, grow, layered
ANTON = "Anton.ttf"; ARCHIVO = "Archivo-Black.ttf"
SEGOE_BLACK = "C:/Windows/Fonts/seguibl.ttf"
def load(n): return np.array(Image.open(f"en/{n}.png").convert("RGBA"))
def save(a, n): Image.fromarray(a.astype(np.uint8), "RGBA").save(f"tr/{n}.png")
def comp(base, lay, x, y):
    im = Image.fromarray(base.astype(np.uint8), "RGBA")
    im.alpha_composite(Image.fromarray((np.clip(lay, 0, 1) * 255).astype(np.uint8), "RGBA"), (int(round(x)), int(round(y))))
    return np.array(im)

def dmg_total():
    a = load("DmgTotal_English"); a[:] = 0
    lay, base, inkl, cap = render_supersampled("TOPLAM HASAR", ANTON, 58, [(0, (200, 200, 200, 255)), (6.5, (24, 24, 24, 255))], sx=1.0, italic=0.22, max_w=600)
    # dolguya hafif dikey gradyan (orijinaldeki gibi üstte açık)
    h = lay.shape[0]; g = np.linspace(1.08, 0.86, h)[:, None]
    fill = (lay[..., 0] > 0.6)
    lay[..., :3] = np.where(fill[..., None], np.clip(lay[..., :3] * g[..., None], 0, 1), lay[..., :3])
    x = 592 - lay.shape[1]; y = 76 - base
    save(comp(a, lay, x, y), "DmgTotal_English")

def directional_fill(a, m, d, maxt=400):
    """maskeli pikselleri d yönünde (iki taraf) en yakın maskesiz pikselle doldur"""
    out = a.copy(); H, W = m.shape
    d = np.array(d, float); d /= np.hypot(*d)
    ys, xs = np.nonzero(m)
    for y, x in zip(ys, xs):
        for t in range(1, maxt):
            done = False
            for s in (1, -1):
                xx = int(round(x + s * t * d[0])); yy = int(round(y + s * t * d[1]))
                if 0 <= xx < W and 0 <= yy < H and not m[yy, xx]:
                    out[y, x] = a[yy, xx]; done = True; break
            if done: break
    return out

def random_equip():
    a = load("randomEquip_English")
    # "RANDOM" gri yazı: x 12..222, y 22..66 ; koyu dokulu zemin
    zone = np.zeros(a.shape[:2], bool); zone[18:70, 10:226] = True
    L = a[..., :3].astype(int).mean(-1)
    m = zone & (L > 85)
    m = ndimage.binary_dilation(m, iterations=2) & zone
    rgb = cv2.inpaint(np.ascontiguousarray(a[..., :3]), m.astype(np.uint8) * 255, 7, cv2.INPAINT_TELEA)
    b = a.copy(); b[..., :3] = rgb
    # renk: orijinal yazının ortanca rengi
    col = np.median(a[m & (L > 110)][:, :3], 0).astype(int)
    lay, base, inkl, cap = render_supersampled("RASTGELE", ARCHIVO, 36, [(0, (*col, 255))], sx=0.92, max_w=300)
    b = comp(b, lay, 16 - inkl, 62 - base)
    save(b, "randomEquip_English")
    return col

def texture_from(a, alpha_thr=128):
    """harflerin içindeki dokuyu tüm alana yay (inpaint)"""
    known = a[..., 3] > alpha_thr
    # harf kenarlarındaki koyu hâleleri dışarıda bırak
    known = ndimage.binary_erosion(known, iterations=2)
    rgb = cv2.inpaint(np.ascontiguousarray(a[..., :3]), (~known).astype(np.uint8) * 255, 9, cv2.INPAINT_TELEA)
    return rgb

def get_weapon():
    a = load("GETWeapon_English")
    tex = texture_from(a)
    H, W = a.shape[:2]
    # orijinal: büyük harf yüksekliği ~ y 32..136
    size_cap = 104
    lay, base, inkl, cap = render_supersampled("EKİPMAN DEPOLANDI", ANTON, size_cap, [(0, (255, 255, 255, 255))], sx=1.0, max_w=W - 4, ref_char="E")
    al = lay[..., 3]
    out = np.zeros_like(a)
    x0 = int(round(2 - inkl + 0)); y0 = int(round(136 - base))
    h, w = al.shape
    ys, xs = slice(max(0, y0), min(H, y0 + h)), slice(max(0, x0), min(W, x0 + w))
    sub = al[ys.start - y0:ys.stop - y0, xs.start - x0:xs.stop - x0]
    out[ys, xs, :3] = tex[ys, xs]; out[ys, xs, 3] = (sub * 255).astype(np.uint8)
    save(out, "GETWeapon_English"); print("GETWeapon cap", cap, "w", w)

def invitation():
    a = load("Invitation_English")
    H, W = a.shape[:2]
    # taç (sol üstteki figür) korunur: renkli/koyu konturlu küçük bölge
    crown = np.zeros((H, W), bool); crown[95:235, 0:135] = True
    # doku: harflerin açık renkli iç kısmı
    L = a[..., :3].astype(int).mean(-1)
    letters = (a[..., 3] > 128) & (L > 120) & ~crown
    known = ndimage.binary_erosion(letters, iterations=2)
    tex = cv2.inpaint(np.ascontiguousarray(a[..., :3]), (~known).astype(np.uint8) * 255, 9, cv2.INPAINT_TELEA)
    # düz metni çiz (dolgu maskesi), sonra perspektifle dörtgene oturt
    m, base = text_mask("DAVETİYE", ANTON, 400, 1.0)
    m0, _ = text_mask("DAVETIYE", ANTON, 400, 1.0)       # noktasız: gövde kutusu buna göre
    ys, xs = np.nonzero(m0 > 0.02)
    top, bot, lft, rgt = ys.min(), ys.max() + 1, xs.min(), xs.max() + 1
    ya, _ = np.nonzero(m > 0.02); pad_top = top - ya.min()
    m = m[ya.min():bot, lft:rgt]
    h, w = bot - top, rgt - lft
    # orijinal harf gövdesinin köşeleri (ölçüldü): sol üst, sağ üst, sağ alt, sol alt
    dst = np.float32([[80, 190], [964, 30], [966, 364], [78, 420]])
    src = np.float32([[0, pad_top], [w, pad_top], [w, pad_top + h], [0, pad_top + h]])
    P = cv2.getPerspectiveTransform(src, dst)
    fill = cv2.warpPerspective(m.astype(np.float32), P, (W, H), flags=cv2.INTER_LINEAR)
    # gölge: sağa-aşağı kalın siyah ekstrüzyon
    sh = np.zeros_like(fill)
    for k in range(1, 22):
        sh = np.maximum(sh, np.roll(np.roll(fill, int(k * 0.9), 1), int(k * 0.75), 0))
    out = np.zeros_like(a)
    out[..., 3] = (np.clip(np.maximum(sh, fill), 0, 1) * 255).astype(np.uint8)
    out[..., :3] = (tex * fill[..., None]).astype(np.uint8)   # gölge siyah
    # taç figürünü orijinalden geri koy
    # taç: İngilizce ve Çince sürümde birebir aynı pikseller (harfler iki sürümde farklıdır)
    c = load("Invitation_Chinese")
    same = np.abs(c.astype(int) - a.astype(int)).max(-1) < 30
    cm = crown & (a[..., 3] > 20) & same
    cm = ndimage.binary_opening(cm, np.ones((2, 2)))
    cm = ndimage.binary_fill_holes(ndimage.binary_closing(cm, np.ones((3, 3)), iterations=3)) & crown & (a[..., 3] > 20)
    o = Image.fromarray(out, "RGBA"); ci = a.copy(); ci[~cm] = 0
    o.alpha_composite(Image.fromarray(ci, "RGBA")); out = np.array(o)
    save(out, "Invitation_English")

def language_frame():
    a = load("LanguageTest")
    # "Language": beyaz dolgu + siyah kontur, x ~262..482, y ~128..190
    zone = np.zeros(a.shape[:2], bool); zone[118:198, 255:490] = True
    L = a[..., :3].astype(int).mean(-1); al = a[..., 3]
    white = (L > 200) & (al > 200) & zone
    dark = (L < 60) & (al > 200) & zone
    # yazı = beyaz harfler + onları saran siyah kontur (harflerden 8 px içinde)
    wl = ndimage.binary_opening(white, np.ones((2, 2)))
    lab, n = ndimage.label(wl)
    # siyah zemin üstündeki beyaz bileşenler harftir; yırtık kağıt şeridi (sol-alt) büyük bir bileşen olabilir: boyut ve konuma bak
    sizes = ndimage.sum(wl, lab, range(1, n + 1))
    letters = np.zeros_like(wl)
    for k, sl in enumerate(ndimage.find_objects(lab), 1):
        hh = sl[0].stop - sl[0].start
        if hh < 60 and sizes[k - 1] > 20: letters |= lab == k
    m = grow(letters.astype(np.float32), 9) > 0
    m &= zone
    d = (4.0, -3.0)   # şeridin yönü (sol-alttan sağ-üste)
    b = directional_fill(a, m, d)
    lay, base, inkl, cap = render_supersampled("Dil", SEGOE_BLACK, 40, [(0, (255, 255, 255, 255)), (6, (10, 10, 10, 255))], sx=1.0)
    # orijinal "Language" başlangıcı x~268, taban ~y 172
    b = comp(b, lay, 300 - inkl, 173 - base)
    save(b, "LanguageTest")
    return int(m.sum())

if __name__ == "__main__":
    import sys
    for f in (sys.argv[1:] or ["dmg_total", "random_equip", "get_weapon", "invitation", "language_frame"]):
        print(f, globals()[f]())
