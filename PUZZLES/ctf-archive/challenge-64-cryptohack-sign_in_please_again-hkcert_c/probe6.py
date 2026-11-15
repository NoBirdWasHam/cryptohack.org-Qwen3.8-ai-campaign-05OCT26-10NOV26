import socket, base64, hashlib, time, sys
def grab(tries=40):
    for i in range(tries):
        s=None
        try:
            s=socket.create_connection(("archive.cryptohack.org",60192),timeout=8); s.settimeout(8)
            b=b""
            while b"\n" not in b:
                d=s.recv(4096)
                if not d: break
                b+=d
            if b.endswith(b"\n") and b[:4]==b"\xf0\x9f\x94\xa7":
                print("got greeting on try",i,flush=True); return s,b
        except Exception: pass
        if s: s.close()
        time.sleep(0.3)
    raise RuntimeError("no greeting")
def line(s):
    b=b""
    while not b.endswith(b"\n"):
        d=s.recv(4096)
        if not d: return None
        b+=d
    return b.decode(errors="replace").rstrip("\n")
s,g=grab()
chal=base64.b64decode(g.split()[1])
t0=time.time()
r=0
while True:
    rb=r.to_bytes(4,"big")
    if hashlib.sha256(chal+rb).digest().startswith(b"\x00\x00\x00"): break
    r+=1
print("pow iters",r,"%.1fs"%(time.time()-t0),flush=True)
s.sendall(base64.b64encode(rb)+b"\n")
print("after pow:",repr(line(s)),flush=True)
def spy(pbox):
    s.sendall("🕵️\n".encode())
    s.sendall((f"[{','.join(map(str,pbox))}]\n").encode())
    s.sendall(b"QUFB\n")
    o=line(s)
    if o is not None and not o.startswith("🔑"): o=line(s)
    return (o or "")[:50]
idb=list(range(21))
print("identity:",repr(spy(idb)),flush=True)
print("identity2:",repr(spy(idb)),flush=True)
print("NEG:",repr(spy(list(range(-20,1))),flush=True) if False else repr(spy(list(range(-20,1)))),flush=True)
print("DUP:",repr(spy(idb+[16,17,18,19])),flush=True)
print("MISS20:",repr(spy(list(range(20))+[0]*1)),flush=True)
s.close()
