import socket, re, sys
def conn():
    s=socket.create_connection(("archive.cryptohack.org",33824),timeout=45)
    f=s.makefile("rwb",buffering=0)
    def rd():
        d=b""
        while True:
            ch=f.read(1)
            if not ch: return d
            d+=ch
            if d.endswith((b"> ",b"friends? ",b"friends... ",b"! ",b"\n\n")) or (d.endswith(b"\n") and not d.endswith(b">\n")):
                return d
    return s,f,rd
