"""Ved: Recure Turkce yama uygulayici / geri alici.
Kullanim: python yama.py apply <oyun_klasoru> <yama_klasoru>
          python yama.py restore <oyun_klasoru>"""
import sys, os, struct, pickle, subprocess, json
BK="TurkceYama_yedek"

def game_running():
    try: out=subprocess.run(["tasklist","/FI","IMAGENAME eq ved.exe"],capture_output=True,text=True).stdout
    except Exception: return False
    return "ved.exe" in out.lower()

class SF:
    def __init__(s, path):
        s.path=path
        with open(path,'rb') as f: s.hdr=f.read(48); 
        s.version=struct.unpack_from(">I",s.hdr,8)[0]; assert s.version>=22
        s.meta_size,s.file_size,s.data_offset=struct.unpack_from(">IQQ",s.hdr,20)
        s.e='<' if s.hdr[16]==0 else '>'
        with open(path,'rb') as f: f.seek(48); s.meta=f.read(s.meta_size)
    def entry(s,pid):
        # object entry: pathID(q) byteStart(q) byteSize(I) typeID(i), 4-byte aligned within metadata
        pat=struct.pack(s.e+"q",pid); i=-1
        while True:
            i=s.meta.find(pat,i+1)
            if i<0: raise KeyError(pid)
            if (48+i)%4: continue
            bs,sz=struct.unpack_from(s.e+"qI",s.meta,i+8)
            if 0<=bs<=s.file_size and 0<sz<2**31 and s.data_offset+bs+sz<=s.file_size: return 48+i,bs,sz

def restore(game):
    data=os.path.join(game,"ved_Data"); bkdir=os.path.join(game,BK); man=os.path.join(bkdir,"manifest.pkl")
    if not os.path.exists(man): print("Yedek bulunamadi, geri alinacak bir sey yok."); return
    M=pickle.load(open(man,'rb'))
    for fn,info in M['assets'].items():
        p=os.path.join(data,fn)
        with open(p,'r+b') as f:
            for off,orig in info['entries']: f.seek(off); f.write(orig)
            f.seek(0); f.write(info['hdr']); f.truncate(info['size'])
        print("geri alindi:",fn)
    for fn,regions in M['ress'].items():
        with open(os.path.join(data,fn),'r+b') as f:
            for off,orig in regions: f.seek(off); f.write(orig)
        print("geri alindi:",fn)
    os.remove(man); print("Orijinal dosyalar geri yuklendi.")

def apply(game, patchdir):
    data=os.path.join(game,"ved_Data"); bkdir=os.path.join(game,BK); os.makedirs(bkdir,exist_ok=True)
    restore(game)  # always start from pristine files
    objs=pickle.load(open(os.path.join(patchdir,"objects.pkl"),'rb'))   # {file: {pid: bytes}}
    ress=pickle.load(open(os.path.join(patchdir,"ress.pkl"),'rb'))      # {file: [(offset, bytes)]}
    M={'assets':{},'ress':{}}
    # backup everything first, then write
    for fn,new in objs.items():
        p=os.path.join(data,fn); sf=SF(p)
        assert os.path.getsize(p)==sf.file_size, fn+": dosya boyutu tutarsiz"
        ents=[]
        for pid in new:
            off,bs,sz=sf.entry(pid)
            with open(p,'rb') as f: f.seek(off); ents.append((off,f.read(20)))
        M['assets'][fn]={'hdr':sf.hdr,'size':sf.file_size,'entries':ents}
    for fn,writes in ress.items():
        regs=[]
        with open(os.path.join(data,fn),'rb') as f:
            for off,b in writes: f.seek(off); regs.append((off,f.read(len(b))))
        M['ress'][fn]=regs
    pickle.dump(M,open(os.path.join(bkdir,"manifest.pkl"),'wb'))
    for fn,new in objs.items():
        p=os.path.join(data,fn); sf=SF(p)
        with open(p,'r+b') as f:
            f.seek(0,2); end=f.tell()
            for pid,raw in new.items():
                off,bs,sz=sf.entry(pid)
                pos=end+(-end)%16; f.seek(end); f.write(b'\0'*(pos-end)); f.write(raw); end=pos+len(raw)
                f.seek(off+8); f.write(struct.pack(sf.e+"qI",pos-sf.data_offset,len(raw)))
            f.seek(end); f.write(b'\0'*((-end)%16)); end+=(-end)%16
            f.seek(24); f.write(struct.pack(">Q",end))
        print("yamalandi:",fn,len(new),"nesne")
    for fn,writes in ress.items():
        with open(os.path.join(data,fn),'r+b') as f:
            for off,b in writes: f.seek(off); f.write(b)
        print("yamalandi:",fn,len(writes),"bolge")
    print("Turkce yama uygulandi.")

if __name__=="__main__":
    if game_running(): sys.exit("Oyun acik! Lutfen once oyunu kapatin.")
    cmd=sys.argv[1]
    if cmd=="apply": apply(sys.argv[2],sys.argv[3])
    elif cmd=="restore": restore(sys.argv[2])
