import struct
from mbhead import mb_header
class R:
    def __init__(s,b,p=0): s.b=b; s.p=p
    def i(s): v=struct.unpack_from("<i",s.b,s.p)[0]; s.p+=4; return v
    def u(s): v=struct.unpack_from("<I",s.b,s.p)[0]; s.p+=4; return v
    def f(s): v=struct.unpack_from("<f",s.b,s.p)[0]; s.p+=4; return v
    def q(s): v=struct.unpack_from("<q",s.b,s.p)[0]; s.p+=8; return v
    def s(s_):
        n=s_.i(); v=s_.b[s_.p:s_.p+n].decode('utf-8','replace'); s_.p+=n; s_.al(); return v
    def al(s): s.p+=(-s.p)%4
    def pptr(s): return (s.i(), s.q())
    def bool(s): v=s.b[s.p]; s.p+=1; s.al(); return v
def parse(raw):
    d={}; _,d['name'],p=mb_header(raw); r=R(raw,p)
    d['hashCode']=r.i(); d['material']=r.pptr(); d['matHash']=r.i()
    d['version']=r.s(); d['guid']=r.s(); d['srcFont']=r.pptr(); d['mode']=r.i()
    d['face_pos']=r.p
    d['faceIndex']=r.i(); d['family']=r.s(); d['style']=r.s(); d['pointSize']=r.i(); d['scale']=r.f(); d['upem']=r.i()
    d['faceFloats']=[r.f() for _ in range(15)]  # lineHeight..tabWidth
    d['glyph_pos']=r.p; n=r.i(); d['glyphs']=[]
    for _ in range(n):
        g=struct.unpack_from("<I5f4i f i i",raw,r.p); r.p+=52; d['glyphs'].append(g)
    d['char_pos']=r.p; n=r.i(); d['chars']=[]
    for _ in range(n):
        c=struct.unpack_from("<iIIf",raw,r.p); r.p+=16; d['chars'].append(c)
    d['char_end']=r.p
    n=r.i(); d['atlasTex']=[r.pptr() for _ in range(n)]
    d['atlasIdx']=r.i(); d['multi']=r.bool(); d['clearDyn']=r.bool()
    n=r.i(); d['used']=[struct.unpack_from("<4i",raw,r.p+16*k) for k in range(n)]; r.p+=16*n
    n=r.i(); d['free']=[struct.unpack_from("<4i",raw,r.p+16*k) for k in range(n)]; r.p+=16*n
    d['legacy_name']=r.s(); leg=[r.f(),r.f(),r.i()]+[r.f() for _ in range(17)]
    d['legacy']=leg
    d['atlasPPtr']=r.pptr(); d['atlasW']=r.i(); d['atlasH']=r.i(); d['padding']=r.i(); d['renderMode']=r.i()
    d['after_pos']=r.p
    return d
