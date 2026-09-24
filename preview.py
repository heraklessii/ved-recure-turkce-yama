import sys, numpy as np
from PIL import Image
from fontgen import *
fn,pid=sys.argv[1],int(sys.argv[2]); ttf=int(sys.argv[3]) if sys.argv[3]!='0' else None; out=sys.argv[4]
gs=GlyphSource(fn,pid,ttf)
import sys as _s
line=_s.argv[5] if len(_s.argv)>5 else "cçgğiıoösşuüCÇGĞIİOÖSŞUÜ"
ims=[]
for ch in line:
    if ord(ch) in gs.d['cmap']:
        img,g=glyph_img(gs.d,ch); m=g[1:6]; how='orig'
    else:
        img,m,how=gs.render(ch)
    ims.append((np.flipud(img),m)); print(ch,how,[round(v,1) for v in m])
# render as text using SDF threshold, aligned on baseline
pad=gs.pad; asc=max(m[3] for _,m in ims)+pad; desc=max(m[1]-m[3] for _,m in ims)+pad
H=int(asc+desc)+2; W=int(sum(m[4] for _,m in ims)+4*pad)+10
can=np.zeros((H,W),np.uint8); x=pad
for im,m in ims:
    top=int(round(asc-m[3]-pad)); left=int(round(x+m[2]-pad))
    h,w=im.shape; reg=can[top:top+h,left:left+w]; np.maximum(reg,im[:reg.shape[0],:reg.shape[1]],out=reg); x+=m[4]
sc=max(1,int(1600/W)) if W<1600 else 1
vis=(np.clip((can.astype(float)-110)/35,0,1)*255).astype(np.uint8)
Image.fromarray(np.vstack([can,vis])).resize((W*sc,2*H*sc),Image.BILINEAR).save(out)
