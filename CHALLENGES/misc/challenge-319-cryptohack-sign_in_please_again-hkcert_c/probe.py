import socket, base64, hashlib, sys, time
def line(s):
    b=b""
    while not b.endswith(b"\n"):
        d=s.recv(4096)
        if not d: return b
        b+=d
    return b.decode().rstrip("\n")
s=socket.create_connection(("archive.cryptohack.org",60192),timeout=30)
s.settimeout(30)
print("greet:",line(s))   # 🔧 b64 challenge
chal=base64.b64decode(line(s).split()[1])
for r in range(1<<26):
    rb=r.to_bytes(4,"big")
    if hashlib.sha256(chal+rb).digest().startswith(b"\x00\x00\x00"): break
s.sendall(base64.b64encode(rb)+b"\n")
print("pow ok, reply:",line(s))
def spy(pbox,salt_b64):
    s.sendall("🕵️\n".encode()); print("cmd:",line(s))
    s.sendall((f"[{','.join(map(str,pbox))}]\n").encode()); print("pbox:",line(s)[:80])
    s.sendall((salt_b64+"\n").encode()); print("salt:",line(s)[:80])
    return line(s)
# 1) identity pbox
idb=list(range(21))
h1=spy(idb,"QUFB")
h2=spy(idb,"QUFB")
print("same-pepper?", h1==h2, h1[:30], h2[:30])
# 2) negative index pbox (old trick) -> expect 😡 if strict
print("neg:",spy(list(range(-20,1)),"QUFB")[:40])
# 3) duplicates allowed?
print("dup:",spy(idb+[16,17,18,19],"QUFB")[:40])
s.close()
