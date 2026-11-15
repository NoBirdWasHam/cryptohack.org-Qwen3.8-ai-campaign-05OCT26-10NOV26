"""
MDFlag solver.

Oracle: h(d) = md5(d XOR cycle(FLAG)), |d| >= L=46.

Key trick (length extension + periodic keystream):
  For any n, let pad_n = MD5 padding of an n-byte message.
  Query d (len n) -> h = md5(s), s = d ^ F^inf.
  The string m' = s || pad_n has length n+|pad_n| (a multiple of 64 if we
  pick n mod 64 in {54,55}), so md5(m') = C(h, pad') where pad' is the
  all-known padding block of m' (0x80 0^55 LE64(8*(n+|pad_n|))).
  The server computes md5(d' ^ F^inf) for d' = d || (pad_n ^ F^inf[n:]).
  Since F^inf[n:] is just the flag starting at position n mod 46, the
  server's answer EQUALS md5(m') iff our guess of those few flag bytes is
  right.  Choose n so the pad region covers exactly ONE unknown flag byte
  (plus known bytes): n = 46k + a, n = 64m + r, r = 64 - p, p+a even.
  256 queries per byte, descending a = 44..8.  Known: "crypto{" (0..6),
  '}' (45).
"""
import struct, sys, json, socket

# ---------------- MD5 compression function (from arbitrary state) ----------
_S = [7,12,17,22, 7,12,17,22, 7,12,17,22, 7,12,17,22,
      5, 9,14,20, 5, 9,14,20, 5, 9,14,20, 5, 9,14,20,
      4,11,16,23, 4,11,16,23, 4,11,16,23, 4,11,16,23,
      6,10,15,21, 6,10,15,21, 6,10,15,21, 6,10,15,21]
_K = [int(abs(__import__('math').sin(i+1)) * 2**32) & 0xFFFFFFFF for i in range(64)]

def _rotl(x, c):
    return ((x << c) | (x >> (32 - c))) & 0xFFFFFFFF

def md5_compress(state16, block):
    """state16: 16 bytes (little-endian 4 words), block: 64 bytes -> 16 bytes."""
    a, b, c, d = struct.unpack('<4I', state16)
    M = struct.unpack('<16I', block)
    aa, bb, cc, dd = a, b, c, d
    for i in range(64):
        if i < 16:   f, k = (b & c) | (~b & d), i
        elif i < 32: f, k = (d & b) | (~d & c), (5*i+1) % 16
        elif i < 48: f, k = b ^ c ^ d,          (3*i+5) % 16
        else:        f, k = c ^ (b | ~d),       (7*i) % 16
        f = (f + a + M[k] + _K[i]) & 0xFFFFFFFF
        a, d, c, b = d, c, b, (b + _rotl(f, _S[i])) & 0xFFFFFFFF
    return struct.pack('<4I', (aa+a)&0xFFFFFFFF, (bb+b)&0xFFFFFFFF,
                                   (cc+c)&0xFFFFFFFF, (dd+d)&0xFFFFFFFF)

def md5_pad(msg_len):
    """MD5 padding bytes for a message of length msg_len (not including msg)."""
    l8 = msg_len * 8
    pad = b'\x80'
    pad += b'\x00' * ((56 - (msg_len + 1) % 64) % 64)
    pad += struct.pack('<Q', l8)
    return pad

def extend_aligned(hbytes, n, p):
    """md5(s || pad_n) given hbytes=md5(s), |s|=n, when (n+p) % 64 == 0
    (p = len(pad_n)): s||pad_n is block aligned, its last block is exactly
    s's final padded block, so the state after it is hbytes; one more
    compression with pad' = md5_pad(n+p) gives the answer."""
    assert (n + p) % 64 == 0
    return md5_compress(hbytes, md5_pad(n + p))

# ---------------- attack core (transport-agnostic) -------------------------
L = 46
KNOWN_PREFIX = b'crypto{'

def find_step(F, a):
    """Find (p, n): pad length p, query length n, so that the pad window
    F[a:a+p) (mod 46) contains at most two unknown flag bytes, n = 46k+a
    (window starts at flag pos a), n = (64-p) mod 64 (pad length p), and
    the JSON message stays under the server's 1024-byte cap (hex doubles
    data, so keep n + p <= 490)."""
    for p in range(9, 65):
        if (p - a) % 2:
            continue
        win = [(a + i) % L for i in range(p)]
        unk = [q for q in win if F[q] is None]
        if not (1 <= len(unk) <= 2):
            continue
        r = (64 - p) % 64
        for k in range(1, 33):
            n = 46 * k + a
            if n % 64 == r and n >= L and n + p <= 490:
                return p, n, unk
    raise RuntimeError(f"no valid step for a={a}")

