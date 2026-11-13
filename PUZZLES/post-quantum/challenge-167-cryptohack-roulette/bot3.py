# roulette v3 — Q=P: r^(k)=s_{k+1}&mask30. State1 digits observed -> r1; then per state:
# s = (c<<240)+r_prev (65536 cands), filter by spins, bet exact once all cands agree.
import socket, json
import p256 as ec

HOST, PORT = "socket.cryptohack.org", 13387
PX = ec.GX
PY = ec.GY
MASK = (1 << 240) - 1

def digits_ms(n, b=37):
    d = []
    while n >= b:
        d.append(n % b); n //= b
    d.append(n)
    return bytes(d[::-1])

def from_ms(ds, b=37):
    n = 0
    for x in ds: n = n * b + x
    return n

# tables: tbl2[i] = 2^(240+i) * G
tbl2 = []
acc = ec.G
for _ in range(240): acc = ec.add(acc, acc)
for i in range(16):
    tbl2.append(acc); acc = ec.add(acc, acc)

def build_cands(r_prev):
    base = ec.mul(r_prev, ec.G)
    out = {}
    for c in range(65536):
        pt = base
        cc = c; i = 0
        while cc:
            if cc & 1: pt = ec.add(pt, tbl2[i])
            cc >>= 1; i += 1
        dg = digits_ms(pt[0] & MASK)
        out.setdefault(dg, []).append((c << 240) + r_prev)
    return out

def run(verbose=True):
    sock = socket.create_connection((HOST, PORT), timeout=120)
    f = sock.makefile("rwb")
    def rjson():
        while True:
            line = f.readline()
            if not line: raise EOFError()
            s = line.decode().strip()
            if not s: continue
            try: return json.loads(s)
            except Exception: continue
    def send(obj):
        sock.sendall((json.dumps(obj) + "\n").encode())
        return rjson()

    send({"x": hex(PX), "y": hex(PY)})
    cands = None
    obs = bytearray()
    k = 0
    for rnd in range(124):
        if cands is not None:
            vals = {dg[k] for dg in cands if len(dg) > k}
            full = all(len(dg) > k for dg in cands)
            bet = vals.pop() if (full and len(vals) == 1) else "EVEN"
        else:
            bet = "EVEN"
        r = send({"choice": bet})
        if "spin" not in r:
            print("end:", str(r)[:200])
            if "flag" in str(r): open("flag_roulette.txt","w").write(str(r))
            sock.close(); return
        spin = r["spin"]
        newc = "new croupier" in r.get("msg", "")
        if cands is not None:
            cands = {dg: v for dg, v in cands.items() if len(dg) > k and dg[k] == spin}
        else:
            obs.append(spin)
        if verbose and rnd >= 40 and rnd % 5 == 0:
            print(f"[{rnd}] bet={bet} spin={spin} cands={len(cands) if cands else 'NA'} $={r.get('$')}")
        if newc:
            if cands is None:
                r1 = from_ms(obs)
                if verbose: print(f"[{rnd}] state1 done ({len(obs)} digits), building cands...")
                cands = build_cands(r1)
                if verbose: print(f"[{rnd}] cands={len(cands)}")
            else:
                surv = [s for v in cands.values() for s in v]
                s_cur = surv[0]
                r_prev = ec.mul(s_cur, ec.G)[0] & MASK
                cands = build_cands(r_prev)
                if verbose: print(f"[{rnd}] NEW STATE, cands={len(cands)} $={r.get('$')}")
            k = 0
        else:
            k += 1
        if r.get("$", 99) <= 1:
            print("broke at", rnd); sock.close(); return
    print("final $", r.get("$"))
    sock.close()

for attempt in range(6):
    try:
        run(verbose=(attempt == 0)); break
    except Exception as ex:
        print("attempt", attempt, "err:", str(ex)[:120])
