# Solve "What a Curve!": oracle stream has FIXED keystream K (random mul => [mul^k]P
# independent of k => same block every query). answer(m) = K ^ m. Recover f from
# zero-blocks (linear: f = v^2 mod u), then K's 14 coeff unknowns (133 bits) via
# nonlinear system u|f-v^2 + ASCII keystream bits (D_1 = [2023]P0).
import socket, json, struct, time, sys, itertools
sys.path.insert(0, ".")
import cantor2 as K7
from polylib import mul as pmul_l, mod as pmod_l, sub as psub_l, crt as pcrt, powmod as ppow_l
P7 = 17585255163044402023
K7.set_p(P7)
HOST, PORT = "archive.cryptohack.org", 39003
SUF = b" This is your final boss, enjoy it while you still can:)"

def recv_some(s, t=8.0, idle=2.5):
    s.settimeout(idle)
    buf = b""; t0 = time.time()
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

def get_hex(buf):
    for ln in buf.decode(errors="replace").split("\n"):
        ln = ln.strip()
        if ln and len(ln) >= 16 and all(c in "0123456789abcdef" for c in ln):
            return ln
    return None

def query(s, msg):
    s.sendall(msg.hex().encode() + b"\n")
    return bytes.fromhex(get_hex(recv_some(s)))

def capture(path="session2.json", nzero=4, extra=True):
    S = {}
    s = socket.create_connection((HOST, PORT), timeout=15)
    S["C"] = get_hex(recv_some(s, 10))
    S["zeros"] = [query(s, b"\x00" * 112).hex() for _ in range(nzero)]
    if extra:
        # pattern queries to probe keystream consistency (should equal K ^ m)
        m = bytes(range(112))
        r = query(s, m)
        S["pat"] = [m.hex(), r.hex()]
    if extra:
        # 2-block query: if stream continues to a DIFFERENT block, detect via pattern re-use
        r = query(s, b"\x00" * 224)
        S["z224"] = r.hex()
    # fresh connection to measure keystream repeatability across connections
    s.close()
    s2 = socket.create_connection((HOST, PORT), timeout=15)
    S["C2"] = get_hex(recv_some(s2, 10))
    S["zeros2"] = query(s2, b"\x00" * 112).hex()
    s2.close()
    json.dump(S, open(path, "w"))
    return S

def recover_f(zero_hexes):
    rs = []; ms = []
    for hx in zero_hexes:
        b = struct.unpack('<14Q', bytes.fromhex(hx))
        u = list(b[:7]) + [1]; v = list(b[7:14])
        rs.append(pmod_l(pmul_l(v, v), u)); ms.append(u)
    F, M = pcrt(rs, ms)
    if len(F) - 1 != 15:
        return None
    return F

def main():
    S = capture()
    print("C len", len(bytes.fromhex(S["C"])))
    f = recover_f(S["zeros"])
    print("f deg15 recovered:", f is not None)
    if f is None:
        # try subsets of 3
        z = S["zeros"]
        for tri in itertools.combinations(range(len(z)), 3):
            f = recover_f([z[i] for i in tri])
            if f is not None:
                print("works with subset", tri); break
    if f is None:
        print("FAILED f recovery"); json.dump(S, open("session2.json", "w")); return
    K = bytes.fromhex(S["zeros"][0])
    # consistency checks
    print("zeros all equal:", all(bytes.fromhex(x) == K for x in S["zeros"]))
    pat_m, pat_r = bytes.fromhex(S["pat"][0]), bytes.fromhex(S["pat"][1])
    print("pattern test K^m:", bytes(a ^ b for a, b in zip(pat_m, K)) == pat_r)
    z224 = bytes.fromhex(S["z224"])
    print("224-query: first112==K:", z224[:112] == K, " second112==K:", z224[112:] == K)
    z2 = bytes.fromhex(S["zeros2"])
    print("keystream same on NEW connection:", z2 == K)
    # unpack K as divisor, check reduced under f
    b = struct.unpack('<14Q', K)
    D = (list(b[:7]) + [1], list(b[7:14]))
    print("K-as-divisor reduced:", K7.is_reduced(D, f))
    # decrypt with known-suffix hypothesis
    C = bytes.fromhex(S["C"])
    m = bytes(a ^ b for a, b in zip(C, K))
    print("decrypted msg:", m[:100])
    print("suffix match:", m.endswith(SUF))

main()
