"""Sahnelere/prefablara gömülü (CSV dışı) sabit metinleri değiştirir.
Çıktı: build/sabit_metin.pkl  ->  {dosya: {pathID: yeni_ham_veri}}
Oyun ORİJİNAL hâldeyken çalıştırılmalıdır."""
import UnityPy, struct, pickle, os

G = "C:/Program Files (x86)/Steam/steamapps/common/Ved疗愈所/"
D = G + "ved_Data/"

DOSYALAR = ["level0", "level1", "level2", "resources.assets"]
# (eski, yeni, beklenen nesne sayısı) — nesneler pathID yerine içerikleriyle bulunur (nesne_bul.py);
# sayı tutmazsa betik durur (oyun güncellemesinde sahne yapısı değişmiş olabilir, elle kontrol edin).
DEGISIKLIKLER = [
    ("NOW LOADING", "HAZIRLANIYOR", 10),   # yükleme ekranı; kontur fontunda Ü/İ'ye yer yok -> ASCII harfli kelime
    ("Languages", "Dil", 5),               # ana menü dil etiketi
    ("English", "Türkçe", 5),              # dil seçicilerde görünen ad (seçim sıraya göre çalışır)
    ("PROPERTY", "ÖZELLİK", 8),            # karakter/ekipman ekranı başlıkları (ArchivoBlackSDF)
    ("WEAPON", "SİLAH", 8),
    ("< EQUIP", "< EKİPMAN", 8),
    ("EQUIP >", "EKİPMAN >", 12),
]
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
        raise SystemExit("HATA: Oyun yamalı görünüyor. Önce yamayı kaldırın.")
    from nesne_bul import dizgi_iceren, dosya
    bul = {fn: dizgi_iceren(fn, [e for e, _, _ in DEGISIKLIKLER]) for fn in DOSYALAR}
    out = {}
    for old, new, beklenen in DEGISIKLIKLER:
        n = sum(len(bul[fn][old]) for fn in DOSYALAR)
        assert n == beklenen, f"'{old}': {n} nesne bulundu, {beklenen} bekleniyordu"
        for fn in DOSYALAR:
            for pid in bul[fn][old]:
                raw = out.get(fn, {}).get(pid) or dosya(fn).objects[pid].get_raw_data()
                out.setdefault(fn, {})[pid] = replace_lp(raw, old, new)
                print(f"{fn:18} {pid:8} {old!r} -> {new!r}")
    pickle.dump(out, open("build/sabit_metin.pkl", "wb"))
    print(sum(len(v) for v in out.values()), "nesne")
