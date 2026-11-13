import socket, json, struct, time, sys
sys.path.insert(0, ".")
import cantor2 as K
from polylib import crt, mul as pmul_l, mod as pmod_l, sub as psub_l
P7 = 17585255163044402023
K.set_p(P7)
HOST, PORT = "archive.cryptohack.org", 39003

def recv_some(s, t=8.0, idle=2.5):
    s.settimeout(idle)
    buf = b""
    t0 = time.time()
    while time.time() - t0 < t:
        try:
            d = s.recv(4096)
        except socket.timeout:
            if buf: break
            continue
        except OSError:
            break
        if not d: break
        buf += d
    return buf

def hexlines(buf):
    out = []
    for ln in buf.decode(errors="replace").split("\n"):
        ln = ln.strip()
        if ln and len(ln) >= 16 and all(c in "0123456789abcdef" for c in ln):
            out.append(ln)
    return out

def unpack(v14):
    return (list(v14[:7]) + [1], list(v14[7:14]))

def send_q(s, nbytes):
    s.sendall(b"00" * nbytes + b"\n")
    buf = recv_some(s)
    hl = hexlines(buf)
    return hl[0] if hl else None

def main():
    S = {}
    s = socket.create_connection((HOST, PORT), timeout=15)
    hello = recv_some(s, 10)
    hl = hexlines(hello)
    C = hl[0]
    S["C"] = C
    print("C len", len(C) // 2, "bytes")
    # fresh-instance samples for f recovery: 4 x 112
    r112 = []
    for i in range(4):
        r = send_q(s, 112)
        r112.append(r)
        print("q112", i, "len", len(r) // 2 if r else None)
    # split test on a FRESH connection later; but same-connection stream test:
    r56a = send_q(s, 56)
    r56b = send_q(s, 56)
    # second 112-block pair to check consecutive relation
    S.update(C_=C, r112=r112, r56a=r56a, r56b=r56b)
    # recover f from r112[0..2]
    rs = []; ms = []
    for r in r112[:3]:
        D = unpack(struct.unpack('<14Q', bytes.fromhex(r)[:112]))
        u, v = D
        vsq = pmul_l(v, v)
        rs.append(pmod_l(vsq, u)); ms.append(u)
    F, M = crt(rs, ms)
    # truncate mod product poly then take deg<16 rep
    # F already reduced mod M (deg M=21). Need f deg<16: check consistency:
    print("crt deg", len(F) - 1)
    # overdetermined check with sample 4
    D4 = unpack(struct.unpack('<14Q', bytes.fromhex(r112[3])[:112]))
    okc = pmod_l(psub_l(F, pmul_l(D4[1], D4[1])), D4[0]) == [0]
    print("sample4 consistent:", okc)
    f = F[:16]
    S["f"] = f
    # reduced check for all
    for i, r in enumerate(r112):
        D = unpack(struct.unpack('<14Q', bytes.fromhex(r)[:112]))
        print("block", i, "reduced:", K.is_reduced(D, f))
    # consecutive-pair test [2023]
    D1 = unpack(struct.unpack('<14Q', bytes.fromhex(r112[0])[:112]))
    D2 = unpack(struct.unpack('<14Q', bytes.fromhex(r112[1])[:112]))
    t0 = time.time()
    m1 = K.mul_scalar(D1, 2023, f)
    print("[2023]R1 == R2 ?", m1 == D2, "(%.1fs)" % (time.time() - t0))
    # split block combined reduced test
    comb = bytes.fromhex(r56a) + bytes.fromhex(r56b)
    Ds = unpack(struct.unpack('<14Q', comb))
    print("split 56+56 one block reduced?", K.is_reduced(Ds, f))
    # if not, split blocks are separate: check each half reduced-as-partial impossible; skip
    # keep connection: also grab hex of another fresh connection later
    s.close()
    json.dump(S, open("session1.json", "w"))
    print("saved session1.json")

main()
