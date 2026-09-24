import struct
def mb_header(raw):
    # GameObject pptr(4+8) enabled(1)+pad(3) script pptr(4+8) name
    fid, ppid = struct.unpack_from("<iq", raw, 0)
    sfid, spid = struct.unpack_from("<iq", raw, 16)
    n = struct.unpack_from("<i", raw, 28)[0]
    name = raw[32:32+n].decode("utf-8","replace")
    end = 32+n; end += (-end)%4
    return (sfid, spid), name, end
