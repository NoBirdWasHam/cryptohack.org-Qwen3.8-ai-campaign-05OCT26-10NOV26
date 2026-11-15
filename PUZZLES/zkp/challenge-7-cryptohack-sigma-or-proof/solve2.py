#!/usr/bin/env python3
"""sigma-or-proof (75 pts, zkp) — archive.cryptohack.org:11840

Three phases:
1. correctness:      WE are the prover. chal.py ships w0 (w1 redacted).
                     Honest side 0 (know w0), simulate side 1.
2. specialSoundness: WE are the verifier. Server prints two transcripts with
                     same (a0,a1), different challenges. Extract witness:
                     on the side where e != e*, w = (z-z*)/(e-e*) mod q.
3. SHVZK:            WE simulate a full accepting transcript for a given s
                     without any witness (SHVZK simulator).

Verification equations (server): g^z_i == a_i * y_i^e_i (mod p); e0 ^ e1 == s (integer xor).
NOTE: server input() prompts ("a0:" etc.) carry no newline — parse with regex grabs,
never line-splitting.
"""
import random
import re
import socket
import time

HOST, PORT = "archive.cryptohack.org", 11840

# --- params.py (provided challenge file) ---
p = 0x1ed344181da88cae8dc37a08feae447ba3da7f788d271953299e5f093df7aaca987c9f653ed7e43bad576cc5d22290f61f32680736be4144642f8bea6f5bf55ef
q = 0xf69a20c0ed4465746e1bd047f57223dd1ed3fbc46938ca994cf2f849efbd5654c3e4fb29f6bf21dd6abb662e911487b0f9934039b5f20a23217c5f537adfaaf7
g = 2
# w0 from provided chal.py (w1 = REDACTED)
w0 = 0x5a0f15a6a725003c3f65238d5f8ae4641f6bf07ebf349705b7f1feda2c2b051475e33f6747f4c8dc13cd63b9dd9f0d0dd87e27307ef262ba68d21a238be00e83
y0 = 0x514c8f56336411e75d5fa8c5d30efccb825ada9f5bf3f6eb64b5045bacf6b8969690077c84bea95aab74c24131f900f83adf2bfe59b80c5a0d77e8a9601454e5
y1 = 0x1ccda066cd9d99e0b3569699854db7c5cf8d0e0083c4af57d71bf520ea0386d67c4b8442476df42964e5ed627466db3da532f65a8ce8328ede1dd7b35b82ed617

E_MAX = 2 ** 511  # challenges sampled in [0, 2^511)


class Conn:
    def __init__(self):
        self.s = socket.create_connection((HOST, PORT), timeout=120)
        self.buf = b""

    def _fill(self):
        d = self.s.recv(65536)
        if not d:
            raise EOFError("server closed")
        self.buf += d

    def grab(self, regex, timeout=60):
        """Accumulate until regex matches the buffer; return group(1), consume up to end of match."""
        t0 = time.time()
        pat = re.compile(regex.encode())
        while True:
            m = pat.search(self.buf)
            if m:
                val = m.group(1).decode()
                self.buf = self.buf[m.end():]
                return val
            if time.time() - t0 > timeout:
                raise TimeoutError(f"no match for {regex!r} in {self.buf[:400]!r}")
            self._fill()

    def grab_text(self, regex, timeout=60):
        t0 = time.time()
        pat = re.compile(regex.encode())
        while True:
            m = pat.search(self.buf)
            if m:
                self.buf = self.buf[m.end():]
                return m.group(0).decode()
            if time.time() - t0 > timeout:
                raise TimeoutError(f"no match for {regex!r}")
            self._fill()

    def send_int(self, v):
        self.s.sendall(f"{v}\n".encode())


