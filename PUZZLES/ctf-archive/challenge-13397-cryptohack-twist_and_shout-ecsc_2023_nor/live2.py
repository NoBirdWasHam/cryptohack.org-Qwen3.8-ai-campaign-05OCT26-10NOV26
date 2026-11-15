import sys
sys.path.insert(0, ".")
import socket, itertools, pickle
import solve
from sympy.ntheory.modular import crt

class Client:
    def __init__(self):
        self.s = None; self.buf = b""; self.connect()
    def connect(self):
        if self.s:
            try: self.s.close()
            except Exception: pass
        self.s = socket.create_connection(("archive.cryptohack.org", 11718), timeout=60)
        self.buf = b""
        while b"x-coordinate: " not in self.buf:
            c = self.s.recv(4096)
            if not c: raise RuntimeError("closed")
            self.buf += c
        i = self.buf.index(b"x-coordinate: ")
        self.buf = self.buf[i+14:]
    def query(self, xv):
        for _ in range(2):
            try:
                self.s.sendall((str(xv) + "\n").encode())
                while b"x-coordinate: " not in self.buf:
                    c = self.s.recv(4096)
                    if not c: raise RuntimeError("closed")
                    self.buf += c
                i = self.buf.index(b"x-coordinate: ")
                resp = self.buf[:i]; self.buf = self.buf[i+14:]
                return int(resp.decode().strip())
            except Exception as e:
                print("reconnect:", repr(e), flush=True)
                self.connect()
        return None

c = Client()
ctxs = []
for l in solve.FACTORS:
    x, Q = solve.find_gen(l)
    ctxs.append((l, x, solve.Table(l, Q)))
    print("prepared", l, "x=", x, flush=True)

rps = []
for l, x, tbl in ctxs:
    xd = c.query(x)
    if xd is None:
        print(l, "CRASH -> residue 0", flush=True)
        rps.append((l, [0])); continue
    T = solve.target_from_x(xd)
    if T is None:
        print(l, "BAD xd:", xd, flush=True); continue
    e = tbl.dlog_sign(T)
    print(l, "e=", e, "(-e)=", (-e) % l, flush=True)
    rps.append((l, sorted({e % l, (-e) % l})))

pickle.dump(rps, open("residues.pkl", "wb"))
print("residues saved")

for combo in itertools.product(*[p for _, p in rps]):
    res = crt(solve.FACTORS, list(combo))
    if res is None: continue
    v, M = res
    L = (v.bit_length() + 7) // 8
    if L == 0 or L > 40: continue
    bs = v.to_bytes(L, "big")
    npass = sum(1 for ch in bs if 32 <= ch < 127)
    if npass >= len(bs) - 2:
        print("cand bits", v.bit_length(), f"{npass}/{len(bs)}", bs)
