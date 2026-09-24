"""gorsel/tr/*.png -> build/gorseller.pkl : [(resS dosyası, ofset, ham bayt)] — doku piksellerini yerinde değiştirir.
Oyun ORİJİNAL hâldeyken çalıştırılmalı (dokuların yeri ve boyutu orijinal dosyadan okunur)."""
import os, sys, pickle, numpy as np, UnityPy, etcpak
from PIL import Image
D = "C:/Program Files (x86)/Steam/steamapps/common/Ved疗愈所/ved_Data/"
HERE = os.path.dirname(os.path.abspath(__file__))
# doku adı -> (varlık dosyası)
KAYNAK = {"LanguageTest": "sharedassets0.assets"}
def encode(img, fmt):
    a = np.array(img.convert("RGBA"))[::-1]            # Unity: alt satır önce
    h, w = a.shape[:2]
    if fmt == 4: return a.tobytes()
    if fmt == 3: return a[..., :3].tobytes()
    if fmt == 10: return etcpak.compress_bc1(np.ascontiguousarray(a).tobytes(), w, h)
    if fmt == 12: return etcpak.compress_bc3(np.ascontiguousarray(a).tobytes(), w, h)
    raise ValueError(fmt)
def textures(names):
    found = {}
    for fn in sorted({KAYNAK.get(n, "resources.assets") for n in names}):
        sf = list(UnityPy.load(D + fn).files.values())[0]
        for pid, o in sf.objects.items():
            if o.type.name != "Texture2D": continue
            t = o.read()
            if t.m_Name in names and KAYNAK.get(t.m_Name, "resources.assets") == fn:
                assert t.m_Name not in found, "aynı adlı iki doku: " + t.m_Name
                found[t.m_Name] = (t, fn)
    return found
def main(check=False):
    names = [f[:-4] for f in os.listdir(os.path.join(HERE, "tr")) if f.endswith(".png")]
    tex = textures(set(names))
    out = []
    for n in sorted(names):
        t, fn = tex[n]; sd = t.m_StreamData
        assert sd.path and getattr(t, "m_MipCount", 1) == 1, n
        src = "en" if check else "tr"
        img = Image.open(os.path.join(HERE, src, n + ".png"))
        assert img.size == (t.m_Width, t.m_Height), n
        raw = encode(img, t.m_TextureFormat)
        assert len(raw) == sd.size, (n, len(raw), sd.size)
        if check:
            with open(D + sd.path, "rb") as f: f.seek(sd.offset); orig = f.read(sd.size)
            if t.m_TextureFormat in (3, 4): print(f"{n:28} fmt={t.m_TextureFormat} birebir={raw == orig}")
            else:
                import texture2ddecoder as td
                dec = lambda b: np.frombuffer((td.decode_bc1 if t.m_TextureFormat == 10 else td.decode_bc3)(b, t.m_Width, t.m_Height), np.uint8).astype(int)
                print(f"{n:28} fmt={t.m_TextureFormat} ort. fark={np.abs(dec(raw) - dec(orig)).mean():.2f}")
        out.append((sd.path, sd.offset, raw))
        print(f"{n:28} -> {sd.path}@{sd.offset} ({len(raw)} bayt)")
    if not check:
        pickle.dump(out, open(os.path.join(HERE, "..", "build", "gorseller.pkl"), "wb"))
        print(len(out), "doku")
if __name__ == "__main__": main("--denetle" in sys.argv)
