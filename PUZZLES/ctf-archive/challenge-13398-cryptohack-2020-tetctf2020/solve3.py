import random, socket, time, sys, re

MAGIC = 0x9908b0df
M = 0xffffffff
HOST, PORT = "archive.cryptohack.org", 63222

def temper(y):
    y &= M
    y ^= y >> 11
    y ^= (y << 7) & 0x9d2c5680
    y ^= (y << 15) & 0xefc60000
    y ^= y >> 18
    return y

def untemper(y):
    y &= M
    y ^= y >> 18
    x2 = y
    for _ in range(4): x2 = y ^ ((x2 << 15) & 0xefc60000)
    x = x2 & M
    x2 = x
    for _ in range(6): x2 = x ^ ((x2 << 7) & 0x9d2c5680)
    x = x2 & M
    x2 = x
    for _ in range(6): x2 = x ^ (x2 >> 11)
    return x2 & M

def local_stream(seed, n=2020):
    r = random.Random(seed)
    return [r.getrandbits(32) for _ in range(n)]

def solve_target(o1792, o1396, msb2019=0):
    # Output j of CPython MT19937 = temper(X_{624+j}); X_m = new word at
    # linear position m (state slot m%624 after ceil(m/624) twists).
    # Twist: X_m = X_{m-227} ^ (y>>1) ^ MAGIC*(y&1),
    #        y = msb(X_{m-624})<<31 | low31(X_{m-623}).
    # Target X_2643: X_2643 = X_2416 ^ ((X_2020&0x7fffffff)>>1)
    #                             ^ MAGIC*(X_2020&1) ^ msb(X_2019)<<30.
    # Reveal idx 1792 -> X_2416 ; reveal idx 1396 -> X_2020.
    # Unknown: bit30 only (msb of the word behind output 1395).
    w2416 = untemper(o1792)
    w2020 = untemper(o1396)
    x2643 = w2416 ^ ((w2020 & 0x7fffffff) >> 1) ^ (MAGIC if (w2020 & 1) else 0) ^ (msb2019 << 30)
    return temper(x2643)

def local_check(verbose=True):
    outs = local_stream(42)
    assert untemper(outs[1792]) == untemper(outs[1792])  # sanity
    wins = tot = wrong = 0
    for t in range(400):
        o = local_stream(t)
        g0 = solve_target(o[1792], o[1396], 0)
        g1 = solve_target(o[1792], o[1396], 1)
        tgt = o[2019]
        tot += 1
        if g0 == tgt: wins += 1
        elif g1 == tgt: pass   # the other half: exactly-one-bit behavior
        else: wrong += 1
    print(f"local: msb=0 wins {wins}/{tot}, msb=1 wins {tot-wins-wrong}, misses {wrong}")
    return wrong == 0 and wins > 0

def run_once():
    ss = socket.create_connection((HOST, PORT), timeout=10)
    ss.settimeout(10)
    ss.sendall(b"1792\n1396\n")
    buf = b""
    lines = []
    t0 = time.time()
    while len(lines) < 2020 and time.time() - t0 < 25:
        try:
            b = ss.recv(65536)
        except socket.timeout:
            break
        if not b:
            break
        buf += b
        lines = buf.decode(errors="replace").splitlines()
    txt = "\n".join(lines)
    nums = re.findall(r"^(\d+)$", txt, re.M)
    if len(nums) != 2:
        ss.close()
        return None, txt
    # lines are printed in increasing i: nums[0]=idx1396, nums[1]=idx1792
    guess = solve_target(int(nums[1]), int(nums[0]), 0)
    ss.sendall(f"{guess}\n".encode())
    ss.settimeout(10)
    rest = b""
    try:
        while True:
            b = ss.recv(65536)
            if not b: break
            rest += b
    except socket.timeout:
        pass
    ss.close()
    return guess, txt + "\n" + rest.decode(errors="replace")

if __name__ == "__main__":
    ok = local_check()
    if "--local" in sys.argv:
        sys.exit(0 if ok else 1)
    if not ok:
        print("ABORT: local self-test failed"); sys.exit(1)
    for n in range(1, 61):
        g, txt = run_once()
        if g is None:
            print(n, "bad:", txt[:120].replace("\n", "|")); time.sleep(1.0); continue
        # 2026-11-05 fix: live flag format is TetCTF{...} (original TETCTF format),
        # not crypto{...}. Server prints NOTHING on wrong guess, the flag on right
        # guess -> win = any flag-shaped token anywhere in the transcript.
        m = re.search(r"[A-Za-z][A-Za-z0-9_]*\{[^}\n]+\}", txt)
        if m:
            print("WIN session", n, "->", m.group(0))
            open("flag_2020-tetctf2020.txt", "w").write(m.group(0))
            sys.exit(0)
        print(n, "miss (msb2019=1)")
        time.sleep(0.7)
    print("no win in budget")
