"""Eski ve yeni İngilizce CSV farkı: eklenen / silinen / değişen anahtarlar -> build/fark.json"""
import csv, io, json, sys
def load(p):
    rows = list(csv.reader(io.StringIO(open(p, "rb").read().decode("utf-8-sig"), newline="")))
    return {r[0]: r[1] for r in rows[1:] if r}
old, new = load(sys.argv[1]), load(sys.argv[2])
add = [k for k in new if k not in old]; rem = [k for k in old if k not in new]
chg = [k for k in new if k in old and new[k] != old[k]]
json.dump({"eklenen": {k: new[k] for k in add}, "silinen": rem, "degisen": {k: [old[k], new[k]] for k in chg}},
          open("build/fark.json", "w", encoding="utf-8"), ensure_ascii=False, indent=1)
print(f"eski {len(old)}  yeni {len(new)}  eklenen {len(add)}  silinen {len(rem)}  değişen {len(chg)}")
