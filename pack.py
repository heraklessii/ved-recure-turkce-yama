"""patch/objects.pkl + patch/ress.pkl + ORİJİNAL (yamasız) oyun dosyaları -> paket/veri/turkce.yama"""
import pickle, struct, os, sys, zlib
GAME = sys.argv[1] if len(sys.argv) > 1 else "C:/Program Files (x86)/Steam/steamapps/common/Ved疗愈所"
OUT = sys.argv[2] if len(sys.argv) > 2 else "../paket/VedRecure_TurkceYama/veri/turkce.yama"
objs = pickle.load(open("patch/objects.pkl", "rb"))
ress = pickle.load(open("patch/ress.pkl", "rb"))
from yama import SF
import UnityPy
data = os.path.join(GAME, "ved_Data")
def s(x): b = x.encode("utf-8"); return struct.pack("<H", len(b)) + b
out = bytearray(b"VEDTR" + bytes([2]))   # sürüm 2: .resS bölgeleri için orijinal CRC32
out += struct.pack("<I", len(objs))
for fn, new in objs.items():
    p = os.path.join(data, fn); sf = SF(p)
    assert os.path.getsize(p) == sf.file_size, fn + " yamalı görünüyor; önce orijinale döndürün"
    out += s(fn) + struct.pack("<Q", sf.file_size) + sf.hdr + struct.pack("<I", len(new))
    uf = list(UnityPy.load(p).files.values())[0]
    with open(p, "rb") as fh:
        for pid, raw in new.items():
            o = uf.objects[pid]
            pat = struct.pack(sf.e + "qqI", pid, o.byte_start - sf.data_offset, o.byte_size)
            i = sf.meta.find(pat)
            assert i >= 0 and sf.meta.find(pat, i + 1) < 0, f"nesne kaydı benzersiz bulunamadı: {fn} {pid}"
            off = 48 + i
            fh.seek(off); orig20 = fh.read(20)
            out += struct.pack("<Q", off) + orig20 + struct.pack("<I", len(raw)) + raw
out += struct.pack("<I", len(ress))
for fn, writes in ress.items():
    # bölgelerin ORİJİNAL baytlarının CRC32'si: kurulum programı dosyanın gerçekten orijinal olduğunu buna göre denetler
    crc = 0
    with open(os.path.join(data, fn), "rb") as fh:
        for off, b in writes:
            fh.seek(off); crc = zlib.crc32(fh.read(len(b)), crc)
    out += s(fn) + struct.pack("<Q", os.path.getsize(os.path.join(data, fn))) + struct.pack("<II", crc & 0xFFFFFFFF, len(writes))
    for off, b in writes:
        out += struct.pack("<QI", off, len(b)) + b
os.makedirs(os.path.dirname(OUT), exist_ok=True)
open(OUT, "wb").write(out)
print(OUT, len(out), "bayt")
