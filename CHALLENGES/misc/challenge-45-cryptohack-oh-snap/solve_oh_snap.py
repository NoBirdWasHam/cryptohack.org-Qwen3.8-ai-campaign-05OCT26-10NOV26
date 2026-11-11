#!/usr/bin/env python3
"""oh_snap solver: iterative Klein/PTW sigma attack over a live RC4 keystream oracle.

Oracle: GET /oh_snap/send_cmd/<ct_hex>/<nonce_hex>/ with ct=00*m echoes
RC4(nonce||FLAG) keystream (m bytes) in the error message.

Round structure: nonce = R(rlen) || known_prefix. KSA is simulated over
nonce + known_prefix (the known flag copy that follows the nonce in the key),
so the first unknown flag byte gets a full-strength Klein vote and later bytes
get telescoped sigma votes. Recover, extend prefix, repeat. Verify candidates
by predicting held-out keystreams.

Usage:
  python3 solve_oh_snap.py collect <prefix> <count> <outfile> [workers] [m]
  python3 solve_oh_snap.py analyze <jsonl files...> [--known PREFIX]
"""
import sys, os, json, time, random, math, threading
from collections import Counter
from concurrent.futures import ThreadPoolExecutor
import requests
from Crypto.Cipher import ARC4

BASE = "https://aes.cryptohack.org/oh_snap/send_cmd/{ct}/{nonce}/"
HDR = {"User-Agent": "Mozilla/5.0 (X11; Linux x86_64) oh-snap-research/1.0"}
RLEN = 4
CHARSET = set(range(0x20, 0x7F))

# ---------------- oracle ----------------
def fetch_ks(session, nonce: bytes, m: int) -> bytes:
    url = BASE.format(ct="00" * m, nonce=nonce.hex())
    r = session.get(url, headers=HDR, timeout=30)
    d = r.json()
    if "error" in d and d["error"].startswith("Unknown command:"):
        return bytes.fromhex(d["error"].split(":", 1)[1].strip())
    raise RuntimeError(d)

def collect(prefix: bytes, count: int, outfile: str, workers: int = 10, m: int = 96):
    rng = random.Random()
    lock = threading.Lock()
    fh = open(outfile, "a")
    done = [0]
    t0 = time.time()
    def worker(_):
        s = requests.Session()
        local = []
        for i in range(10 ** 9):
            R = bytes(rng.randrange(256) for _ in range(RLEN))
            N = R + prefix
            try:
                ks = fetch_ks(s, N, m)
            except Exception as e:
                time.sleep(1.0)
                try:
                    ks = fetch_ks(s, N, m)
                except Exception:
                    s = requests.Session()
                    continue
            local.append((N.hex(), ks.hex()))
            if len(local) >= 200:
                with lock:
                    for a, b in local:
                        fh.write(json.dumps({"n": a, "k": b}) + "\n")
                    fh.flush()
                    done[0] += len(local)
                    if done[0] % 10000 < 200:
                        el = time.time() - t0
                        print(f"[{el:7.1f}s] {done[0]}/{count} ({done[0]/el:.1f} q/s)", flush=True)
                local = []
            if done[0] >= count:
                break
        with lock:
            for a, b in local:
                fh.write(json.dumps({"n": a, "k": b}) + "\n")
            fh.flush()
            done[0] += len(local)
    with ThreadPoolExecutor(workers) as ex:
        list(ex.map(worker, range(workers)))
    fh.close()
    print(f"done: {done[0]} samples -> {outfile}")

# ---------------- voting ----------------
def ksa_sim(N: bytes):
    S = list(range(256)); j = 0; jhist = []
    for i in range(len(N)):
        j = (j + S[i] + N[i]) & 0xFF
        S[i], S[j] = S[j], S[i]
        jhist.append(j)
    return S, j, jhist

def add_votes(sim_prefix: bytes, z: bytes, tmax: int, table: dict, w_mp=4):
    """sim_prefix: all key bytes whose KSA rounds are fully known (nonce+known copy).
    table[t] votes for sigma_t = sum of key bytes [len(sim_prefix) .. len(sim_prefix)+t]."""
    S, j, jhist = ksa_sim(sim_prefix)
    n = len(sim_prefix)
    sigma = 0
    for t in range(tmax):
        l = n + t
        if l >= len(z):
            break
        sigma = (sigma + S[l]) & 0xFF
        tmp = (l - z[l - 1]) & 0xFF
        table[t][(S.index(tmp) - j - sigma) & 0xFF] += 13
        zl = z[l]
        if zl >= l and all(jh != zl for jh in jhist):
            table[t][(zl - j - sigma) & 0xFF] += w_mp

# ---------------- DP search ----------------
def dp_search(table: dict, t_start: int, tmax: int, M=16, charset=CHARSET):
    """table[t] votes sigma over bytes starting at t_start (sigma_-1 = 0).
    Returns closed candidates (bytes from t_start onward ending with '}'), best first."""
    states = {0: [(0.0, b"")]}
    closed = []
    for t in range(t_start, tmax):
        if t not in table:
            break
        votes = table[t]
        tot = sum(votes.values()) or 1
        logp = [(sg, math.log(v / tot)) for sg, v in votes.items()]
        newstates = {}
        for sprev, paths in states.items():
            for score, bs in paths:
                for sg, lp in logp:
                    b = (sg - sprev) & 0xFF
                    if b in charset:
                        sc = score + lp
                        nb = bs + bytes([b])
                        if b == 0x7D:
                            closed.append((sc, nb))
                        newstates.setdefault(sg, []).append((sc, nb))
        states = {}
        for sg, lst in newstates.items():
            lst.sort(key=lambda x: -x[0])
            states[sg] = lst[:M]
        if not states:
            break
    closed.sort(key=lambda x: -x[0])
    return closed

