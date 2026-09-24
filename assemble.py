import csv, io, json, glob, re, collections, sys

def q(f):
    if any(c in f for c in ',"\r\n') or f != f.rstrip():
        return '"' + f.replace('"', '""') + '"'
    return f

def dump(rows):
    return "".join(",".join(q(f) for f in r) + "\r\n" for r in rows)

t = open("build/en_original.csv", "rb").read().decode("utf-8-sig")
rows = list(csv.reader(io.StringIO(t, newline='')))
tr = {}
for p in sorted(glob.glob("tr/b*.json")):
    tr.update(json.load(open(p, encoding="utf-8")))

TAIL = re.compile(r"((?:\$[A-Za-z]+(?:\[[^\]]*\])+|\[\$[A-Za-z]+[^\]]*\]|\s)*)$")
CMD = re.compile(r"\$[A-Za-z]+\[|\[\$[A-Za-z]")
en0 = {r[0]: r[1] for r in rows[1:]}
for k, v in en0.items():
    tail = TAIL.search(v).group(1)
    if k in tr:
        if tail.strip() and not CMD.search(tr[k]):
            tr[k] = tr[k].rstrip() + tail
    elif tail.strip() and v.strip() == tail.strip():
        tr[k] = v  # command-only line
TOK = re.compile(r"\{\d+\}|<[^>]*>|\$n|\$[A-Za-z]+(?:\[[^\]]*\])*|%")
en = {r[0]: r[1] for r in rows[1:]}
bad = 0
for k, v in tr.items():
    if k not in en:
        print("BILINMEYEN ANAHTAR", k); bad += 1; continue
    a = collections.Counter(TOK.findall(en[k])); b = collections.Counter(TOK.findall(v))
    if a != b:
        print("ETIKET UYUSMAZ", k, "\n  EN:", sorted((a - b).elements()), "\n  TR:", sorted((b - a).elements())); bad += 1

new = [rows[0]] + [[r[0], tr.get(r[0], r[1])] + r[2:] for r in rows[1:]]
open("build/tr.csv", "wb").write(b"\xef\xbb\xbf" + dump(new).encode("utf-8"))
print(f"cevrilen {len(tr)}/{len(rows)-1}  hata {bad}")
if bad: sys.exit(1)
