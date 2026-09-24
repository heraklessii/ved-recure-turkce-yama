"""build/fonts_plan.pkl + build/tr.csv -> patch/objects.pkl, patch/ress.pkl"""
import pickle, struct, os, sys
os.makedirs("patch",exist_ok=True)
plan=pickle.load(open("build/fonts_plan.pkl","rb"))
objs={}; ress={}
for p in plan:
    objs.setdefault(p['file'],{})[p['pid']]=p['newraw']
    fn,base,size=p['tex']
    # merge consecutive row writes into (offset,bytes)
    ress.setdefault(fn,[]).extend((base+o,b) for o,b in p['writes'])
csv=open(sys.argv[1] if len(sys.argv)>1 else "build/tr.csv","rb").read()
def s(b): return struct.pack("<i",len(b))+b+b'\0'*((-len(b))%4)
objs.setdefault("resources.assets",{})[13066]=s(b"translation")+s(csv)
if os.path.exists("build/sabit_metin.pkl"):
    for fn,new in pickle.load(open("build/sabit_metin.pkl","rb")).items():
        for pid,raw in new.items():
            assert pid not in objs.get(fn,{}), (fn,pid)
            objs.setdefault(fn,{})[pid]=raw
# yerinde yazılan diğer bölgeler: Türkçeleştirilmiş dokular ve dil adı (IL2CPP metin sabiti)
for extra in ("build/gorseller.pkl", "build/metadata.pkl"):
    if os.path.exists(extra):
        for fn, off, b in pickle.load(open(extra, "rb")):
            ress.setdefault(fn, []).append((off, b))
for fn, w in ress.items():   # hiçbir bölge üst üste binmemeli
    w.sort(key=lambda t: t[0])
    for (o1, b1), (o2, b2) in zip(w, w[1:]): assert o1 + len(b1) <= o2, ("CAKISMA", fn, o1, o2)
pickle.dump(objs,open("patch/objects.pkl","wb")); pickle.dump(ress,open("patch/ress.pkl","wb"))
print({k:len(v) for k,v in objs.items()}, {k:len(v) for k,v in ress.items()})
