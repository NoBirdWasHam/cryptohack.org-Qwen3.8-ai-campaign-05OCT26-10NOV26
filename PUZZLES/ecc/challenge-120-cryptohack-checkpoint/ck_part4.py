"""checkpoint part4 v2: smooth-twist oracle attack, prime-power merge.
Per curve: order-m point Q, oracle ct, enumerate r<m => s = r mod m.
Merge per prime (max exponent), consistency-check overlaps, CRT -> s mod M>=N.
ALL residues must come from ONE server session (s is per-session): no cross-run cache."""
import socket, json, hashlib, random, re, sys, time
from Crypto.Cipher import AES

P = 0xFFFFFFFF00000001000000000000000000000000FFFFFFFFFFFFFFFFFFFFFFFF
A = 0xFFFFFFFF00000001000000000000000000000000FFFFFFFFFFFFFFFFFFFFFFFC
N = 0xFFFFFFFF00000000FFFFFFFFFFFFFFFFBCE6FAADA7179E84F3B9CAC2FC632551
O = None
TEST_MSG = b"SERVER_TEST_MESSAGE"
PREFIX = TEST_MSG[:16]  # single CBC block match

def padd(Pt, Qt):
    if Pt is O: return Qt
    if Qt is O: return Pt
    x1, y1 = Pt; x2, y2 = Qt
    if x1 == x2:
        if (y1 + y2) % P == 0: return O
        lam = (3*x1*x1 + A) * pow(2*y1, -1, P) % P
    else:
        lam = (y2 - y1) * pow(x2 - x1, -1, P) % P
    x3 = (lam*lam - x1 - x2) % P
    y3 = (lam*(x1 - x3) - y1) % P
    return (x3, y3)
def pmul(k, Pt):
    R = O
    while k:
        if k & 1: R = padd(R, Pt)
        Pt = padd(Pt, Pt); k >>= 1
    return R
