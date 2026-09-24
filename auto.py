import json,re
allr=json.load(open("src/all.json",encoding="utf-8"))
A=json.load(open("tr/arketip.json",encoding="utf-8"))
P=[(r"Higher chance to obtain (.+) Buffs", "{} Buff'ı edinme şansı artar"),
   (r"Probability - (.+)", "Olasılık - {}"),
   (r"<color=#00D4FF>Higher chance for (.+)-related Buffs to appear</color>", "<color=#00D4FF>{} ile ilgili Buff'ların çıkma şansı artar</color>"),
   (r"<color=#00D4FF>Higher chance to obtain (.+)-related Buffs</color>", "<color=#00D4FF>{} ile ilgili Buff'ları edinme şansı artar</color>")]
out={}; miss=set()
for k,v in allr:
    for p,t in P:
        m=re.fullmatch(p,v)
        if m:
            n=m.group(1)
            if n in A: out[k]=t.format(A[n])
            else: miss.add(n)
            break
json.dump(out,open("tr/b-auto.json","w",encoding="utf-8"),ensure_ascii=False,indent=0)
print(len(out),"otomatik; eksik ad:",miss)
# Buff names that are archetype names (optionally with +, ++, +++ suffix)
n2=0
for k,v in allr:
    if k.startswith("BuffName_"):
        m=re.fullmatch(r"(.+?)(\++)?",v)
        base,plus=m.group(1),m.group(2) or ""
        if base in A: out[k]=A[base]+plus; n2+=1
json.dump(out,open("tr/b-auto.json","w",encoding="utf-8"),ensure_ascii=False,indent=0)
print("buff adlari otomatik:",n2)