def verify(flag: bytes, samples, need=3):
    ok = 0
    for nhex, kshex in samples:
        N = bytes.fromhex(nhex); ks = bytes.fromhex(kshex)
        if ARC4.new(N + flag).decrypt(b"\x00" * len(ks)) == ks:
            ok += 1
        else:
            return False
        if ok >= need:
            return True
    return ok >= need

def load_samples(*files):
    out = []
    for f in files:
        with open(f) as fh:
            for line in fh:
                line = line.strip()
                if line:
                    out.append(tuple(json.loads(line).values()))
    return out

def build_table(samples, known: bytes, tmax=50):
    """samples: (nonce_hex, ks_hex) with nonce = R||known. Votes indexed by
    ABSOLUTE flag byte index: table[p+t] estimates sigma over known..p+t."""
    p = len(known)
    table = {}
    for nhex, kshex in samples:
        N = bytes.fromhex(nhex); z = bytes.fromhex(kshex)
        sim = N + known
        n = len(sim)
        S, j, jhist = ksa_sim(sim)
        sigma = 0
        for t in range(tmax):
            l = n + t
            if l >= len(z):
                break
            sigma = (sigma + S[l]) & 0xFF
            tmp = (l - z[l - 1]) & 0xFF
            table.setdefault(p + t, Counter())[(S.index(tmp) - j - sigma) & 0xFF] += 13
            zl = z[l]
            if zl >= l and all(jh != zl for jh in jhist):
                table[p + t][(zl - j - sigma) & 0xFF] += 4
    return table

def argmax_bytes(table, p, tmax=50):
    """greedy: bytes from p onward via argmax sigma differences; report margins."""
    out = []
    sprev = 0
    for t in range(p, tmax):
        if t not in table:
            break
        mc = table[t].most_common(2)
        if not mc:
            break
        best = mc[0][0]
        margin = mc[0][1] - (mc[1][1] if len(mc) > 1 else 0)
        b = (best - sprev) & 0xFF
        sprev = best
        out.append((t, b, margin, mc[0][1]))
    return out

def confident_extend(known, table, thresh=3.5):
    """Greedy argmax-sigma differences while margin >= thresh*sqrt(top2) and
    byte in charset. Returns (extended_known, rows)."""
    out = bytearray(known)
    sprev = 0
    rows = []
    for t in range(len(known), 50):
        if t not in table:
            break
        mc = table[t].most_common(2)
        if not mc:
            break
        top, v1 = mc[0]
        v2 = mc[1][1] if len(mc) > 1 else 0
        margin = v1 - v2
        b = (top - sprev) & 0xFF
        rows.append((t, b, margin, v1, v2))
        if margin < thresh * (v2 ** 0.5 + 1) or b not in CHARSET:
            break
        out.append(b)
        sprev = top
        if b == 0x7D:  # '}'
            break
    return bytes(out), rows

def final_dp(known, table, held, M=16, tmax=50):
    closed = dp_search(table, len(known), tmax, M=M)
    for score, bs in closed:
        cand = known + bs
        if verify(cand, held):
            return cand, score, len(closed)
    return None, None, len(closed)

if __name__ == "__main__":
    mode = sys.argv[1]
    if mode == "collect":
        prefix = sys.argv[2].encode()
        count = int(sys.argv[3]); outfile = sys.argv[4]
        workers = int(sys.argv[5]) if len(sys.argv) > 5 else 10
        m = int(sys.argv[6]) if len(sys.argv) > 6 else 96
        collect(prefix, count, outfile, workers, m)
    elif mode == "report":
        files = [a for a in sys.argv[2:] if not a.startswith("--")]
        known = b"crypto{"
        for a in sys.argv[2:]:
            if a.startswith("--known="):
                known = a.split("=", 1)[1].encode()
        samples = load_samples(*files)
        print(f"{len(samples)} samples, prefix={known!r}")
        held = samples[-20:]
        table = build_table(samples[:-20], known)
        ext, rows = confident_extend(known, table)
        for t, b, margin, v1, v2 in rows:
            print(f"byte {t}: {chr(b)!r} margin={margin} votes={v1} second={v2}")
        print(f"confident: {ext!r}")
        if ext.endswith(b"}"):
            ok = verify(ext, held)
            print(f"FLAG candidate: {ext!r} verified={ok}")
        else:
            cand, score, nc = final_dp(ext, table, held)
            print(f"DP closed={nc} verified={'None' if cand is None else repr(cand)}")
    elif mode == "analyze":
        files = [a for a in sys.argv[2:] if not a.startswith("--")]
        known = b"crypto{"
        for a in sys.argv[2:]:
            if a.startswith("--known"):
                known = a.split("=", 1)[1].encode()
        samples = load_samples(*files)
        print(f"{len(samples)} samples, prefix={known!r}")
        held = samples[-20:]
        table = build_table(samples[:-20], known)
        for t, b, margin, v in argmax_bytes(table, len(known)):
            print(f"byte {t}: {chr(b)!r} margin={margin} votes={v}")
