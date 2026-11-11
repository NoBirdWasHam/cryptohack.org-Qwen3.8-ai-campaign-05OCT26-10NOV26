#!/usr/bin/env python3
# OffTopic (ECSC 2024 Italy) — malicious-receiver OT break. LIVE solver.
# H = infinity (O) kills all r*H re-randomization noise, so with our C.S = K*G
# the server answer satisfies res.S = (m0*(1-K) + m1*K)*G exactly; K=10^9 makes
# the map injective on digits -> both m0,m1 readable in one round.
import json, sys, socket

K = 10**9
GX = 0x6b17d1f2e12c4247f8bce6e563a440f277037d812deb33a0f4a13945d898c296
GY = 0x4fe342e2fe1a7f9b8ee7eb4a7c0f9e162bce33576b315ececbb6406837bf51f5
Q  = 0xffffffff00000000ffffffffffffffffbce6faada7179e84f3b9cac2fc632551

from Crypto.PublicKey.ECC import EccPoint
G = EccPoint(GX, GY)
KS = K*G

TABLE = {}
for m0 in range(10):
    for m1 in range(10):
        v = (m0*(1-K) + m1*K) % Q
        if v == 0:
            TABLE[(0, 0)] = None
            continue
        p = v*G
        TABLE[(int(p.x), int(p.y))] = (m0, m1)
assert len(TABLE) == 100

def main(host, port):
    s = socket.create_connection((host, port), timeout=110)
    buf = b""
    def readuntil(marker):
        nonlocal buf
        marker = marker.encode()
        while marker not in buf:
            d = s.recv(4096)
            if not d: raise EOFError(f"closed; buf={buf!r}")
            buf += d
        i = buf.index(marker) + len(marker)
        out, buf = buf[:i], buf[i:]
        return out.decode(errors="replace")
    def send(x): s.sendall(x.encode() + b"\n")

    print(readuntil("ready?").strip(), flush=True)
    send(json.dumps({"Hx": 0, "Hy": 0}))
    readuntil("choice bit: ")
    for r in range(128):
        send(json.dumps({"Rx": GX, "Ry": GY, "Sx": int(KS.x), "Sy": int(KS.y)}))
        out = readuntil("messages: ")
        res = json.loads(out[out.index("{"):out.index("}")+1])
        key = (res["Sx"], res["Sy"])
        pair = TABLE.get(key)
        if pair is None and key != (0, 0):
            raise RuntimeError(f"round {r}: no match {res}")
        if key == (0, 0): pair = (0, 0)
        send(json.dumps({"m0": pair[0], "m1": pair[1]}))
        print(f"round {r:3d}: m0={pair[0]} m1={pair[1]}", flush=True)
    # flag line follows the 128th answer
    s.settimeout(30)
    flag = b""
    try:
        while True:
            d = s.recv(4096)
            if not d: break
            flag += d
    except socket.timeout:
        pass
    print("FINAL:", flag.decode(errors="replace").strip(), flush=True)
    return flag.decode(errors="replace")

if __name__ == "__main__":
    host, port = "archive.cryptohack.org", 40704
    if "--local-sock" in sys.argv:
        import subprocess, os, threading
        env = dict(os.environ, FLAG="TEST{local_selftest}")
        proc = subprocess.Popen([sys.executable, "-u", "offtopic.py"],
                                stdin=subprocess.PIPE, stdout=subprocess.PIPE, env=env)
        # bridge: socketpair-like via stdin/stdout bytes
        class Bridge:
            def __init__(self, p): self.p = p
            def recv(self, n):
                d = self.p.stdout.read(1)
                if not d: raise EOFError
                while len(d) < n and d[-1:] != b"\n":
                    c = self.p.stdout.read(1)
                    if not c: break
                    d += c
                return d
            def sendall(self, b): self.p.stdin.write(b); self.p.stdin.flush()
            def settimeout(self, t): pass
            def close(self): pass
        class BS:
            def __init__(self, p): self.b = Bridge(p)
            def recv(self, n):
                d = self.b.recv(n)
                if not d: raise EOFError
                return d
            def sendall(self, x): self.b.sendall(x)
            def settimeout(self, t): pass
        bs = BS(proc)
        # monkey-patch connection
        import builtins
        globals()["socket_create"] = None
        orig = socket.create_connection
        socket.create_connection = lambda *a, **k: bs
        out = main("", 0)
        print("LOCAL:", out)
    else:
        main(host, port)
