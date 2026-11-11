#!/usr/bin/env python3
# Probe the archive listener: fingerprint which validation the server's
# pycryptodome does (construct checks? DSS.new L/N check?) via error messages.
import socket, sys

def session(q, p, g, seed="1337", sign=None, timeout=25):
    s = socket.create_connection(("archive.cryptohack.org", 2783), timeout=timeout)
    f = s.makefile("rw", encoding="utf-8", errors="replace")
    def ask(sub):
        data = ""
        while sub not in data:
            ch = f.read(1)
            if not ch:
                return data + "<<EOF>>"
            data += ch
        return data
    def send(line):
        f.write(line + "\n"); f.flush()
    out = []
    out.append(ask("q = ")); send(str(q))
    out.append(ask("p = ")); send(str(p))
    out.append(ask("g = ")); send(str(g))
    out.append(ask("hex")); send(seed)
    # wait for either "y = " (success) or error+EOF
    data = ""
    while True:
        ch = f.read(1)
        if not ch:
            data += "<<EOF>>"; break
        data += ch
        if "y = " in data:
            # read rest of line
            while not data.rstrip().endswith(("=", "\n")) or not data.endswith("\n"):
                ch = f.read(1)
                if not ch: data += "<<EOF>>"; break
                data += ch
                if data.endswith("\n"): break
            break
        if data.endswith("<<EOF>>"): break
    out.append(data)
    if sign is not None and "y = " in data:
        send(sign)
        rest = f.read()
        out.append(rest)
    s.close()
    return "".join(out)

if __name__ == "__main__":
    from sympy import isprime
    # probe A: small q (32-bit) safe prime — tests DSS.new (L,N) check
    q = 3329505089; p = 6659010179; g = 4
    print("PROBE A (small q):", repr(session(q, p, g)))
    # probe B: q=2, 1024-bit prime p, g=p-1 (order 2 = q)
    p2 = (1 << 1023) | ((1 << 1023) - 1) // 3 * 3 + 1
    while not isprime(p2):
        p2 += 2
    print("PROBE B (q=2):", repr(session(2, p2, p2 - 1)))
