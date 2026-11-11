import socket, re, hashlib, time
def clean(b): return re.sub(rb'\x1b\[[0-9;]*m', b'', b)
def conn():
    s = socket.create_connection(("archive.cryptohack.org", 2762), timeout=20)
    def rv(t=2):
        s.settimeout(t); buf=b""
        try:
            while True:
                d=s.recv(4096)
                if not d: break
                buf+=d
        except Exception: pass
        return buf
    buf=b""
    while b"hexdigest()" not in buf: buf+=rv(5)
    m=re.search(rb'hexdigest\(\) = ([0-9a-f]{32})', buf)
    salt=re.search(rb"md5\(str\(n\)\.encode\(\) \+ b'([^']+)'", buf).group(1)
    h=m.group(1).decode(); n=0
    while hashlib.md5(str(n).encode()+salt).hexdigest()!=h: n+=1
    s.sendall((str(n)+"\n").encode()); time.sleep(.3); rv(1)
    return s, rv
def gettag(s, rv, cmd=b"tag\n"):
    s.sendall(cmd); out=clean(rv(2))
    mm=re.search(rb'tag: ([0-9a-f]{32})', out)
    return mm.group(1).decode() if mm else out
for i in range(2):
    s1,rv1 = conn()
    tA = gettag(s1,rv1)
    tB = gettag(s1,rv1)   # same state twice -> same?
    time.sleep(2)
    s2,rv2 = conn()
    tC = gettag(s2,rv2)
    print(i, "conn1:", tA, "conn1b:", tB, "conn2:", tC, "SAME" if tA==tC else "diff", flush=True)
    s1.close(); s2.close()
