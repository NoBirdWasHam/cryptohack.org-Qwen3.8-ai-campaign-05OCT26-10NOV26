# RUN#6 intended path (official deuterium solve, per AAR RUN#5): per-block CP-SAT over
# all 512 bits + 256 pseudo-Boolean equalities sum_k a_{j,k} x_k = c_j, reconnect-loop
# across fresh instances until all 7 flag segments land.
# modes:
#   cpsat_solve.py offline [blockidx]   -> sanity-check vs cached live_output.txt (no net)
#   cpsat_solve.py live                 -> reconnect loop, archive.cryptohack.org 36813
import hashlib, json, os, socket, sys, time

D = os.path.dirname(os.path.abspath(__file__))
P = lambda f: os.path.join(D, f)
STATE = P("cpsat_segs.json")
HOST, PORT = "archive.cryptohack.org", 36813
MIN_CONN_GAP = 10.0  # rate limit: <=1 connection / 10s

def pubkey(secret: bytes):
    st = hashlib.sha512(secret).digest(); pub = []
    for _ in range(256):
        pub.append(int.from_bytes(st, "big")); st = hashlib.sha512(st).digest()
    return pub

def parse_instance(text):
    lines = [l for l in text.splitlines() if l.strip()]
    secret = bytes.fromhex(lines[0].strip())
    enc = json.loads(lines[1])
    assert len(enc) in range(1, 20) and all(len(b) == 256 for b in enc)
    return secret, enc

def solve_block(pub, cvec, time_limit):
    from ortools.sat.python import cp_model
    m = cp_model.CpModel()
    x = [m.NewBoolVar(f"x{p}") for p in range(512)]
    for j, cj in enumerate(cvec):
        aa = pub[j]; terms = []
        while aa:
            lb = (aa & -aa).bit_length() - 1
            terms.append(x[lb]); aa &= aa - 1
        m.Add(sum(terms) == cj)
    solver = cp_model.CpSolver()
    solver.parameters.max_time_in_seconds = float(time_limit)
    solver.parameters.num_search_workers = 2
    st = solver.Solve(m)
    if st not in (cp_model.OPTIMAL, cp_model.FEASIBLE):
        return None
    m_int = 0
    for p in range(512):
        if solver.Value(x[p]): m_int |= 1 << p
    # independent verification: all 256 popcount eqs
    for j in range(256):
        if bin(pub[j] & m_int).count("1") != cvec[j]:
            return None
    return m_int

def seg_of(m_int):
    return m_int.to_bytes(64, "big")[24:32]

def printable(b):
    return all(32 <= c < 127 for c in b)

def load_segs():
    if os.path.exists(STATE):
        d = json.load(open(STATE))
        return {int(k): bytes.fromhex(v) for k, v in d.items()}
    return {}

def save_segs(segs):
    json.dump({str(k): v.hex() for k, v in segs.items()}, open(STATE, "w"))

def time_cap(pass_no):
    return 5.0 if pass_no <= 3 else (10.0 if pass_no <= 6 else 20.0)

def main():
    mode = sys.argv[1] if len(sys.argv) > 1 else "offline"
    if mode == "offline":
        bi = int(sys.argv[2]) if len(sys.argv) > 2 else 0
        txt = open(P("live_output.txt")).read()
        secret, enc = parse_instance(txt)
        pub = pubkey(secret)
        t = time.time(); m_int = solve_block(pub, enc[bi], 60.0)
        dt = time.time() - t
        if m_int is None:
            print(f"OFFLINE b{bi}: NO SOLUTION within 60s"); sys.exit(1)
        seg = seg_of(m_int)
        print(f"OFFLINE b{bi}: solved+verified 256 eqs in {dt:.1f}s seg={seg!r} printable={printable(seg)}")
        sys.exit(0)

    assert mode == "live"
    segs = load_segs()
    print(f"resume: have {sorted(segs)} of 7", flush=True)
    pass_no = 0
    last_conn = 0.0
    t0 = time.time()
    while len(segs) < 7 and time.time() - t0 < 3000:
        gap = time.time() - last_conn
        if gap < MIN_CONN_GAP: time.sleep(MIN_CONN_GAP - gap)
        last_conn = time.time(); pass_no += 1
        s = socket.create_connection((HOST, PORT), timeout=15)
        s.settimeout(30)
        buf = b""
        while True:
            try: chunk = s.recv(65536)
            except socket.timeout: break
            if not chunk: break
            buf += chunk
            if buf.count(b"\n") >= 2 and len(buf) > 100: break
        s.close()
        try:
            secret, enc = parse_instance(buf.decode())
        except Exception as ex:
            print(f"pass{pass_no}: bad instance ({ex!r}) len={len(buf)}", flush=True); continue
        pub = pubkey(secret)
        for bi in range(7):
            if bi in segs: continue
            t = time.time()
            m_int = solve_block(pub, enc[bi], time_cap(pass_no))
            dt = time.time() - t
            if m_int is None:
                print(f"pass{pass_no} b{bi}: unsolved {dt:.1f}s", flush=True); continue
            seg = seg_of(m_int)
            if not printable(seg):
                print(f"pass{pass_no} b{bi}: verified but non-printable {seg!r} {dt:.1f}s", flush=True); continue
            segs[bi] = seg; save_segs(segs)
            print(f"pass{pass_no} b{bi}: LANDED {seg!r} {dt:.1f}s total={len(segs)}/7", flush=True)
        print(f"pass{pass_no} done, have {sorted(segs)}", flush=True)
    if len(segs) == 7:
        flag = b"".join(segs[i] for i in range(7)).rstrip(b"\x00").decode("latin-1")
        print("FLAG:", repr(flag), flush=True)
        open(P("flag_failproof_revenge-sekaictf202.txt"), "w").write(flag)
    else:
        print("incomplete:", sorted(segs)); sys.exit(2)

if __name__ == "__main__":
    main()
