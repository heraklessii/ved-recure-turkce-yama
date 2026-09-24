import UnityPy, numpy as np
from tmpfa import parse
G="C:/Program Files (x86)/Steam/steamapps/common/Ved疗愈所/ved_Data/"
_envs={}
def getf(fn):
    if fn not in _envs: _envs[fn]=list(UnityPy.load(G+fn).files.values())[0]
    return _envs[fn]
def load_font(fn,pid):
    f=getf(fn); raw=f.objects[pid].get_raw_data(); d=parse(raw); d['raw']=raw
    t=f.objects[d['atlasTex'][0][1]].read()
    sd=t.m_StreamData
    if sd.path:
        with open(G+sd.path,'rb') as fh: fh.seek(sd.offset); data=fh.read(sd.size)
        d['tex_loc']=(sd.path,sd.offset,sd.size)
    else:
        data=bytes(t.image_data); d['tex_loc']=None
    d['atlas']=np.frombuffer(data,np.uint8).reshape(t.m_Height,t.m_Width).copy()  # bottom-up rows
    d['gmap']={g[0]:g for g in d['glyphs']}
    d['cmap']={c[1]:c[2] for c in d['chars']}
    return d
def glyph_img(d,ch,extra=None):
    pad=d['padding'] if extra is None else extra
    g=d['gmap'][d['cmap'][ord(ch)]]
    x,y,w,h=g[6:10]
    return d['atlas'][y-pad:y+h+pad, x-pad:x+w+pad], g
