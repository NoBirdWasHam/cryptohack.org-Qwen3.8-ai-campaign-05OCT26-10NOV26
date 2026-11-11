import socket, base64, hashlib, time
t0=time.time()
s=socket.create_connection(("archive.cryptohack.org",60192),timeout=60)
s.settimeout(60)
print("connected", time.time()-t0)
b=b""
while b"\n" not in b:
    d=s.recv(4096)
    if not d: print("EOF"); break
    b+=d
    print("chunk t=%.1f"%(time.time()-t0), repr(d[:100]))
print("full:",repr(b))
s.close()
