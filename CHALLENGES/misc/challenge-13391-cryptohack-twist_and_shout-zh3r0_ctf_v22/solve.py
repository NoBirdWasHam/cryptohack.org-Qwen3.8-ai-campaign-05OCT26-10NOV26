#!/usr/bin/env python3
# twist_and_shout (Zh3r0 CTF V2) — archive.cryptohack.org:46347
# Server: random.setstate(full state containing flag), print 624 getrandbits(32).
# Attack: untemper all 624 outputs -> post-twist array N; untwist (in-place
# CPython twist) -> original state bytes. Only low31(A[0]) is lost; if the flag
# overlaps word 0 we reconnect (flag position is re-randomised per connection).
import socket, re, sys

U, L, MA = 0x80000000, 0x7fffffff, 0x9908b0df

def inv_rshift_xor(y, s):
    x = y; m = s
    while m < 32: x ^= y >> m; m *= 2
    return x & 0xffffffff

def inv_lshift_xor(y, s, mask):
    x = [(y >> i) & 1 for i in range(32)]
    for i in range(s, 32):
        if (mask >> i) & 1: x[i] ^= x[i - s]
    return sum(x[i] << i for i in range(32)) & 0xffffffff

def untemper(y):
    x = inv_rshift_xor(y, 18)
    x = inv_lshift_xor(x, 15, 0xefc60000)
    x = inv_lshift_xor(x, 7, 0x9d2c5680)
    return inv_rshift_xor(x, 11)

def inv_f(z):
    b = (z >> 31) & 1
    return (((z ^ (MA * b)) << 1) | b) & 0xffffffff

def untwist(N):
    O = [0] * 624
    for i in range(227, 624):
        y = inv_f(N[i] ^ N[i - 227]) if i < 623 else inv_f(N[623] ^ N[396])
        O[i] |= y & U
        if i < 623: O[i + 1] |= y & L
    for i in range(0, 227):
        y = inv_f(N[i] ^ O[i + 397])
        O[i] |= y & U
        O[i + 1] |= y & L
    return O

def recover(words):
    N = [untemper(w) for w in words]
    O = untwist(N)
    b = b"".join(w.to_bytes(4, "big") for w in O)
    return O, b

FLAG_RE = re.compile(rb"zh3r0\{[^}]*\}")

def local_test(n=20):
    import os, random
    ok = 0
    for t in range(n):
        flag = b"zh3r0{fake_flag_%d_padding_padding}" % t
        state_len = 624 * 4
        right_pad = random.randint(0, state_len - len(flag))
        left_pad = state_len - len(flag) - right_pad
        sb = os.urandom(left_pad) + flag + os.urandom(right_pad)
        state = tuple(int.from_bytes(sb[i:i+4], "big") for i in range(0, state_len, 4))
        random.setstate((3, state + (624,), None))
        outs = [random.getrandbits(32) for _ in range(624)]
        O, b = recover(outs)
        got = FLAG_RE.search(b)
        if got and got.group() == flag:
            ok += 1
        elif left_pad < 4:
            print(f"  trial {t}: flag overlaps word0 (left_pad={left_pad}) -> would reconnect")
        else:
            print(f"  trial {t}: FAIL left_pad={left_pad} recovered={got}")
    print(f"local: {ok}/{n} exact recoveries")
    return ok

def live(trials=6):
    for t in range(trials):
        s = socket.create_connection(("archive.cryptohack.org", 46347), timeout=30)
        s.settimeout(30)
        buf = b""
        while buf.count(b"\n") < 624:
            d = s.recv(65536)
            if not d: break
            buf += d
        s.close()
        lines = [l for l in buf.decode().split() if l.strip()]
        if len(lines) < 624:
            print(f"trial {t}: only {len(lines)} tokens: {buf[:120]!r}"); continue
        words = [int(x) for x in lines[:624]]
        O, b = recover(words)
        m = FLAG_RE.search(b)
        if m:
            print("FLAG:", m.group().decode())
            return m.group().decode()
        print(f"trial {t}: no flag match (word0 overlap? head={b[:16]!r}) — reconnecting")
    return None

if __name__ == "__main__":
    if "--test" in sys.argv:
        sys.exit(0 if local_test() > 0 else 1)
    live()
