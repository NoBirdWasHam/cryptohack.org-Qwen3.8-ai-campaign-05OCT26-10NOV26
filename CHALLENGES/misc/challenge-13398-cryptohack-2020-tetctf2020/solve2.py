import random, socket, time, sys, re

MAGIC = 0x9908b0df
HOST, PORT = "archive.cryptohack.org", 63222

def temper(y):
    y &= 0xffffffff
    y ^= y >> 11
    y ^= (y << 7) & 0x9d2c5680
    y ^= (y << 15) & 0xefc60000
    y ^= y >> 18
    return y

def untemper(y):
    y &= 0xffffffff
    y ^= y >> 18
    x2 = y
    for _ in range(4): x2 = y ^ ((x2 << 15) & 0xefc60000)
    x = x2 & 0xffffffff
    x2 = x
    for _ in range(6): x2 = x ^ ((x2 << 7) & 0x9d2c5680)
    x = x2 & 0xffffffff
    x2 = x
    for _ in range(6): x2 = x ^ (x2 >> 11)
    return x2 & 0xffffffff

def mt2020(seed):
    r = random.Random(seed)
    return [r.getrandbits(32) for _ in range(2020)]

def solve_target(o1396, o2018, msb2019=0):
    # CPython emits word s_624+j at output j (state index starts at 624, so the
    # FIRST output comes after the first twist). Target = output 2019 = word
    # s_2643 = s_2020 ^ ((s_2642 & 0x7fffffff) >> 1) ^ MAGIC*(s_2642&1) ^ msb(s_2019)<<30
    w2020 = untemper(o1396)
    w2642 = untemper(o2018)
    s2643 = w2020 ^ ((w2642 & 0x7fffffff) >> 1) ^ (MAGIC if (w2642 & 1) else 0) ^ (msb2019 << 30)
    return temper(s2643)

def local_check():
    s0 = list(random.Random(42).getstate()[1][:624])
    s = list(s0)
    for k in range(624, 2020):
        y = (s[(k-624) % 624] & 0x80000000) | (s[(k-1) % 624] & 0x7fffffff)
        s[k % 624] = s[(k-623) % 624] ^ (y >> 1) ^ (MAGIC if y & 1 else 0)
    outs = mt2020(42)
    assert temper(s[0]) == outs[0]
    assert untemper(outs[1396]) == s[2020 % 624] and untemper(outs[2018]) == s[2642 % 624]
    wins = sum(solve_target(o[1396], o[2018]) == o[2019] for o in (mt2020(t) for t in range(200)))
    print(f"local self-test: {wins}/200 (expect ~100)")
    return wins

def run_once(try_msb=0):
    ss = socket.create_connection((HOST, PORT), timeout=10)
    ss.settimeout(10)
    ss.sendall(b"1396\n2018\n")
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
    nums = re.findall(r"^(\d+)$", "\n".join(lines), re.M)
    if len(nums) != 2:
        ss.close()
        return None, "\n".join(lines)
    guess = solve_target(int(nums[0]), int(nums[1]), try_msb)
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
    return guess, "\n".join(lines) + "\n" + rest.decode(errors="replace")

if __name__ == "__main__":
    if "--local" in sys.argv:
        local_check()
        sys.exit(0)
    if local_check() == 0:
        print("WARNING: 0/200 local wins")
    for n in range(1, 61):
        g, txt = run_once(0)
        if g is None:
            print(n, "bad:", txt[:120].replace("\n", "|")); time.sleep(1.0); continue
        if "crypto{" in txt:
            m = re.search(r"crypto\{[^}\n]*\}", txt)
            print("WIN session", n, "->", m.group(0))
            open("flag_2020-tetctf2020.txt", "w").write(m.group(0))
            sys.exit(0)
        print(n, "miss")
        time.sleep(0.7)
    print("no win in budget")
