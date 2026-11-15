import random, socket, time, sys

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
    w2020 = untemper(o1396)   # word s_2020 (output j emits word s_624+j)
    w2642 = untemper(o2018)   # word s_2642
    s2643 = w2020 ^ ((w2642 & 0x7fffffff) >> 1) ^ (MAGIC if (w2642 & 1) else 0) ^ (msb2019 << 30)
    return temper(s2643)

# --- local end-to-end validation ---
# verify word/output mapping: first output == temper(state[0] after twist)
s0 = list(random.Random(42).getstate()[1][:624])
s = list(s0)
for k in range(624, 2020):
    y = (s[(k-624) % 624] & 0x80000000) | (s[(k-1) % 624] & 0x7fffffff)
    s[k % 624] = s[(k-623) % 624] ^ (y >> 1) ^ (MAGIC if y & 1 else 0)
outs = mt2020(42)
assert temper(s[624 % 624]) == outs[0]
assert untemper(outs[1396]) == s[2020 % 624] and untemper(outs[2018]) == s[2642 % 624]
assert temper(s[2019 % 624]) == outs[1395]
wins = sum(solve_target(o[1396], o[2018]) == o[2019] for o in (mt2020(t) for t in range(200)))
print(f"local self-test: {wins}/200 wins (expect ~100)")

def session(guess):
    ss = socket.create_connection((HOST, PORT), timeout=10)
    ss.settimeout(15)
    ss.sendall(f"1396\n2018\n{guess}\n".encode())
    data = b""
    try:
        while True:
            b = ss.recv(65536)
            if not b: break
            data += b
    except socket.timeout:
        pass
    ss.close()
    return data.decode(errors="replace")

def run_once():
    ss = socket.create_connection((HOST, PORT), timeout=10)
    ss.settimeout(15)
    ss.sendall(b"1396\n2018\n")
    ss.sendall(b"0\n")  # placeholder guess; real check below
    data = b""
    try:
        while True:
            b = ss.recv(65536)
            if not b: break
            data += b
    except socket.timeout:
        pass
    ss.close()
    txt = data.decode(errors="replace")
    import re
    nums = re.findall(r"^(\d+)$", txt, re.M)
    if len(nums) != 2:
        return None, txt
    guess = solve_target(int(nums[0]), int(nums[1]), 0)
    flag = "crypto{" in txt
    return guess, txt

if __name__ == "__main__":
    if "--local" in sys.argv:
        sys.exit(0)
    for n in range(1, 61):
        g, txt = run_once()
        if g is None:
            print(n, "bad response:", txt[:200]); time.sleep(2); continue
        # NOTE: guess can only be used on a FRESH connection? No - the guess line
        # must be sent BEFORE output is known. Restructure: two-phase in one conn.
        print(n, "computed guess", g, "flag?", "crypto{" in txt)
        break
