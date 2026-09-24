"""Dil seçicide görünen "English" adı IL2CPP metin sabitidir (global-metadata.dat).
Sabit tablosunda "English" girdisi, kullanılmayan "English (Zimbabwe)" kültür adının veri alanına yazılan "Türkçe"yi gösterecek
şekilde değiştirilir; Zimbabwe girdisi de eski "English" verisini gösterir. Dosya boyutu değişmez.
Çıktı: build/metadata.pkl -> [(göreli yol, ofset, bayt)]"""
import struct, pickle, os
G = "C:/Program Files (x86)/Steam/steamapps/common/Ved疗愈所/ved_Data/"
REL = "il2cpp_data/Metadata/global-metadata.dat"
b = open(G + REL, "rb").read()
assert struct.unpack_from("<I", b, 0)[0] == 0xFAB11BAF and struct.unpack_from("<I", b, 4)[0] == 29
LO, LC, DO, DC = struct.unpack_from("<4I", b, 8)
lits = [struct.unpack_from("<2I", b, LO + 8 * i) for i in range(LC // 8)]
def find(s):
    e = s.encode()
    r = [i for i, (n, d) in enumerate(lits) if n == len(e) and b[DO + d:DO + d + n] == e]
    assert len(r) == 1, (s, r); return r[0]
ie, iz = find("English"), find("English (Zimbabwe)")
new = "Türkçe".encode()
assert len(new) <= lits[iz][0]
out = [(REL, DO + lits[iz][1], new),
       (REL, LO + 8 * ie, struct.pack("<2I", len(new), lits[iz][1])),
       (REL, LO + 8 * iz, struct.pack("<2I", lits[ie][0], lits[ie][1]))]
pickle.dump(out, open("build/metadata.pkl", "wb"))
print("English #%d, Zimbabwe #%d -> %d bölge" % (ie, iz, len(out)))
