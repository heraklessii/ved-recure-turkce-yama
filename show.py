import json, sys, glob, re
TAIL = re.compile(r'((?:\$[A-Za-z]+(?:\[[^\]]*\])+|\[\$[A-Za-z]+[^\]]*\]|\s)*)$')
done = set()
for p in glob.glob("tr/b*.json"):
    done |= set(json.load(open(p, encoding="utf-8")))
for k, v in json.load(open(f'src/b{int(sys.argv[1]):03}.json', encoding='utf-8')):
    t = TAIL.search(v).group(1)
    if k in done or (t.strip() and v.strip() == t.strip()):
        continue
    print(k + '\t' + (v[:len(v) - len(t)] if t.strip() else v))