def recover(query):
    """query: bytes -> 16 raw bytes of md5(d ^ F^inf).  Returns flag bytes."""
    F = [None] * L
    for i, ch in enumerate(KNOWN_PREFIX):
        F[i] = ch
    F[45] = ord('}')
    for a in range(44, 7, -1):
        p, n, unk = find_step(F, a)
        pad = md5_pad(n)
        assert len(pad) == p and n % 64 == (64 - p) % 64 and n % 46 == a
        d = bytes(n)
        h = query(d)
        assert (n + p) % 64 == 0
        pred = extend_aligned(h, n, p)          # md5(s || pad)
        win = [(a + i) % L for i in range(p)]
        found = None
        import itertools as _it
        for gs in _it.product(range(256), repeat=len(unk)):
            Fg = list(F)
            for pos, g in zip(unk, gs):
                Fg[pos] = g
            dprime = d + bytes(pad[i] ^ Fg[win[i]] for i in range(p))
            if query(dprime) == pred:
                found = gs
                break
        if found is None:
            raise RuntimeError(f"no match at pos {unk}")
        for pos, g in zip(unk, found):
            F[pos] = g
            print(f"[+] pos {pos:2d}: {chr(g)!r}  (known {sum(x is not None for x in F)}/{L})", flush=True)
    flag = bytes(F)
    assert all(x is not None for x in F)
    return flag

# ---------------- local self-test ------------------------------------------
def local_test():
    import hashlib, itertools
    # sanity: our compression matches hashlib on a single block
    import os as _os
    IV = bytes.fromhex('0123456789abcdeffedcba9876543210')
    blk = _os.urandom(64)
    st = md5_compress(IV, blk)
    # state after 1 block == md5 of (blk + padding) minus final pad compression?
    # easier: full message = blk (64B) -> md5 = C(C(IV,blk), pad(64))
    assert md5_compress(st, md5_pad(64)) == hashlib.md5(blk).digest()
    # sanity: extend_aligned matches hashlib
    s = _os.urandom(823)
    p = len(md5_pad(len(s)))
    assert (len(s) + p) % 64 == 0
    assert extend_aligned(hashlib.md5(s).digest(), len(s), p) == hashlib.md5(s + md5_pad(len(s))).digest()
    print("compression + extension verified")
    FAKE = b'[flag value withheld — real-flag strings live only under FLAGS/]'
    assert len(FAKE) == L
    def bxor(x, y): return bytes(u ^ v for u, v in zip(x, itertools.cycle(y)))
    calls = [0]
    def query(d):
        calls[0] += 1
        assert len(d) >= L
        return hashlib.md5(bxor(d, FAKE)).digest()
    got = recover(query)
    print("fake :", FAKE)
    print("got  :", got)
    print("queries:", calls[0])
    assert got == FAKE
    print("LOCAL TEST PASSED")

# ---------------- live transport -------------------------------------------
def live():
    PORT = 13407
    s = socket.create_connection(("socket.cryptohack.org", PORT), timeout=30)
    s.settimeout(30)
    buf = b""
    def recv_obj():
        nonlocal buf
        while True:
            bpos = buf.find(b"{")
            if bpos >= 0:
                try:
                    obj, i = json.JSONDecoder().raw_decode(buf[bpos:].decode())
                    buf = buf[bpos+i:]
                    return obj
                except json.JSONDecodeError:
                    pass
            d = s.recv(65536)
            if not d:
                raise RuntimeError("connection closed")
            buf += d
    try:
        s.recv(65536)  # plain-text greeting "Enter data\n"
    except Exception:
        pass
    calls = [0]
    def query(d):
        s.sendall((json.dumps({"option": "message", "data": d.hex()}) + "\n").encode())
        obj = recv_obj()
        calls[0] += 1
        if "hash" not in obj:
            raise RuntimeError(f"server error: {obj}")
        return bytes.fromhex(obj["hash"])
    flag = recover(query)
    print("FLAG:", flag.decode())
    print("queries:", calls[0])
    s.close()

if __name__ == '__main__':
    if '--local' in sys.argv:
        local_test()
    else:
        live()
