import struct, pickle, numpy as np
from fontgen import GlyphSource, TR, EXTRA_COMP
# (dosya, TMP font adı, TTF font adı veya None) — pathID'ler güncellemelerde kaydığı için ada göre bulunur
FONT_ADLARI = [("sharedassets0.assets", "VedEnglish", None),             # ana İngilizce arayüz/diyalog fontu
               ("resources.assets", "VedAllLanguage", None),
               ("sharedassets0.assets", "BahnschriftStaticBold SDF_outlineGrery", "BahnschriftStaticBold"),
               *[("resources.assets", "BarlowBlackItalicEnglish_" + k, "BarlowBlackItalic") for k in ("outlineblack", "outlineblackA0", "outlinegreyBold", "outlinewhite")],
               *[("resources.assets", "BahnschriftStaticBold SDF" + k, "BahnschriftStaticBold") for k in ("", "_outline", "_outlineLittle", "_outlineWhite")],
               *[("resources.assets", "AntonSDF" + k, "Anton") for k in ("", "_outline", "_soft")],
               *[("resources.assets", "ArchivoBlackSDF" + k, "Archivo-Black") for k in ("", "_outline")]]
def font_listesi():
    from nesne_bul import ada_gore, dosya
    ttf = {o.read().m_Name: pid for pid, o in dosya("resources.assets").objects.items() if o.type.name == "Font"}
    ids = {}
    for fn in {f for f, _, _ in FONT_ADLARI}:
        ids[fn] = ada_gore(fn, [a for f, a, _ in FONT_ADLARI if f == fn])
    return [(fn, ids[fn][ad], ttf[t] if t else None) for fn, ad, t in FONT_ADLARI]
def pack(atlas, free, sizes):
    """place boxes (h,w) (+1px margin) into empty atlas space found with an integral image"""
    H,W=atlas.shape; occ=(atlas>0).astype(np.int32); placed=[]
    for (h,w) in sizes:
        ii=np.zeros((H+1,W+1),np.int64); ii[1:,1:]=occ.cumsum(0).cumsum(1)
        hh,ww=h+2,w+2
        s_=ii[hh:,ww:]-ii[:-hh,ww:]-ii[hh:,:-ww]+ii[:-hh,:-ww]
        ys,xs=np.nonzero(s_==0)
        assert len(ys), "no space"
        k=np.lexsort((xs,-ys))[0]  # prefer top rows (usually empty tail of atlas)
        y,x=ys[k]+1,xs[k]+1
        occ[y-1:y+h+1, x-1:x+w+1]=1; placed.append((x,y))
    return placed
if __name__ != "__main__": raise ImportError("build_fonts.py doğrudan çalıştırılmalı")
plan=[]
import os
_G="C:/Program Files (x86)/Steam/steamapps/common/Ved疗愈所/"
if os.path.exists(_G+"TurkceYama_yedek/yedek.bin") or os.path.exists(_G+"TurkceYama_yedek/manifest.pkl"):
    raise SystemExit("HATA: Oyun yamalı görünüyor. Önce Yamayi_Kaldir.bat ile orijinale döndürün.")
FONTS = font_listesi()
for fn, pid, ttf in FONTS: print("font:", fn, pid, "ttf:", ttf)
for fn,pid,ttf in FONTS:
    gs=GlyphSource(fn,pid,ttf); d=gs.d; pad=gs.pad; raw=d['raw']
    todo=[ch for ch in TR+(EXTRA_COMP if gs.face is None else '') if ord(ch) not in d['cmap']]
    spots=None
    for f in (1.0,0.85,0.7,0.6,0.5,0.4,0.33,0.28,0.24,0.2,0.17,0.15):
        if f<1 and not all(gs.has_ttf(ch) for ch in todo): break
        gs.set_scale(f)
        rendered=[(ch,)+gs.render(ch) for ch in todo]
        try: spots=pack(d['atlas'], d['free'], [r[1].shape for r in rendered]); break
        except AssertionError: continue
    if spots is None and all(gs.has_ttf(ch) for ch in todo):
        # tüm set sığmıyor: öncelik sırasıyla harfleri tek tek, sığabildiği kadar ekle
        order=[c for c in "İÜÖŞÇĞıüöşçğ" if c in todo]
        for f in (0.4,0.33,0.28,0.24,0.2,0.17,0.15):
            gs.set_scale(f)
            cand=[(ch,)+gs.render(ch) for ch in order]
            chosen=[]; 
            for c in cand:
                try: sp=pack(d['atlas'], d['free'], [x[1].shape for x in chosen+[c]]); chosen.append(c)
                except AssertionError: pass
            if chosen:
                rendered=chosen; todo=[c[0] for c in chosen]
                spots=pack(d['atlas'], d['free'], [x[1].shape for x in chosen]); break
    if spots is None:
        print(f"ATLANDI (yer yok): {d['name']}"); continue
    next_idx=max(max(d['gmap']), 0)+1
    gl=b''; cl=b''; writes=[]; hows=set()
    W=d['atlas'].shape[1]
    for (ch,img,m,how),(x,y) in zip(rendered,spots):
        gi=next_idx; next_idx+=1; hows.add(how)
        h,w=img.shape
        rect=(x+pad,y+pad,w-2*pad,h-2*pad)
        gl+=struct.pack("<I5f4ifii",gi,*m,*rect,1.0,0,0)  # ölçek her zaman 1 (bkz. fontgen.render)
        cl+=struct.pack("<iIIf",1,ord(ch),gi,1.0)
        for r in range(h): writes.append(((y+r)*W+x, img[r].tobytes()))
    ng=len(d['glyphs']); nc=len(d['chars'])
    new=bytearray(raw[:d['glyph_pos']]); new+=struct.pack("<i",ng+len(todo))
    new+=raw[d['glyph_pos']+4:d['char_pos']]+gl
    new+=struct.pack("<i",nc+len(todo))+raw[d['char_pos']+4:d['char_end']]+cl+raw[d['char_end']:]
    plan.append(dict(file=fn,pid=pid,name=d['name'],newraw=bytes(new),tex=d['tex_loc'],writes=writes))
    print(f"{d['name']:45} +{len(todo)} ({''.join(todo)}) glyphs via {hows} scale={f} tex={d['tex_loc'][0]}@{d['tex_loc'][1]}")
# zorunlu güvenlik kontrolleri: taşma ve çakışma olmamalı
import collections
by=collections.defaultdict(list)
for p in plan:
    base,size=p['tex'][1],p['tex'][2]
    for o,b in p['writes']:
        assert 0<=o and o+len(b)<=size, "TASMA "+p['name']
        by[p['tex'][0]].append((base+o,base+o+len(b)))
for fn,L in by.items():
    L.sort()
    for a,b in zip(L,L[1:]): assert b[0]>=a[1], "CAKISMA "+fn
print("guvenlik kontrolu: OK")
pickle.dump(plan,open("build/fonts_plan.pkl","wb"))
