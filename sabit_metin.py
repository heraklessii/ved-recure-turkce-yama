"""Sahnelere/prefablara gömülü (CSV dışı) sabit metinleri değiştirir.
Çıktı: build/sabit_metin.pkl  ->  {dosya: {pathID: yeni_ham_veri}}
Oyun ORİJİNAL hâldeyken çalıştırılmalıdır."""
import UnityPy, struct, pickle, os

G = "C:/Program Files (x86)/Steam/steamapps/common/Ved疗愈所/"
D = G + "ved_Data/"

# (dosya, pathID, eski, yeni)
DEGISIKLIKLER = []
# Yükleme ekranı: Bahnschrift kontur fontunda Ü/İ'ye yer yok -> yalnızca ASCII harfli kelime
for fn, pid in [("level0", 453), ("level1", 253267), ("level1", 254990), ("level2", 2679),
                ("resources.assets", 1656462), ("resources.assets", 1703224), ("resources.assets", 1855535),
                ("resources.assets", 1922638), ("resources.assets", 2019272), ("resources.assets", 2020657)]:
    DEGISIKLIKLER.append((fn, pid, "NOW LOADING", "HAZIRLANIYOR"))
# Ana menüdeki dil etiketi (VedSimplifiedChinese fontu, Türkçe harf gerektirmeyen kelime)
for fn, pid in [("level0", 448), ("level1", 254649), ("resources.assets", 1853330), ("resources.assets", 1893238), ("resources.assets", 1930339)]:
    DEGISIKLIKLER.append((fn, pid, "Languages", "Dil"))
# Dil seçicilerindeki görünen ad (sıraya göre seçilir; yalnızca görüntü metni)
for fn, pid in [("level1", 292881), ("resources.assets", 1886401), ("resources.assets", 1892945),
                ("resources.assets", 1907707), ("resources.assets", 1979138)]:
    DEGISIKLIKLER.append((fn, pid, "English", "Türkçe"))

# Karakter/ekipman ekranı başlıkları (ArchivoBlackSDF; Türkçe harfler fonta eklendi)
_ARCHIVO = {
    "PROPERTY": ("ÖZELLİK", [("level1", 258842), ("level1", 258904), ("resources.assets", 1655853), ("resources.assets", 1656391),
                             ("resources.assets", 1660696), ("resources.assets", 1713930), ("resources.assets", 1738683), ("resources.assets", 1743216)]),
    "WEAPON": ("SİLAH", [("level1", 256190), ("level1", 257153), ("resources.assets", 1753750), ("resources.assets", 1779718),
                         ("resources.assets", 1808543), ("resources.assets", 1833654), ("resources.assets", 1839089), ("resources.assets", 1841851)]),
    "< EQUIP": ("< EKİPMAN", [("level1", 253640), ("level1", 254255), ("resources.assets", 1968493), ("resources.assets", 1968638),
                              ("resources.assets", 1998376), ("resources.assets", 1998679), ("resources.assets", 2000484), ("resources.assets", 2021130)]),
    "EQUIP >": ("EKİPMAN >", [("level1", 254145), ("level1", 256470), ("level1", 258915), ("resources.assets", 1661341),
                              ("resources.assets", 1663407), ("resources.assets", 1711663), ("resources.assets", 1738026),
                              ("resources.assets", 1759230), ("resources.assets", 1782363), ("resources.assets", 1812609),
                              ("resources.assets", 1967185), ("resources.assets", 2006077)]),
}
for _old, (_new, _lst) in _ARCHIVO.items():
    for fn, pid in _lst:
        DEGISIKLIKLER.append((fn, pid, _old, _new))


def lp(s):
    b = s.encode("utf-8")
    return struct.pack("<i", len(b)) + b


def replace_lp(raw, old, new):
    """Uzunluk önekli + 4 bayt hizalı bir Unity string alanını değiştirir."""
    o = lp(old)
    i = raw.find(o)
    assert i >= 0 and raw.find(o, i + 1) < 0, f"'{old}' bulunamadı ya da birden fazla"
    end = i + len(o); pad_old = (-end) % 4
    assert raw[end:end + pad_old] == b"\0" * pad_old
    n = lp(new); pad_new = (-(i + len(n))) % 4
    return raw[:i] + n + b"\0" * pad_new + raw[end + pad_old:]


if __name__ == "__main__":
    if os.path.exists(G + "TurkceYama_yedek/yedek.bin"):
        raise SystemExit("HATA: Oyun yamalı görünüyor. Önce Yamayi_Kaldir.bat ile orijinale döndürün.")
    out = {}; cache = {}
    for fn, pid, old, new in DEGISIKLIKLER:
        if fn not in cache:
            cache[fn] = list(UnityPy.load(D + fn).files.values())[0]
        raw = out.get(fn, {}).get(pid) or cache[fn].objects[pid].get_raw_data()
        out.setdefault(fn, {})[pid] = replace_lp(raw, old, new)
        print(f"{fn:18} {pid:8} {old!r} -> {new!r}")
    pickle.dump(out, open("build/sabit_metin.pkl", "wb"))
    print(sum(len(v) for v in out.values()), "nesne")
