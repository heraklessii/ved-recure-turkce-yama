"""Kendi oyun kopyanızdan orijinal İngilizce metni çıkarır: build/en_original.csv
(Oyunun metinleri telif hakkı sahibine aittir; bu yüzden depoda bulunmaz.)
Oyun ORİJİNAL (yamasız) hâldeyken çalıştırın. Ardından: python split.py"""
import os, sys, UnityPy
G = sys.argv[1] if len(sys.argv) > 1 else "C:/Program Files (x86)/Steam/steamapps/common/Ved疗愈所"
sf = list(UnityPy.load(os.path.join(G, "ved_Data", "resources.assets")).files.values())[0]
ta = sf.objects[13066].read()          # localization/english/translation
assert ta.m_Name == "translation", ta.m_Name
data = ta.m_Script if isinstance(ta.m_Script, bytes) else ta.m_Script.encode("utf-8", "surrogateescape")
os.makedirs("build", exist_ok=True)
open("build/en_original.csv", "wb").write(data)
print("build/en_original.csv", len(data), "bayt")
