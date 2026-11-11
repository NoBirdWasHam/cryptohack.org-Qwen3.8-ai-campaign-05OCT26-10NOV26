"""
mixed_up solver (socket.cryptohack.org 13402).

Server: mixed_and = FLAG & data ; mixed_xor = (FLAG^data)^urandom ;
        very_mixed[j] = mixed_xor[mixed_and[j] % L] ; reply sha256(very_mixed).

Attack:
 - Probe data=00*64 -> mixed_and=0 -> very_mixed = c^L -> brute c,m finds L.
 - Per bit b, per group of positions: data[j]=2^b on group, 0 elsewhere.
   very_mixed = x0 everywhere, x1 at positions where FLAG[j] has bit b.
   Brute (x0,x1,subset) = 2^(16+k) hashes; unique match reveals the bits.
"""
import socket, json, hashlib, sys, time
from concurrent.futures import ProcessPoolExecutor

HOST, PORT = "socket.cryptohack.org", 13402

class Srv:
    def __init__(self):
        self.sock = None
    def connect(self):
        self.sock = socket.create_connection((HOST, PORT), timeout=30)
        self.f = self.sock.makefile("rwb")
        self.f.readline()  # before_input banner
    def mix(self, data_hex, retries=4):
        for a in range(retries):
            try:
                if self.sock is None: self.connect()
                self.f.write((json.dumps({"option": "mix", "data": data_hex}) + "\n").encode())
                self.f.flush()
                line = self.f.readline()
                if not line: raise ConnectionError("closed")
                r = json.loads(line)
                if "mixed" in r: return r["mixed"]
                raise RuntimeError(f"server error: {r}")
            except Exception as e:
                print(f"  retry {a+1} ({e})", flush=True)
                try: self.sock.close()
                except Exception: pass
                self.sock = None
                time.sleep(2 * (a + 1))
        raise RuntimeError("mix failed")

def find_len(srv):
    table = {}
    for m in range(1, 97):
        for c in range(256):
            table[hashlib.sha256(bytes([c]) * m).hexdigest()] = (c, m)
    dig = srv.mix("00" * 96)
    if dig not in table:
        raise RuntimeError("length probe failed")
    c, L = table[dig]
    print(f"FLAG length L = {L} (probe byte c={c})", flush=True)
    return L

def _brute(args):
    L, group, digest, x0_lo, x0_hi = args
    out = []
    k = len(group)
    n = 1 << k
    for x0 in range(x0_lo, x0_hi):
        base = bytearray([x0]) * L
        for x1 in range(256):
            if x1 == x0:
                if hashlib.sha256(bytes(base)).hexdigest() == digest:
                    out.append((x0, x1, 0))
                continue
            s = bytearray(base)
            prev = 0
            for idx in range(n):
                g = idx ^ (idx >> 1)
                if idx:
                    d = g ^ prev
                    t = d.bit_length() - 1
                    s[group[t]] = x1 if (g >> t) & 1 else x0
                prev = g
                if hashlib.sha256(bytes(s)).hexdigest() == digest:
                    out.append((x0, x1, g))
    return out

_POOL = None
def get_pool():
    global _POOL
    if _POOL is None:
        _POOL = ProcessPoolExecutor(max_workers=8)
    return _POOL

def brute(srv_digest, L, group):
    ex = get_pool()
    step = 32
    chunks = [(L, group, srv_digest, lo, min(lo + step, 256)) for lo in range(0, 256, step)]
    res = [r for ch in ex.map(_brute, chunks, chunksize=1) for r in ch]
    return res

def get_mask(srv, L, group, const_set, tries=5):
    """Return the bit-mask for `group` (data=2^b on group set by caller via data hex)."""
    n_const = 0
    for attempt in range(tries):
        dig = srv.mix(group["hex"])
        if dig in const_set:
            # constant string: either x0==x1 (no info) or all bits 0 (mask=0).
            n_const += 1
            continue
        res = brute(dig, L, group["pos"])
        masks = {m for (_, _, m) in res}
        if len(masks) == 1:
            return masks.pop()
        print(f"  ambiguous masks {masks} -> retry", flush=True)
    if n_const == tries:
        return 0  # every attempt constant => mask really is 0 (x0==x1 5x is ~2^-40)
    raise RuntimeError("get_mask failed")

def main():
    srv = Srv()
    L = find_len(srv)
    const_set = {hashlib.sha256(bytes([c]) * L).hexdigest() for c in range(256)}
    flag = [0] * L
    unknown = list(range(7, L - 1))
    K = 8
    groups = [unknown[i:i+K] for i in range(0, len(unknown), K)]
    for b in range(7):  # printable ASCII: bits 0..6
        for gi, group in enumerate(groups):
            data = bytearray(L)
            for j in group: data[j] = 1 << b
            t0 = time.time()
            mask = get_mask(srv, L, {"pos": group, "hex": data.hex()}, const_set)
            for t, j in enumerate(group):
                flag[j] |= (1 if (mask >> t) & 1 else 0) << b
            print(f"  bit {b} group {gi} mask={mask} in {time.time()-t0:.1f}s", flush=True)
    # verify known prefix and suffix
    gp = list(range(0, 7)) + [L - 1]
    for b in range(7):
        data = bytearray(L)
        for j in gp: data[j] = 1 << b
        mask = get_mask(srv, L, {"pos": gp, "hex": data.hex()}, const_set)
        for t, j in enumerate(gp):
            known = ord("crypto{"[j]) if j < 7 else ord("}")
            assert ((known >> b) & 1) == ((mask >> t) & 1), f"prefix mismatch pos {j} bit {b}"
    print("prefix/suffix verification passed", flush=True)
    # fill prefix/suffix
    for j in range(7): flag[j] = ord("crypto{"[j])
    flag[L-1] = ord("}")
    out = bytes(flag)
    print("FLAG:", out.decode(errors="replace"), flush=True)
    with open("flag_mixed_up.txt", "w") as fh:
        fh.write(out.decode())
    if _POOL is not None:
        _POOL.shutdown()

if __name__ == "__main__":
    main()
