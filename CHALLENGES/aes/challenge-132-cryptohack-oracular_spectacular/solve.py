#!/usr/bin/env python3
"""oracular_spectacular solver.

Attack: CBC padding oracle with a 40%-truth lying oracle.
 - message = 32 hex chars (2 AES blocks, no padding on encrypt).
 - unpad oracle: result = good XOR (rand>0.4)  -> P(True|valid)=0.4, P(True|invalid)=0.6.
 - Per byte b (right-to-left), set suffix so padding length p=16-b is valid iff
   byte b decrypts to p. Hex charset => only 16 candidate XOR values.
 - Identify the good candidate with greedy argmax-LLR, stop when top1-top2 >= G.
 - Recover block2 via c2 XOR deltas; block1 via IV deltas (single-block ct iv'||c1).
 - Verify each block by crafting pt = 0x10*16 (valid padding) and measuring
   frac_true ~ 0.4 (vs 0.6 if any byte wrong).
Run LOCAL=1 to test against a local in-process stub of 13423.py.
"""
import os, sys, time

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)

HEX = b"0123456789abcdef"
G = 24            # LLR gap (in F-T units) to accept a byte
CAPMAX = 1200     # max queries per byte (starved bytes need room to self-correct)
MIN = 100         # guaranteed floor per remaining byte
BUD = 11500       # planning budget (server hard-kills at 12000 unpad queries)
ABORT_AT = 11800  # hard client-side abort

def xor(a, b):
    return bytes(x ^ y for x, y in zip(a, b))

class Oracle:
    def __init__(self, client):
        self.c = client
        self.n = 0
    def ask_multi(self, cts):
        if self.n + len(cts) > ABORT_AT:
            raise RuntimeError("budget")
        res = self.c.unpad_batch(cts, chunk=6)
        self.n += len(cts)
        return res
    def ask(self, ct):
        return self.ask_multi([ct])[0]

class ByteRecover:
    """One byte position: 16 hex candidates, greedy-LLR with dynamic cap."""
    def __init__(self, b, known, mkq, cap_fn):
        self.b = b; self.known = known; self.mkq = mkq; self.cap_fn = cap_fn
        self.p = 16 - b
        self.cands = [c ^ self.p for c in HEX]
        self.F = [0]*16; self.T = [0]*16
        self.q = 0; self.done = False; self.cur = None
    def _llr(self, j):
        return self.F[j] - self.T[j]
    def _argmax(self):
        return max(range(16), key=lambda j: (self._llr(j), -(self.F[j]+self.T[j])))
    def next_ct(self):
        self.cur = self._argmax()
        return self.mkq(self.b, self.p, self.cands[self.cur], self.known)
    def feed(self, r):
        if r: self.T[self.cur] += 1
        else: self.F[self.cur] += 1
        self.q += 1
        l = sorted((self._llr(j) for j in range(16)), reverse=True)
        if l[0] - l[1] >= G or self.q >= self.cap_fn():
            self.done = True
    def pick(self):
        return HEX[self._argmax()]

def recover_two(oracle, mkq2, mkq1, log=print):
    P1 = {}; P2 = {}
    remaining = [32]
    def cap_fn():
        return min(CAPMAX, max(MIN, BUD - oracle.n - MIN*(remaining[0]-1)))
    for b in range(15, -1, -1):
        br2 = ByteRecover(b, P2, mkq2, cap_fn)
        br1 = ByteRecover(b, P1, mkq1, cap_fn)
        while not (br2.done and br1.done):
            cts = []; order = []
            if not br2.done: cts.append(br2.next_ct()); order.append(br2)
            if not br1.done: cts.append(br1.next_ct()); order.append(br1)
            res = oracle.ask_multi(cts)
            for o, r in zip(order, res):
                was = o.done
                o.feed(r)
                if o.done and not was:
                    remaining[0] -= 1
        P2[b] = br2.pick(); P1[b] = br1.pick()
        log(f"byte {b:2d}: blk2={chr(P2[b])} (q={br2.q})  blk1={chr(P1[b])} (q={br1.q})  total={oracle.n}")
    return bytes(P1[j] for j in range(16)), bytes(P2[j] for j in range(16))

def attempt(ClientCls, log=print):
    c = ClientCls()
    try:
        ct = c.encrypt()
        iv, c1, c2 = ct[:16], ct[16:32], ct[32:48]
        oracle = Oracle(c)
        def mkq2(b, p, v, known):
            d = bytearray(16)
            for j in range(b+1, 16): d[j] = known[j] ^ p
            d[b] = v
            return iv + xor(c1, bytes(d)) + c2
        def mkq1(b, p, v, known):
            m = bytearray(16)
            for j in range(b+1, 16): m[j] = known[j] ^ p
            m[b] = v
            return xor(iv, bytes(m)) + c1
        P1, P2 = recover_two(oracle, mkq2, mkq1, log)
        # No separate verification: `check` is the ultimate verifier and a wrong
        # check merely ends the session, which we'd reconnect on anyway.
        msg = (P1 + P2).decode("ascii")
        log(f"message guess: {msg}  (queries used {oracle.n})")
        o = c.check(msg)
        log(f"check -> {o}")
        return o.get("flag"), oracle.n
    finally:
        c.close()

def make_local_client():
    import types
    utils = types.ModuleType("utils"); lis = types.ModuleType("utils.listener")
    def start_server(port=None): pass
    lis.start_server = start_server; utils.listener = lis
    sys.modules["utils"] = utils; sys.modules["utils.listener"] = lis
    src = open(os.path.join(HERE, "13423.py")).read()
    g = {"__name__": "srv"}
    exec(compile(src, "13423.py", "exec"), g)
    Challenge = g["Challenge"]
    class LocalClient:
        def __init__(self):
            self.ch = Challenge(); self.greeting = b"local"
        def encrypt(self):
            return bytes.fromhex(self.ch.challenge({"option": "encrypt"})["ct"])
        def unpad(self, ct):
            return self.ch.challenge({"option": "unpad", "ct": ct.hex()})
        def unpad_batch(self, cts, chunk=6):
            return [self.ch.challenge({"option": "unpad", "ct": x.hex()})["result"] for x in cts]
        def check(self, m):
            return self.ch.challenge({"option": "check", "message": m})
        def close(self): pass
    return LocalClient

if __name__ == "__main__":
    if os.environ.get("LOCAL"):
        LC = make_local_client()
        flag, n = attempt(LC)
        print("LOCAL flag:", flag, "queries:", n)
    else:
        from client import Client
        for i in range(1, 7):
            try:
                flag, n = attempt(Client, log=lambda *a: print(*a, flush=True))
            except Exception as e:
                print(f"attempt {i} failed: {e!r}", flush=True)
                flag = None
            if flag:
                print("FLAG:", flag)
                break
            time.sleep(2)
