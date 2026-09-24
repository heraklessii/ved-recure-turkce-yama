import csv, io, json, collections
t=open("build/en_original.csv","rb").read().decode("utf-8-sig")
rows=list(csv.reader(io.StringIO(t,newline='')))
print("header",rows[0], "rows",len(rows)-1)
ent=[(r[0],r[1],r[2:]) for r in rows[1:]]
json.dump([[k,v] for k,v,_ in ent],open("src/all.json","w",encoding="utf-8"),ensure_ascii=False)
# batches of ~12000 chars in file order
b=[];cur=[];n=0
for k,v,_ in ent:
    cur.append([k,v]); n+=len(v)+len(k)
    if n>12000: b.append(cur); cur=[]; n=0
if cur: b.append(cur)
for i,x in enumerate(b): json.dump(x,open(f"src/b{i:03}.json","w",encoding="utf-8"),ensure_ascii=False,indent=0)
print("batches",len(b))
print(collections.Counter(len(r) for r in rows))
print([r for r in rows if len(r)==6][:3])