def main():
    conn = Conn()
    conn.grab_text(r"Correctness!")
    conn.grab_text(r"Prove to me")

    # ---- Phase 1: correctness, honest on side 0 (we know w0) ----
    assert pow(g, w0, p) == y0, "sanity: g^w0 != y0"
    r = random.randrange(q)
    a0 = pow(g, r, p)                      # honest commitment, side 0
    e1 = random.randrange(E_MAX)            # simulated side 1
    z1 = random.randrange(q)
    a1 = pow(pow(y1, e1, p), -1, p) * pow(g, z1, p) % p
    conn.send_int(a0)
    conn.send_int(a1)
    s = int(conn.grab(r"verifier sends s = (\d+)(?=\s)"))
    e0 = s ^ e1
    z0 = (r + e0 * w0) % q
    conn.send_int(e0)
    conn.send_int(e1)
    conn.send_int(z0)
    conn.send_int(z1)
    print("phase 1 (correctness) accepted", flush=True)

    # ---- Phase 2: special soundness, we extract ----
    conn.grab_text(r"i will now prove knowledge")
    y0s = int(conn.grab(r"y0 = (\d+)(?=\s)"))
    y1s = int(conn.grab(r"y1 = (\d+)(?=\s)"))
    conn.grab_text(r"Special Soundness!")
    conn.grab_text(r"transcript 1:")
    a0 = int(conn.grab(r"a0 = (\d+)(?=\s)"))
    a1 = int(conn.grab(r"a1 = (\d+)(?=\s)"))
    s1 = int(conn.grab(r"(?<!\*)s = (\d+)(?=\s)"))
    e0 = int(conn.grab(r"e0 = (\d+)(?=\s)"))
    e1 = int(conn.grab(r"e1 = (\d+)(?=\s)"))
    z0 = int(conn.grab(r"z0 = (\d+)(?=\s)"))
    z1 = int(conn.grab(r"z1 = (\d+)(?=\s)"))
    conn.grab_text(r"transcript 2:")
    a0b = int(conn.grab(r"a0 = (\d+)(?=\s)"))
    a1b = int(conn.grab(r"a1 = (\d+)(?=\s)"))
    s2 = int(conn.grab(r"s\* = (\d+)(?=\s)"))
    e0b = int(conn.grab(r"e0\* = (\d+)(?=\s)"))
    e1b = int(conn.grab(r"e1\* = (\d+)(?=\s)"))
    z0b = int(conn.grab(r"z0\* = (\d+)(?=\s)"))
    z1b = int(conn.grab(r"z1\* = (\d+)(?=\s)"))
    dbg = dict(y0s=y0s, y1s=y1s, a0=a0, a1=a1, s1=s1, e0=e0, e1=e1, z0=z0, z1=z1,
               a0b=a0b, a1b=a1b, s2=s2, e0b=e0b, e1b=e1b, z0b=z0b, z1b=z1b)
    open("phase2_debug.json", "w").write(str(dbg).replace("'", '"'))
    print("t1s0", pow(g, z0, p) == (a0 * pow(y0s, e0, p)) % p,
          "t1s1", pow(g, z1, p) == (a1 * pow(y1s, e1, p)) % p,
          "t2s0", pow(g, z0b, p) == (a0b * pow(y0s, e0b, p)) % p,
          "t2s1", pow(g, z1b, p) == (a1b * pow(y1s, e1b, p)) % p, flush=True)
    print("e0==e0b", e0 == e0b, "e1==e1b", e1 == e1b, "z0==z0b", z0 == z0b, "z1==z1b", z1 == z1b, flush=True)
    assert (a0, a1) == (a0b, a1b), "commitments must match"

    wb = None
    # side 0 extractable iff e0 != e0*
    if e0 != e0b:
        w_cand = (z0 - z0b) * pow(e0 - e0b, -1, q) % q
        if pow(g, w_cand, p) == y0s:
            wb = w_cand
            print(f"extracted witness from side 0: {wb}", flush=True)
    if wb is None and e1 != e1b:
        w_cand = (z1 - z1b) * pow(e1 - e1b, -1, q) % q
        if pow(g, w_cand, p) == y1s:
            wb = w_cand
            print(f"extracted witness from side 1: {wb}", flush=True)
    assert wb is not None, "extraction failed"
    conn.send_int(wb)
    conn.grab_text(r"Well done! You proved extraction!")
    print("phase 2 (extraction) accepted", flush=True)

    # ---- Phase 3: SHVZK simulator, given s ----
    conn.grab_text(r"Finally, show me you can simulate proofs!")
    y0t = int(conn.grab(r"y0 = (\d+)(?=\s)"))
    y1t = int(conn.grab(r"y1 = (\d+)(?=\s)"))
    st = int(conn.grab(r"give me satisfying transcript for s = (\d+)(?=\s)"))
    e0t = random.randrange(E_MAX)
    z0t = random.randrange(q)
    a0t = pow(pow(y0t, e0t, p), -1, p) * pow(g, z0t, p) % p
    e1t = st ^ e0t
    z1t = random.randrange(q)
    a1t = pow(pow(y1t, e1t, p), -1, p) * pow(g, z1t, p) % p
    conn.send_int(a0t)
    conn.send_int(a1t)
    conn.send_int(e0t)
    conn.send_int(e1t)
    conn.send_int(z0t)
    conn.send_int(z1t)
    conn.grab_text(r"well done!")
    flag = conn.grab_text(r"crypto\{[^\}]*\}")
    print("FLAG:", flag, flush=True)
    return flag


if __name__ == "__main__":
    main()
