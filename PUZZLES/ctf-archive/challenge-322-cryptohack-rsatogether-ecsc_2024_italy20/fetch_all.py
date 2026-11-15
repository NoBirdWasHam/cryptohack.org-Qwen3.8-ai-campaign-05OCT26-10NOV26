# Single-connection fetch: n,e + all 101 'yours' shares (menu 2, k=1..101) + flag ct (menu 3).
import socket, time, select, re, json, sys

HOST, PORT = "archive.cryptohack.org", 33824
T0 = time.time()

def rd(s, stop, t=20):
    d = b""; end = time.time() + t
    while time.time() < end:
        r, _, _ = select.select([s], [], [], max(0.05, end - time.time()))
        if not r: break
        ch = s.recv(65536)
        if not ch: break
        d += ch
        if stop(d): return d
    return d

def attempt():
    s = socket.create_connection((HOST, PORT), timeout=40)
    init = rd(s, lambda d: b"n = " in d and b"e = " in d and b"key?" in d, 30)
    n = int(re.search(rb"n = (\d+)", init).group(1))
    e = int(re.search(rb"e = (\d+)", init).group(1))
    s.sendall(b"5\n"); rd(s, lambda d: b"> " in d, 15)   # startup share, discard
    u = {}
    for k in range(1, 102):
        s.sendall(b"2\n")
        a = rd(s, lambda d: b"key?" in d, 15)
        assert b"key?" in a, f"k={k} no friends prompt: {a[:120]!r}"
        s.sendall(f"{k}\n".encode())
        a = rd(s, lambda d: b"> " in d, 20)
        m = re.search(rb"part: (\d+)", a)
        assert m, f"k={k} no part: {a[:200]!r}"
        u[k] = int(m.group(1))
        if k % 25 == 0: print("got", k, round(time.time()-T0, 1), flush=True)
    s.sendall(b"3\n")
    bye = rd(s, lambda d: re.search(rb"you!\n\d{100,}", d) is not None, 25)
    m = re.search(rb"you!\n(\d+)", bye)
    assert m, f"no ct: {bye[:200]!r}"
    ct = int(m.group(1))
    s.close()
    return n, e, u, ct

for tr in range(3):
    try:
        n, e, u, ct = attempt()
        json.dump({"n": str(n), "e": str(e), "u": {str(k): v for k, v in u.items()}, "ct": str(ct)},
                  open("live_data.json", "w"))
        print("DONE n bits:", n.bit_length(), "ct bits:", ct.bit_length(), "shares:", len(u))
        sys.exit(0)
    except Exception as ex:
        print("attempt", tr, "failed:", repr(ex), flush=True)
        time.sleep(3)
sys.exit(1)
