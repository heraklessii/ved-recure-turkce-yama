import numpy as np, io, struct
from scipy import ndimage
from PIL import Image
import freetype
from atlas import load_font, glyph_img, getf
TR = "çğıöşüÇĞİÖŞÜ"
EXTRA_COMP = "âîû"   # yalnızca kompozisyonla üretilen fontlara (VedEnglish/VedAllLanguage) eklenir

class Piece:
    """hi-res bool mask (bottom-up) with pen-space position of its bottom-left corner in hi-res px"""
    def __init__(s, m, x0, y0):
        x0=int(round(x0)); y0=int(round(y0))
        ys,xs=np.nonzero(m)
        s.m=m[ys.min():ys.max()+1, xs.min():xs.max()+1]; s.x0=x0+xs.min(); s.y0=y0+ys.min()
    def bbox(s):
        ys,xs=np.nonzero(s.m)
        return s.x0+xs.min(), s.y0+ys.min(), s.x0+xs.max()+1, s.y0+ys.max()+1  # l,b,r,t
    def moved(s,dx,dy): return Piece(s.m, s.x0+dx, s.y0+dy)
    def scaled(s,f):
        l,b,r,t=s.bbox(); m=s.m[b-s.y0:t-s.y0, l-s.x0:r-s.x0]
        h,w=m.shape; nw,nh=max(1,round(w*f)),max(1,round(h*f))
        m2=np.asarray(Image.fromarray(m.astype(np.uint8)*255).resize((nw,nh),Image.BILINEAR))>127
        cx,cy=(l+r)/2,(b+t)/2
        return Piece(m2, cx-nw/2, cy-nh/2)

