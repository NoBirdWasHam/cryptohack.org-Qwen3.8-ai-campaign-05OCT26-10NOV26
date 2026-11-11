#!/usr/bin/env python3
# OffTopic (ECSC 2024 Italy) — malicious-receiver OT break.
# We choose the receiver pubkey H = O (infinity). Then every re-randomization
# term r*H in Ciphertext.from_pt vanishes, so for our ciphertext C with
# S_C = k*G the server's homomorphic answer
#   res = m0*(1-C) + m1*C
# satisfies res.S = (m0*(1-k) + m1*k) * G  (no noise!). With k = 10^9 the map
# (m0,m1) -> v = m0*(1-k)+m1*k mod q is injective on [0,9]^2, so one round
# leaks BOTH digits — breaking OT soundness. H=O passes `assert H != G`.
import json, sys, socket

K = 10**9

def make_io(sock=None, proc=None):
    if sock is not None:
        buf = b""
        def readuntil(marker):
            nonlocal buf
            while marker not in buf:
                d = sock.recv(4096)
                if not d: raise EOFError("closed")
                buf += d
            i = buf.index(marker) + len(marker)
            line, buf = buf[:i], buf[i:]
            return line.decode()
        def send(s): sock.sendall(s.encode() + b"\n")
    else:
        def readuntil(marker):
            line = proc.stdout.readline()
            if not line: raise EOFError("closed")
            return line
        def send(s):
            proc.stdin.write(s + "\n"); proc.stdin.flush()
    return readuntil, send

def solve(io, verbose=True):
    readuntil, send = io
    readuntil("ready?")
    send(json.dumps({"Hx": 0, "Hy": 0}))          # H = point at infinity
    readuntil("choice bit: ")
    for r in range(128):
        send(json.dumps({"Rx": GX, "Ry": GY, "Sx": int(KS.x), "Sy": int(KS.y)}))
        out = readuntil("messages: ")
        res = json.loads(out[:out.index("Send the recovered")].strip().split("\n")[-1])
        found = None
        for m0 in range(10):
            for m1 in range(10):
                v = (m0*(1-K) + m1*K) % Q
                if v == 0:
                    pt = (0, 0)                    # infinity
                else:
                    p = v*G
                    pt = (int(p.x), int(p.y))
                if pt[0] == res["Sx"] and pt[1] == res["Sy"]:
                    found = (m0, m1); break
            if found: break
        if found is None:
            raise RuntimeError(f"round {r}: no match, res={res}")
        m0, m1 = found
        if verbose: print(f"round {r}: m0={m0} m1={m1}", flush=True)
        send(json.dumps({"m0": m0, "m1": m1}))
    final = b"" if True else None
    # after 128th answer the flag line follows
    line = proc_or_sock_read(readuntil)
    return line

def proc_or_sock_read(readuntil):
    # read until EOF-ish: read one nonempty line
    while True:
        s = readuntil("\n")
        s = s.strip()
        if s: return s

if __name__ == "__main__":
    from Crypto.PublicKey.ECC import EccPoint
    GX = 0x6b17d1f2e12c4247f8bce6e563a440f277037d812deb33a0f4a13945d898c296
    GY = 0x4fe342e2fe1a7f9b8ee7eb4a7c0f9e162bce33576b315ececbb6406837bf51f5
    Q  = 0xffffffff00000000ffffffffffffffffbce6faada7179e84f3b9cac2fc632551
    G = EccPoint(GX, GY)
    KS = K*G

    if "--local" in sys.argv:
        import subprocess, os
        env = dict(os.environ, FLAG="TEST{local_selftest}")
        proc = subprocess.Popen([sys.executable, "-u", "offtopic.py"], stdin=subprocess.PIPE,
                                stdout=subprocess.PIPE, text=True, env=env)
        line = solve(make_io(proc=proc), verbose=False)
        print("LOCAL FLAG:", line)
        assert line == "TEST{local_selftest}", line
        print("LOCAL SELF-TEST OK")
    else:
        s = socket.create_connection(("archive.cryptohack.org", 40704), timeout=90)
        readuntil, send = make_io(sock=s)
        # inline variant of solve() for socket (flag = last line read)
        readuntil("ready?")
        send(json.dumps({"Hx": 0, "Hy": 0}))
        readuntil("choice bit: ")
        for r in range(128):
            send(json.dumps({"Rx": GX, "Ry": GY, "Sx": KS.x, "Sy": KS.y}))
            out = readuntil("messages: ")
            res = json.loads(out[:out.index("Send the recovered")].strip().split("\n")[-1])
            found = None
            for m0 in range(10):
                for m1 in range(10):
                    v = (m0*(1-K) + m1*K) % Q
                    pt = (0, 0) if v == 0 else None
                    if pt is None:
                        p = v*G; pt = (int(p.x), int(p.y))
                    if pt[0] == res["Sx"] and pt[1] == res["Sy"]:
                        found = (m0, m1); break
                if found: break
            if found is None: raise RuntimeError(f"round {r}: no match {res}")
            send(json.dumps({"m0": found[0], "m1": found[1]}))
            print(f"round {r}: {found}", flush=True)
        # read flag
        rest = s.recv(4096).decode()
        print("FLAG LINE:", rest.strip())
