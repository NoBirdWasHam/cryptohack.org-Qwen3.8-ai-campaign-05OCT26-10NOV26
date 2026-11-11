import sys, socket, time
sys.path.insert(0, ".")
import solve
import itertools
from sympy.ntheory.modular import crt

buf = b""
s = None
def connect():
    global s, buf
    s = socket.create_connection(("archive.cryptohack.org", 11718), timeout=60)
    buf = b""
    while b"x-coordinate: " not in buf:
        c = s.recv(4096)
        if not c: raise RuntimeError("closed")
        buf += c
    return s

def oracle(xv):
    global s
    for attempt in range(2):
        try:
            s.sendall((str(xv) + "\n").encode())
            while b"x-coordinate: " not in buf:
                c = s.recv(4096)
                if not c: raise RuntimeError("closed")
                buf += c
            i = buf.index(b"x-coordinate: "); resp, buf = buf[:i], buf[i+14:]
            return resp.decode().strip(), repr(resp)
        except Exception as e:
            print("reconnect after", repr(e), flush=True)
            connect()
    return None, None

connect()
ctxs = []
for l in solve.FACTORS:
    x, Q = solve.find_gen(l)
    ctxs.append((l, x, solve.Table(l, Q)))
rps = []
raw = []
for l, x, tbl in ctxs:
    r = oracle(x)
    if r[0] is None:
        print(l, "CRASH->0")
        rps.append((l, [0])); raw.append((l, None)); continue
    txt, rr = r
    try:
        xd = int(txt)
    except ValueError:
        print(l, "PARSE FAIL raw:", rr); raise
    e = tbl.dlog_sign(solve.target_from_x(xd))
    print(l, "xd=", xd, "e=", e, flush=True)
    rps.append((l, sorted({e % l, (-e) % l})))
    raw.append((l, xd))

for combo in itertools.product(*[p for _, p in rps]):
    res = crt(solve.FACTORS, list(combo))
    if res is None: continue
    v, M = res
    L = (v.bit_length() + 7) // 8
    try: bs = v.to_bytes(L, "big")
    except Exception: continue
    npass = sum(1 for c in bs if 32 <= c < 127)
    if npass >= len(bs) - 2 and len(bs) <= 40:
        print("cand bits", v.bit_length(), npass, "/", len(bs), bs[:40])
print("done")
