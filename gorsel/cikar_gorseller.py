"""Kendi oyun kopyanızdan, görsel betiklerinin ihtiyaç duyduğu orijinal dokuları gorsel/en/ klasörüne PNG olarak çıkarır.
Oyun ORİJİNAL (yamasız) hâldeyken çalıştırın."""
import os, re, sys, UnityPy
G = sys.argv[1] if len(sys.argv) > 1 else "C:/Program Files (x86)/Steam/steamapps/common/Ved疗愈所"
HERE = os.path.dirname(os.path.abspath(__file__)); OUT = os.path.join(HERE, "en"); os.makedirs(OUT, exist_ok=True)
# İngilizce dokular + maske için diğer dil sürümleri (buffTitle, Invitation) + ana menü dil başlığı
PAT = re.compile(r"_English$|^buffTitle_\d+_(Chinese|ChineseTraditional|Japanese)$|^Invitation_Chinese$|^LanguageTest$")
for fn in ("resources.assets", "sharedassets0.assets"):
    sf = list(UnityPy.load(os.path.join(G, "ved_Data", fn)).files.values())[0]
    for o in sf.objects.values():
        if o.type.name != "Texture2D": continue
        t = o.read()
        if PAT.search(t.m_Name) and "Atlas" not in t.m_Name:
            t.image.save(os.path.join(OUT, t.m_Name + ".png")); print(t.m_Name)
# basliklar.py'nin kullandığı oyun fontları (Anton, Archivo Black) -> gorsel/*.ttf
sf = list(UnityPy.load(os.path.join(G, "ved_Data", "resources.assets")).files.values())[0]
for pid in (19878, 19889):
    t = sf.objects[pid].read_typetree()
    open(os.path.join(HERE, t["m_Name"] + ".ttf"), "wb").write(bytes(t["m_FontData"])); print(t["m_Name"] + ".ttf")
