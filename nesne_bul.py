"""Nesneleri pathID yerine içerikleriyle bulur (oyun güncellemelerinde pathID'ler kayabiliyor).
Dosyada uzunluk önekli UTF-8 dizgiyi arar ve onu içeren nesneyi döndürür."""
import mmap, struct, re, bisect, UnityPy
from mbhead import mb_header
D = "C:/Program Files (x86)/Steam/steamapps/common/Ved疗愈所/ved_Data/"
_sf = {}
def dosya(fn):
    if fn not in _sf: _sf[fn] = list(UnityPy.load(D + fn).files.values())[0]
    return _sf[fn]
def dizgi_iceren(fn, dizgiler, tip="MonoBehaviour"):
    """{dizgi: [pathID, ...]} — dizgiyi (uzunluk önekli) içeren, verilen tipteki nesneler"""
    enc = {s: struct.pack("<i", len(s.encode())) + s.encode() for s in dizgiler}
    rx = re.compile(b"|".join(re.escape(b) for b in enc.values()))
    geri = {b: s for s, b in enc.items()}
    with open(D + fn, "rb") as f:
        m = mmap.mmap(f.fileno(), 0, access=mmap.ACCESS_READ)
        hits = [(mt.start(), geri[mt.group()]) for mt in rx.finditer(m)]
        m.close()
    sf = dosya(fn)
    objs = sorted((o.byte_start, o.byte_size, pid, o.type.name) for pid, o in sf.objects.items())
    starts = [o[0] for o in objs]
    out = {s: [] for s in dizgiler}
    for off, s in hits:
        k = bisect.bisect_right(starts, off) - 1
        if k < 0: continue
        bs, sz, pid, tn = objs[k]
        if off < bs + sz and tn == tip and pid not in out[s]: out[s].append(pid)
    return out
def ada_gore(fn, adlar):
    """{ad: pathID} — m_Name'i tam olarak bu ad olan tek MonoBehaviour (ör. TMP_FontAsset)"""
    sf = dosya(fn); res = {}
    for ad, pids in dizgi_iceren(fn, adlar).items():
        tam = [p for p in pids if mb_header(sf.objects[p].get_raw_data())[1] == ad]
        assert len(tam) == 1, f"{fn}: '{ad}' adlı nesne {len(tam)} tane bulundu"
        res[ad] = tam[0]
    return res
