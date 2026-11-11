#!/usr/bin/env python
"""dh_static (100 pts) — Bob reuses a STATIC secret key b across ALL sessions.

Protocol (socket.cryptohack.org:13373):
  Phase 1 (passive, fresh per connection):
    Intercepted from Alice: {p, g=2, A}      (A = g^a, fresh a)
    Intercepted from Bob:   {B}              (B = g^b, STATIC — same every
                                              connection, verified live)
    Intercepted from Alice: {iv, encrypted}  (flag, key = SHA1(str(A^b))[:16])
  Phase 2: "Bob connects to you, send him some parameters"
    I send {p, g, A}; Bob replies {"B": g^b mod p} and a message under
    SHA1(str(A^b mod p))[:16]. Bob uses MY p and g.

Attack — the static key is the whole game:
  The flag was encrypted with s = A^b from the intercepted conversation.
  In phase 2 Bob computes his public value as (my g)^b. Choose g = A!
  Then Bob returns B2 = A^b mod P = s — the very shared secret, in the clear.
  (If b were fresh per session, phase 2's A^b would be a different secret;
  the static b is what makes the intercepted secret derivable.)
  key = SHA1(str(s))[:16] -> AES-128-CBC decrypt -> flag.

No DLP needed: P is a 1536-bit SAFE prime (P-1 = 2q, q 1535-bit prime), so
B = g^b is otherwise infeasible.
"""
import socket, json, time, hashlib
from Crypto.Cipher import AES

P = 0xffffffffffffffffc90fdaa22168c234c4c6628b80dc1cd129024e088a67cc74020bbea63b139b22514a08798e3404ddef9519b3cd3a431b302b0a6df25f14374fe1356d6d51c245e485b576625e7ec6f44c42e9a637ed6b0bff5cb6f406b7edee386bfb5a899fa5ae9f24117c4b1fe649286651ece45b3dc2007cb8a163bf0598da48361c55d39a69163fa8fd24cf5f83655d23dca3ad961c62f356208552bb9ed529077096966d670c354e4abc9804f1746c08ca237327ffffffffffffffff
B_static = 0x8d79b69390f639501d81bdce911ec9defb0e93d421c02958c8c8dd4e245e61ae861ef9d32aa85dfec628d4046c403199297d6e17f0c9555137b5e8555eb941e8dcfd2fe5e68eecffeb66c6b0de91eb8cf2fd0c0f3f47e0c89779276fa7138e138793020c6b8f834be20a16237900c108f23f872a5f693ca3f93c3fd5a853dfd69518eb4bab9ac2a004d3a11fb21307149e8f2e1d8e1d7c85d604aa0bee335eade60f191f74ee165cd4baa067b96385aa89cbc7722e7426522381fc94ebfa8ef0


def main():
    s = socket.create_connection(("socket.cryptohack.org", 13373), timeout=30)
    s.settimeout(25)
    buf = b""

    def drain(t=6):
        nonlocal buf
        t0 = time.time()
        while time.time() - t0 < t:
            try:
                d = s.recv(65536)
            except socket.timeout:
                break
            if not d:
                break
            buf += d
        lines = []
        while b"\n" in buf:
            line, buf = buf.split(b"\n", 1)
            lines.append(line.decode().strip())
        return lines

    # Phase 1: eavesdrop
    A = iv = ct = B_conn = None
    for l in drain(6):
        print("S:", l[:110])
        if l.startswith("Intercepted from Alice") and '"A"' in l:
            A = json.loads(l.split("Intercepted from Alice:", 1)[1])["A"]
        elif l.startswith("Intercepted from Bob:"):
            B_conn = int(json.loads(l.split("Intercepted from Bob:", 1)[1])["B"], 16)
        elif l.startswith("Intercepted from Alice") and '"iv"' in l:
            o = json.loads(l.split("Intercepted from Alice:", 1)[1])
            iv, ct = o["iv"], o["encrypted"]
    assert A and iv and ct
    assert B_conn == B_static, "Bob's key is no longer static?!"
    print("B static across connections: verified")

    # Phase 2: choose g = A. Bob returns g^b = A^b = the intercepted secret.
    s.sendall((json.dumps({"p": hex(P), "g": A, "A": "0x1"}) + "\n").encode())
    print("C: p=P, g=A (Alice's public value), A=1")
    shared = None
    for l in drain(6):
        print("S:", l[:130])
        b = l.find("{")
        if b >= 0:
            try:
                o = json.loads(l[b:])
                if "B" in o:
                    shared = int(o["B"], 16)
            except Exception:
                pass
    assert shared is not None and shared != 0
    print("shared secret s = A^b =", shared)

    key = hashlib.sha1(str(shared).encode()).digest()[:16]
    pt = AES.new(key, AES.MODE_CBC, bytes.fromhex(iv)).decrypt(bytes.fromhex(ct))
    n = pt[-1]
    if 1 <= n <= 16 and pt[-n:] == bytes([n]) * n:
        pt = pt[:-n]
    print("PLAINTEXT:", pt.decode("utf-8", "replace"))
    s.close()


if __name__ == "__main__":
    main()
