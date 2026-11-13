import socket
def conn(q,p,g,seed,host="archive.cryptohack.org",port=2783):
    s=socket.create_connection((host,port),timeout=40)
    f=s.makefile("rw",encoding="utf-8",errors="replace")
    def ask(sub):
        d=""
        while sub not in d:
            c=f.read(1)
            if not c: return d+"<<EOF>>"
            d+=c
        return d
    out=""
    try:
        ask("q = "); f.write(str(q)+"\n"); f.flush()
        ask("p = "); f.write(str(p)+"\n"); f.flush()
        ask("g = "); f.write(str(g)+"\n"); f.flush()
        ask("hex"); f.write(seed+"\n"); f.flush()
        s.settimeout(40)
        while True:
            c=f.read(1)
            if not c: break
            out+=c
            if "sign = " in out: break
    except Exception as e:
        out+=f"<<{type(e).__name__}>>"
    s.close()
    return out
