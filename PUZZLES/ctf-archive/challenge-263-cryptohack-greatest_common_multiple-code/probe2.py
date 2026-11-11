import socket, re, hashlib, time
def clean(b): return re.sub(rb'\x1b\[[0-9;]*m', b'', b)
def conn():
    s = socket.create_connection(("archive.cryptohack.org", 2762), timeout=20)
    def recv_avail(t=3):
        s.settimeout(t); buf=b""
        try:
            while True:
                d=s.recv(4096)
                if not d: break
                buf+=d
        except Exception: pass
        return buf
    buf=b""
    while b"hexdigest()" not in buf: buf+=recv_avail(5)
    m=re.search(rb'hexdigest\(\) = ([0-9a-f]{32})', buf)
    salt=re.search(rb"md5\(str\(n\)\.encode\(\) \+ b'([^']+)'", buf).group(1)
    h=m.group(1).decode(); n=0
    while hashlib.md5(str(n).encode()+salt).hexdigest()!=h: n+=1
    s.sendall((str(n)+"\n").encode()); time.sleep(.5); recv_avail(2)
    return s, recv_avail
s, rv = conn()
for cmd in [b"digest\n", b"help\n", b"u2\n", b"tag\n", b"\n"]:
    s.sendall(cmd)
    print(cmd, "->", clean(rv(2)), flush=True)
    if b"> " not in clean(rv(0)) : pass
s.sendall(b"0"*32+b"\n")
print("FINAL:", clean(rv(4)), flush=True)
s.close()
