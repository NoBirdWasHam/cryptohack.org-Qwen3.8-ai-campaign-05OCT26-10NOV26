import solve3, socket, time, re, sys

HOST, PORT = solve3.HOST, solve3.PORT

def full_session():
    ss = socket.create_connection((HOST, PORT), timeout=10)
    ss.settimeout(12)
    ss.sendall(b"1792\n1396\n")
    buf = b""
    t0 = time.time()
    nlines = 0
    while nlines < 2020 and time.time() - t0 < 25:
        try:
            b = ss.recv(65536)
        except socket.timeout:
            break
        if not b:
            break
        buf += b
        nlines = len(buf.decode(errors="replace").splitlines())
    return ss, buf.decode(errors="replace")

def session_guess(guess_fn):
    ss, txt = full_session()
    nums = [int(l) for l in txt.splitlines() if l.isdigit()]
    if len(nums) != 2:
        ss.close(); return "bad", txt
    v1396, v1792 = nums  # printed in index order
    g = guess_fn(v1396, v1792)
    if g is None:
        ss.close(); return "nofn", txt
    ss.sendall(f"{g}\n".encode())
    ss.settimeout(8)
    rest = b""
    try:
        while True:
            b = ss.recv(65536)
            if not b: break
            rest += b
    except socket.timeout:
        pass
    ss.close()
    tail = rest.decode(errors="replace")
    return ("WIN" if tail.strip() else "miss"), tail  # 2026-11-05 fix: any tail = flag (TetCTF{...} format)

def raw_guess(v1396, v1792):
    # live RNG emits RAW words: v1396 = X_2020, v1792 = X_2416 directly
    x = v1792 ^ ((v1396 & 0x7fffffff) >> 1) ^ (solve3.MAGIC if v1396 & 1 else 0)
    return x & 0xffffffff  # msb2019=0 branch

MODE = sys.argv[1] if len(sys.argv) > 1 else "raw"
fn = raw_guess if MODE == "raw" else (lambda a, b: solve3.solve_target(b, a, 0))
for n in range(16):
    st, tail = session_guess(fn)
    print(n, st)
    if st == "WIN":
        m = re.search(r"crypto\{[^}\n]*\}", tail)
        print("FLAG:", m.group(0))
        open("flag_2020-tetctf2020.txt", "w").write(m.group(0))
        sys.exit(0)
    time.sleep(0.5)
