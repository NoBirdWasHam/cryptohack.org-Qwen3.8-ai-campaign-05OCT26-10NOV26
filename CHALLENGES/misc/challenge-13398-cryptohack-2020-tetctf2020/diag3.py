import solve3, socket, time, re, sys

HOST, PORT = solve3.HOST, solve3.PORT
M = 0xffffffff
MAGIC = solve3.MAGIC

def relation(vA, vB, bitoff=0):
    """vA=untempered X_{m-227}, vB=untempered X_{m-623} -> temper(X_m) candidates."""
    x = vA ^ ((vB & 0x7fffffff) >> 1) ^ (MAGIC if vB & 1 else 0)
    return [x & M, (x ^ (1 << 30)) & M]

def one_session(guess):
    ss = socket.create_connection((HOST, PORT), timeout=10)
    ss.settimeout(12)
    ss.sendall(b"1792\n1396\n")
    buf = b""; t0 = time.time(); nl = 0
    while nl < 2020 and time.time() - t0 < 25:
        try:
            b = ss.recv(65536)
        except socket.timeout:
            break
        if not b: break
        buf += b
        nl = len(buf.decode(errors="replace").splitlines())
    nums = [int(l) for l in buf.decode(errors="replace").splitlines() if l.isdigit()]
    if len(nums) != 2:
        ss.close(); return None
    v1396, v1792 = solve3.untemper(nums[0]), solve3.untemper(nums[1])
    cands = relation(v1792, v1396)
    g = cands[guess]
    ss.sendall(f"{g}\n".encode())
    ss.settimeout(8); rest = b""
    try:
        while True:
            b = ss.recv(65536)
            if not b: break
            rest += b
    except socket.timeout:
        pass
    ss.close()
    return rest.decode(errors="replace")

# hypothesis: target word m = 2643 + d for d in range(0..12) with
# same (X_{m-227},X_{m-623}) = revealed (only true for specific d but we test
# the d=0 branch pair exhaustively AND alternate both branches; a live model
# where target = one of the two candidates gives ~1/2 win for the right branch
# sequence. Run 16 sessions alternating branches 0,1,0,1...
wins = 0
for n in range(16):
    r = one_session(n % 2)
    if r is None:
        print(n, "bad"); time.sleep(0.5); continue
    if "{" in r:  # 2026-11-05 fix: live flag is TetCTF{...}; tail non-empty = win
        m = re.search(r"[A-Za-z][A-Za-z0-9_]*\{[^}\n]+\}", r)
        print("WIN", n, m.group(0))
        open("flag_2020-tetctf2020.txt", "w").write(m.group(0))
        sys.exit(0)
    print(n, "miss")
    time.sleep(0.4)
print("both-branch alternation: no win")