class GlyphSource:
    def __init__(s, fn, pid, ttf_pid=None):
        s.d=load_font(fn,pid); s.pad=s.d['padding']
        s.S = 8 if s.d['pointSize']<150 else 2
        s.k = 1/(2*(s.pad+1))
        s.face=None
        if ttf_pid:
            t=getf("resources.assets").objects[ttf_pid].read_typetree()
            s.face=freetype.Face(io.BytesIO(bytes(t["m_FontData"])))
            s.face.set_char_size(int(s.d['pointSize']*s.S*64))
    def atlas_piece(s,ch):
        img,g=glyph_img(s.d,ch); S=s.S; pad=s.pad
        im=Image.fromarray(img.astype(np.float32),mode='F').resize((img.shape[1]*S,img.shape[0]*S),Image.BILINEAR)
        m=np.asarray(im)>127.5
        w,h,bx,by,adv=g[1:6]
        return Piece(m,(bx-pad)*S,(by-h-pad)*S), adv
    def ttf_piece(s,ch):
        f=s.face; f.load_char(ch, freetype.FT_LOAD_RENDER|freetype.FT_LOAD_NO_HINTING)
        gs=f.glyph; bm=gs.bitmap
        a=np.array(bm.buffer,np.uint8).reshape(bm.rows,bm.pitch)[:, :bm.width]
        m=np.flipud(a>127)
        return Piece(m, gs.bitmap_left, gs.bitmap_top-bm.rows), gs.advance.x/64/s.S
    def has_ttf(s,ch): return s.face is not None and s.face.get_char_index(ch)!=0

    # ---- composition helpers ----
    def parts(s):
        if hasattr(s,'_parts'): return s._parts
        ip,_=s.atlas_piece('i'); lab,n=ndimage.label(ip.m)
        comps=[]
        for k in range(1,n+1):
            ys,xs=np.nonzero(lab==k); comps.append((ys.min(),k,len(ys)))
        comps=[c for c in comps if c[2]>20]
        comps.sort(); stem_k=comps[0][1]; dot_k=comps[-1][1]
        dot=Piece(lab==dot_k, ip.x0, ip.y0); stem=Piece(lab==stem_k, ip.x0, ip.y0)
        gap=dot.bbox()[1]-stem.bbox()[3]
        cp,_=s.atlas_piece(','); lab,n=ndimage.label(cp.m)
        big=max(range(1,n+1),key=lambda k:(lab==k).sum()); comma=Piece(lab==big,cp.x0,cp.y0)
        sl,_,sr,_=stem.bbox()
        s._parts=dict(dot=dot,stem=stem,gap=gap,comma=comma,stroke=sr-sl)
        return s._parts
    def compose(s,ch):
        P=s.parts(); base_ch={'ı':'i','İ':'I','ö':'o','ü':'u','Ö':'O','Ü':'U','ç':'c','Ç':'C','ş':'s','Ş':'S','ğ':'g','Ğ':'G','â':'a','î':'i','û':'u'}[ch]
        if ch=='ı':
            _,adv=s.atlas_piece('i'); return [P['stem']], adv
        if ch in 'âîû':
            if ch=='î':
                base=P['stem']; _,adv=s.atlas_piece('i')
            else:
                base,adv=s.atlas_piece(base_ch)
            l,b,r,t=base.bbox(); cx=(l+r)/2
            st=P['stroke']*0.7
            dl,_,dr,_=P['dot'].bbox(); half=(dr-dl)*(0.72 if ch=='î' else 0.9); hgt=(dr-dl)*0.8
            W=int(2*half+st+4); H=int(hgt+st+4)
            yy,xx=np.mgrid[0:H,0:W].astype(float)+0.5
            ax,ay=W/2,H-2-st/2          # tepe noktası (üstte; maskede y yukarı doğru artar)
            def seg(x0,y0,x1,y1):
                dx,dy=x1-x0,y1-y0; tt=np.clip(((xx-x0)*dx+(yy-y0)*dy)/(dx*dx+dy*dy),0,1)
                return np.hypot(xx-(x0+tt*dx),yy-(y0+tt*dy))<=st/2
            m=seg(ax-half,ay-hgt,ax,ay)|seg(ax,ay,ax+half,ay-hgt)
            pl,pb,pr,pt=Piece(m,0,0).bbox()
            cap=Piece(m,0,0)
            cap=cap.moved(cx-(pl+pr)/2, t+P['gap']-pb)
            return [base,cap], adv
        base,adv=s.atlas_piece(base_ch); l,b,r,t=base.bbox(); cx=(l+r)/2
        upper=ch.isupper() or ch=='İ'
        gap=P['gap']*(0.75 if upper else 1.0)
        dot=P['dot'].scaled(0.9 if upper else 1.0)
        pieces=[base]
        def place(p,cx_,bottom):
            pl,pb,pr,pt=p.bbox(); return p.moved(cx_-(pl+pr)/2, bottom-pb)
        if ch in 'İ':
            pieces.append(place(dot,cx,t+gap))
        elif ch in 'öüÖÜ':
            dl,_,dr,_=dot.bbox(); dw=dr-dl
            off=dw*1.05 if not upper else dw*1.15
            pieces += [place(dot,cx-off,t+gap), place(dot,cx+off,t+gap)]
        elif ch in 'çÇşŞ':
            c=P['comma'].scaled(0.85); cl,cb,cr,ct=c.bbox()
            pieces.append(c.moved(cx-(cl+cr)/2, (b+P['stroke']*0.35)-ct))
        elif ch in 'ğĞ':
            st=P['stroke']*(0.8 if not upper else 0.75)
            dl,_,dr,_=P['dot'].bbox(); R=(dr-dl)*1.25 + st/2
            W=int(2*R+4); H=int(R+4)
            yy,xx=np.mgrid[0:H,0:W]; cxr=W/2; cyr=R+2   # centre above -> lower half ring
            rr=np.hypot(xx+0.5-cxr, yy+0.5-cyr)
            ring=(rr<=R)&(rr>=R-st)&(yy+0.5<=cyr)
            pieces.append(place(Piece(ring,0,0),cx,t+gap*(0.9)))
        return pieces, adv
    def make(s,ch):
        if s.has_ttf(ch):
            p,adv=s.ttf_piece(ch); return [p],adv,'ttf'
        p,adv=s.compose(ch); return p,adv,'comp'
    def set_scale(s,f):
        s.f=f
        if s.face is not None: s.face.set_char_size(int(s.d['pointSize']*f*s.S*64))
    def render(s,ch):
        f=getattr(s,'f',1.0)
        if f!=1.0: assert s.has_ttf(ch), "scaled render needs ttf"
        pieces,adv,how=s.make(ch); S=s.S; pad=s.pad
        L=min(p.bbox()[0] for p in pieces); B=min(p.bbox()[1] for p in pieces)
        R=max(p.bbox()[2] for p in pieces); T=max(p.bbox()[3] for p in pieces)
        # snap to low-res pixel grid, add padding
        # f<1: glif düşük çözünürlükte saklanır ama glyph.scale=1 kalır (TMP satır yüksekliğini glyph.scale ile büyütür).
        # Metrikler tam boyda verilir; dolgu bandındaki oran farkı görünmesin diye glif kutusu SDF yayılımı kadar genişletilir.
        e=int(np.ceil((pad+1)*f)) if f<1 else 0
        l=int(np.floor(L/S))-pad-e; b=int(np.floor(B/S))-pad-e; r=int(np.ceil(R/S))+pad+e; t=int(np.ceil(T/S))+pad+e
        canvas=np.zeros(((t-b)*S,(r-l)*S),bool)
        for p in pieces:
            y=p.y0-b*S; x=p.x0-l*S; h,w=p.m.shape
            canvas[y:y+h, x:x+w] |= p.m
        inside=ndimage.distance_transform_edt(canvas); outside=ndimage.distance_transform_edt(~canvas)
        dist=(inside-outside)/S; c=S//2
        img=np.clip(np.round((0.5+dist[c::S,c::S]/f*s.k)*255),0,255).astype(np.uint8)
        w=(r-l)-2*pad; h=(t-b)-2*pad
        metrics=(w/f,h/f,(l+pad)/f,(b+pad+h)/f,adv/f)
        return img,metrics,how
