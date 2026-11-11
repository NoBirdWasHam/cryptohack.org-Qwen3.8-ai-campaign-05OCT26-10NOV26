# Full live run: PoW -> send (1,1,1) -> capture q,n1..n4 -> solve -> submit factors -> flag.
import socket, hashlib, json, sys, time, multiprocessing
sys.path.insert(0, ".")

HOST, PORT = "archive.cryptohack.org", 42957

def _pow_chunk(args):
    s, lo, hi = args
    h = hashlib.sha256
    for i in range(lo, hi):
        cand = hex(i)[2:] if i else "0"
        d0 = h((s + cand).encode()).digest()
        if d0[-1] < 4:
            d = int.from_bytes(d0, "big")
            if d == (d >> 26) << 26:
                return cand
    return None

def pow_answer(s):
    procs = multiprocessing.cpu_count()
    for base_shift in (28, 30, 32):
        span = 1 << base_shift
        per = span // procs
        with multiprocessing.Pool(procs) as p:
            for r in p.imap_unordered(_pow_chunk,
                                      [(s, k * per, (k + 1) * per) for k in range(procs)]):
                if r is not None:
                    return r
    return None

def main():
    t0 = time.time()
    sk = socket.create_connection((HOST, PORT), timeout=20)
    f = sk.makefile("rwb")
    def readline(t=30):
        f.flush()
        sk.settimeout(t)
        b = f.readline()
        return b.decode().strip()
    def sendline(s):
        f.write((str(s) + "\n").encode()); f.flush()
    print("L1:", readline(), flush=True)
    salt = readline()
    print("salt:", salt, flush=True)
    ans = pow_answer(salt)
    print("POW:", ans, "%.0fs" % (time.time() - t0), flush=True)
    if ans is None:
        print("POW FAILED"); return
    sendline(ans)
    line = readline()
    print("qline:", line[:60], flush=True)
    q = int(line.split("=")[1].strip()) if "=" in line else int(line)
    print("q bits:", q.bit_length(), flush=True)
    print("hello:", readline(), flush=True)
    sendline(1); sendline(1); sendline(1)
    ns = []
    for i in range(4):
        line = readline(t=120)
        if not line:
            print("EOF before n%d" % i); return
        ns.append(int(line))
        print("got n%d (%d chars)" % (i, len(line)), flush=True)
    json.dump({"q": str(q), "ns": [str(x) for x in ns]}, open("live_instance.json", "w"))
    t1 = time.time()
    from attack import solve_instance
    out = solve_instance(q, ns)
    print("solve: %.0fs ->" % (time.time() - t1), "OK" if out else "FAIL", flush=True)
    if not out:
        return
    for (pu, pv), n in zip(out, ns):
        assert pu * pv == n
        sendline(pu); sendline(pv)
        print("submitted factor pair", flush=True)
    time.sleep(1)
    sk.settimeout(15)
    try:
        rest = f.read().decode(errors="replace")
    except Exception:
        rest = ""
    print("SERVER REST:", rest, flush=True)
    for tok in rest.split():
        if tok.startswith("crypto{") or tok.startswith("flag{"):
            open("FLAG.txt", "w").write(tok)
            print("FLAG SAVED:", tok, flush=True)

if __name__ == "__main__":
    main()
