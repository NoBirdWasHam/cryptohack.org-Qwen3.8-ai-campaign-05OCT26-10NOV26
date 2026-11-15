import socket, base64, hashlib, time
def line(s):
    b=b""
    while not b.endswith(b"\n"):
        d=s.recv(4096)
        if not d: return None
        b+=d
    return b.decode(errors="replace").rstrip("\n")
s=socket.create_connection(("archive.cryptohack.org",60192),timeout=30); s.settimeout(25)
chal=base64.b64decode(line(s).split()[1])
for r in range(1<<28):
    rb=r.to_bytes(4,"big")
    if hashlib.sha256(chal+rb).digest().startswith(b"\x00\x00\x00"): break
s.sendall(base64.b64encode(rb)+b"\n")
print("pow ->", repr(line(s)))
def spy(pbox,salt_b64):
    s.sendall("🕵️\n".encode())
    s.sendall((f"[{','.join(map(str,pbox))}]\n").encode())
    s.sendall((salt_b64+"\n").encode())
    out=[]
    out.append(line(s))
    if out[-1] and not out[-1].startswith("🔑"): out.append(line(s))
    return out[0] if out[0] and out[0].startswith("🔑") else out[-1]
idb=list(range(21))
h1=spy(idb,"QUFB"); h2=spy(idb,"QUFB")
print("spy1:",h1); print("spy2:",h2); print("fixed-pepper:", h1==h2)
print("neg-pbox:", repr(spy(list(range(-20,1)),"QUFB")))
print("dup-pbox:", repr(spy(idb+[16,17,18,19],"QUFB"))[:70])
print("missing:", repr(spy(list(range(20)),"QUFB")))
s.close()
