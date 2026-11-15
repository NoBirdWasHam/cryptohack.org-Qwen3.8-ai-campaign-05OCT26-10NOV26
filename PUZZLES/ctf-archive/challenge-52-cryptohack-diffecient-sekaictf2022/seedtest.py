import socket, os, mmh3

# birthday collision on murmur3-32 seed 0 among ~200k random 24-byte keys
seen = {}
X = Y = None
for i in range(400000):
    k = os.urandom(24)
    h = mmh3.hash(k, 0)
    if h in seen:
        prev = seen[h]
        if prev != k:
            X, Y = prev, k
            print("collision seed0:", h)
            break
    else:
        seen[h] = k
assert X and Y, "no collision found"
print("X=", X.hex()[:24], "... Y=", Y.hex()[:24])
print("d0 equal:", mmh3.hash(X,0)==mmh3.hash(Y,0))
print("d1 equal:", mmh3.hash(X,1)==mmh3.hash(Y,1))

s = socket.create_connection(("archive.cryptohack.org", 29201), timeout=20)
s.settimeout(6)
def rd():
    buf=b""
    while True:
        try: d=s.recv(4096)
        except socket.timeout: return buf
        if not d: return buf
        buf+=d
        if buf.rstrip().endswith(b"option:"): return buf
rd()
s.sendall(b"1\n"+Y.hex().encode()+b"\n"); print("query Y before:", rd())
s.sendall(b"2\n"+X.hex().encode()+b"\n"); print("add X:", rd())
s.sendall(b"1\n"+Y.hex().encode()+b"\n"); print("query Y after add X:", rd())
s.sendall(b"4\n"); s.close()
print("done")