def sqrt_p(v): return pow(v, (P+1)//4, P)
def key_of(x): return hashlib.sha256(str(x).encode()).digest()[:16]

def new_session():
    s = socket.create_connection(("socket.cryptohack.org", 13419), timeout=60)
    f = s.makefile("rwb")
    banner = b""
    while banner.count(b"\n") < 5:
        line = f.readline()
        if not line: break
        banner += line
    txt = banner.decode()
    cps = re.findall(r"Point\(x=(\d+), y=(\d+)\)", txt)
    client_pub = (int(cps[0][0]), int(cps[0][1]))
    server_pub = (int(cps[1][0]), int(cps[1][1]))
    flag_ct = bytes.fromhex(re.match(r"([0-9a-f]+)", txt.split("server->client : ")[2]).group(1))
    return s, f, client_pub, flag_ct, server_pub

def send(f, o):
    f.write((json.dumps(o)+"\n").encode()); f.flush()
    return json.loads(f.readline().decode())

def rand_on(b, rng):
    while True:
        x = rng.randrange(P)
        v = (x*x*x + A*x + b) % P
        y = sqrt_p(v)
        if (y*y) % P == v: return (x, y)

def main():
    curves = json.load(open("ck_curves.json"))
    # order curves by descending m-size so we accumulate fast
    curves.sort(key=lambda c: -c["m"].bit_length())
    rng = random.Random(99)
    s, f, client_pub, flag_ct, server_pub = new_session()
    print("session ok", flush=True)

    best = {}   # prime l -> (e, residue mod l^e)
    raw = []    # per-curve (b, m, r) with the curve's own sign
    M = 1
    TARGET = 1 << 450   # ~22 curves: plenty of coprime material for sign search
    for c in curves:
        if M >= TARGET: break
        b, n, m = c["b"], c["n"], c["m"]
        primes = [l for l, e in c["fac"]]
        # skip if curve adds no new prime-power capacity
        gain = 1
        for l, pe in c["fac"]:
            e = 0; t = pe
            while t % l == 0: t //= l; e += 1
            if l not in best or best[l][0] < e: gain *= l ** (e - (best.get(l, (0,))[0]))
        if gain == 1:
            continue
        Q = None
        for _ in range(20):
            T = rand_on(b, rng)
            Qc = pmul(n // m, T)
            if Qc is O: continue
            if pmul(m, Qc) is not O: continue
            ok = True
            for l in set(primes):
                if m % l == 0 and pmul(m // l, Qc) is O: ok = False; break
            if ok: Q = Qc; break
        if Q is None:
            print("no order-m point b=", b % 10**6, flush=True); continue
        try:
            r = send(f, {"option": "start_key_exchange", "Qx": hex(Q[0]), "Qy": hex(Q[1]),
                         "ciphersuite": "ECDHE_P256_WITH_AES_128"})
            if "error" in str(r).lower():
                print("server err:", str(r)[:80], flush=True); continue
            ct = bytes.fromhex(send(f, {"option": "get_test_message"})["msg"])
        except Exception as ex:
            print("SESSION LOST:", ex, "- discarding, restart needed", flush=True)
            return
        rv = None
        R = O
        for rr in range(m):
            kx = key_of(R[0]) if R is not O else key_of(0)
            blk = AES.new(kx, AES.MODE_ECB).decrypt(ct[16:32])
            if bytes(a ^ bb for a, bb in zip(blk, ct[:16])) == PREFIX:
                rv = rr; break
            R = padd(R, Q)
        if rv is None:
            print("NO MATCH m bits", m.bit_length(), flush=True); continue
        raw.append({"b": b, "m": m, "r": rv})
        # merge per prime
        for l, pe in c["fac"]:
            e = 0; t = pe
            while t % l == 0: t //= l; e += 1
            if l in best and best[l][0] >= e:
                e0, r0 = best[l]
                if m % (l**e0) == 0 and r0 != rv % (l**e0):
                    print("!! INCONSISTENT mod", l, "^", e0, flush=True)
                continue
            best[l] = (e, rv % (l**e))
        M = 1
        for l, (e, r) in best.items(): M *= l**e
        print(f"curve m bits={m.bit_length()} r={rv} unique bits={M.bit_length()}", flush=True)
        time.sleep(0.3)
    print("collected unique bits:", M.bit_length(), flush=True)
    if M < N:
        print("INSUFFICIENT", flush=True); return
    # incremental CRT over prime powers (pairwise coprime)
    x, mm = 0, 1
    for l, (e, r) in sorted(best.items()):
        me = l**e
        x = x + mm * (((r - x) * pow(mm, -1, me)) % me)
        mm *= me
        x %= mm
    json.dump({"best": {str(l): [e, r] for l, (e, r) in best.items()},
               "client_pub": list(client_pub), "server_pub": list(server_pub),
               "flag_ct": flag_ct.hex(), "x": str(x), "M": str(M), "raw": raw}, open("ck_res.json", "w"))
    # SELF-CHECK: if x == s (mod N), then x*G == server_pub. No KDF assumptions.
    GX = 0x6B17D1F2E12C4247F8BCE6E563A440F277037D812DEB33A0F4A13945D898C296
    GY = 0x4FE342E2FE1A7F9B8EE7EB4A7C0F9E162BCE33576B315ECECBB6406837BF51F5
    xG = pmul(x % N, (GX, GY))
    print("x*G == server_pub ?", xG == server_pub, flush=True)
    if xG != server_pub:
        xG2 = pmul(x, (GX, GY))
        print("x*G (unreduced) == server_pub ?", xG2 == server_pub, flush=True)
    print("residues saved to ck_res.json", flush=True)
    # conclusion if x*G != P: s >= M, collect more curve bits and rerun
    if xG != server_pub:
        print("SCALAR INCOMPLETE - need more curve bits", flush=True)
    for tag, sec in [("x", x), ("x%N", x % N), ("x-N", x - N if x > N else None)]:
        if sec is None or sec <= 0: continue
        shared = pmul(sec, client_pub)
        key = key_of(shared[0])
        pt = AES.new(key, AES.MODE_CBC, flag_ct[:16]).decrypt(flag_ct[16:])
        print(tag, "plaintext:", pt[:60], flush=True)
        mm2 = re.search(rb"crypto\{{[^}}]+\}}", pt)
        if mm2:
            print("FLAG:", mm2.group(0).decode(), flush=True)
            open("flag.txt", "w").write(mm2.group(0).decode() + "\n")
            break

if __name__ == "__main__":
    main()
