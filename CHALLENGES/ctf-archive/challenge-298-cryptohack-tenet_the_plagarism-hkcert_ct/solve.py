# tenet_the_plagarism-hkcert_ct: exact 16-byte key recovery via a 251 x 256 GF(2) solve.
#
# Algebra (self-contained; reconstructs the author's matrix solve referenced in the
# postmortem mystiz.hk/posts/2021/2021-11-18-hkcert-ctf-2, which is NOT opened here):
#   * Every layer key is b||0^15 with the same counter(128, 0) => all 16 layers index ONE
#     256-entry keystream table v(b) (64 bytes = 4 counter blocks for a 62-byte msg).
#   * CTR chaining => KS = XOR_i v(k_i); duplicates cancel => KS = XOR_{b in S} v(b) where
#     S = multiset of key bytes with ODD multiplicity (|S| <= 16, |S| even).
#   * Known plaintext "Congratulations! hkcert21{" + \w{35} + "}":
#       - 26 prefix bytes + final '}'  -> 27 bytes x 8 = 216 exact bits of D = m^KS
#       - every \w char is ASCII => BIT 7 OF EACH OF THE 35 INTERIOR BYTES IS ALSO KNOWN (0)
#         => +35 exact bits  => 251 EXACT bits total.
#   * In indicator form u in GF(2)^256 (u[b]=1 <=> b in S) the system  M u = D  is LINEAR
#     (M: 251 rows x 256 cols). rank 251 => solution coset of dim 5 => enumerate 32
#     candidates, keep weight <= 16 (even) => unique S in milliseconds. No MITM needed.
import os, re, sys, time
from Crypto.Cipher import AES
from Crypto.Util import Counter

CT = bytes.fromhex(
    "6ccb80c46c19243a37633d316a66871ca70ec8a44f48a80134f31d8d27f920c6"
    "bd5d810831833221d0f282130d2c222de38c2080ef995b2ad10dc5af8518")
PREFIX = b"Congratulations! hkcert21{"
N = 62
NW = 35
FLAG_RE = re.compile(r"hkcert21\{\w{35}\}")
WORD = "abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789_"

def keystream_table(nblk=4):
    """v(b) = keystream (16*nblk bytes) of AES-128-CTR, key b||0^15, counter 0..nblk-1."""
    tab = {}
    for b in range(256):
        ecb = AES.new(key=bytes([b]) + b"\0" * 15, mode=AES.MODE_ECB)
        tab[b] = ecb.encrypt(b"".join(i.to_bytes(16, "big") for i in range(nblk)))
    return tab

def tenet_encrypt(msg, key):
    """Reference implementation of the cipher (mirrors challenge.py encrypt())."""
    out = msg
    for i in range(16):
        a = AES.new(key=key[i:i+1] + b"\0" * 15, mode=AES.MODE_CTR,
                    counter=Counter.new(128, initial_value=0))
        out = a.encrypt(out)
    return out

def xor_bytes(bs):
    r = 0
    for x in bs:
        r ^= int.from_bytes(x, "big")
    return r.to_bytes(len(bs[0]), "big")

def known_bit_positions():
    """(byte j, bit t, known plaintext bit) for all exactly-known keystream bits."""
    pos = []
    for j in range(26):                     # prefix bytes: all 8 bits known
        for t in range(8):
            pos.append((j, t, (PREFIX[j] >> t) & 1))
    for j in range(26, 26 + NW):            # interior \w bytes: bit7 == 0 (ASCII)
        pos.append((j, 7, 0))
    for t in range(8):                      # final '}' byte: all 8 bits known
        pos.append((61, t, (0x7d >> t) & 1))
    return pos                              # len == 26*8 + 35 + 8 == 251

def solve_gf2(rows, rhs, ncols=256):
    """rows: list of int bitmasks; rhs: list of bits. Returns (particular, kernel_basis, rank).
    Full RREF so each pivot column appears in exactly one row."""
    red, red_rhs = list(rows), list(rhs)
    pivots = {}                              # col -> row index
    keep_r, keep_b = [], []
    for r, b in zip(red, red_rhs):
        for c, ri in pivots.items():
            if (r >> c) & 1:
                r ^= keep_r[ri]; b ^= keep_b[ri]
        if r:
            c = (r & -r).bit_length() - 1    # lowest set bit = pivot col
            pivots[c] = len(keep_r)
            keep_r.append(r); keep_b.append(b)
    # upward reduction: clear each pivot column from all other rows (RREF).
    # Ascending pivot order: row-i has no bits below its pivot, so already-cleaned
    # lower pivot columns can never be re-introduced.
    for c in sorted(pivots):
        ri = pivots[c]
        for j in range(len(keep_r)):
            if j != ri and (keep_r[j] >> c) & 1:
                keep_r[j] ^= keep_r[ri]; keep_b[j] ^= keep_b[ri]
    red, red_rhs = keep_r, keep_b
    free_cols = [c for c in range(ncols) if c not in pivots]
    x_p = 0                                   # particular: free vars = 0
    for c, ri in pivots.items():
        if red_rhs[ri]:
            x_p |= 1 << c
    kern = []
    for f in free_cols:
        v = 1 << f
        for c, ri in pivots.items():
            if (red[ri] >> f) & 1:
                v |= 1 << c
        kern.append(v)
    return x_p, kern, len(pivots)

def run_recovery(c, known_cbits, tab):
    """known_cbits: list of (j, t, m_bit). Build M u = (m^c) bits, solve, enumerate coset."""
    rows = []
    for (j, t, _) in known_cbits:
        row = 0
        for b in range(256):
            if (tab[b][j] >> t) & 1:
                row |= 1 << b
        rows.append(row)
    rhs = [mb ^ ((c[j] >> t) & 1) for (j, t, mb) in known_cbits]
    x_p, kern, rank = solve_gf2(rows, rhs)
    dim = len(kern)
    cands = []
    for mask in range(1 << dim):
        x = x_p
        m_ = mask
        i = 0
        while m_:
            if m_ & 1:
                x ^= kern[i]
            m_ >>= 1; i += 1
        w = bin(x).count("1")
        if w <= 16 and w % 2 == 0:
            cands.append(x)
    return cands, rank, dim

def keystream_from_S(x, tab):
    r = int.from_bytes(b"\0" * 64, "big")
    for b in range(256):
        if (x >> b) & 1:
            r ^= int.from_bytes(tab[b], "big")
    return r.to_bytes(64, "big")

def pad_to_16(x):
    """Any 16-byte key whose parity subset is S(x): distinct bytes + duplicate pairs."""
    supp = [b for b in range(256) if (x >> b) & 1]
    key = supp[:]
    fill = [b for b in range(256) if not ((x >> b) & 1)]
    while len(key) < 16:
        p = fill.pop()
        key += [p, p]                         # duplicate pair cancels in parity
    return bytes(key)

def synth_trial(tab, seed=None):
    rng = random_local(seed)
    key = bytes(rng.randrange(256) for _ in range(16))
    interior = "".join(rng.choice(WORD) for _ in range(NW))
    flag = "hkcert21{" + interior + "}"
    m = (PREFIX.decode() + interior + "}").encode()   # PREFIX already contains 'hkcert21{'
    c = tenet_encrypt(m, key)
    true_S = 0
    for b in set(key):
        if key.count(b) % 2 == 1:
            true_S |= 1 << b
    t0 = time.time()
    cands, rank, dim = run_recovery(c, known_bit_positions(), tab)
    t1 = time.time()
    hit = [x for x in cands if x == true_S]
    dec_ok, key_ok = False, False
    if hit:
        m2 = bytes(p ^ q for p, q in zip(c, keystream_from_S(hit[0], tab)))[:N]
        dec_ok = (m2 == m)
        k2 = pad_to_16(hit[0])
        key_ok = (tenet_encrypt(m, k2) == c)
    return dict(rank=rank, dim=dim, ncand=len(cands), true_in=bool(hit),
                dec_ok=dec_ok, key_ok=key_ok, secs=round(t1 - t0, 2))

def random_local(seed=None):
    import random
    r = random.Random(seed)
    return r

if __name__ == "__main__":
    tab = keystream_table()
    print("keystream table built (256 entries x 64 B)")
    if "--synth" in sys.argv or len(sys.argv) == 1:
        print("== synthetic twin trials (same 62 B model, random 16-byte keys) ==")
        allok = True
        for seed in range(5):
            r = synth_trial(tab, seed=seed)
            allok &= (r["rank"] == 251 and r["true_in"] and r["dec_ok"] and r["key_ok"])
            print(f"  trial {seed}: rank={r['rank']} cosetdim={r['dim']} "
                  f"weight<=16-cands={r['ncand']} trueS_recovered={r['true_in']} "
                  f"decrypt_ok={r['dec_ok']} key_regen_ok={r['key_ok']} ({r['secs']}s)")
        print("SYNTHETIC TWIN: ALL OK" if allok else "SYNTHETIC TWIN: FAIL")
    if "--real" in sys.argv or len(sys.argv) == 1:
        print("== real ciphertext ==")
        cands, rank, dim = run_recovery(CT, known_bit_positions(), tab)
        print(f"rank={rank} coset dim={dim} -> {1<<dim} solutions; "
              f"weight<=16 even candidates: {len(cands)}")
        flags = []
        for x in cands:
            m2 = bytes(p ^ q for p, q in zip(CT, keystream_from_S(x, tab)[:62]))
            txt = m2.decode("latin1")
            cand_flag = txt[len(PREFIX) - 9:]     # flag = txt[17:] (starts at 'hkcert21{')
            ok = bool(FLAG_RE.fullmatch(cand_flag)) and txt.startswith(PREFIX.decode())
            print(f"  cand weight={bin(x).count('1')} plaintext={txt!r} flag_format_ok={ok}")
            if ok:
                k2 = pad_to_16(x)                 # end-to-end: regenerated 16-byte key
                assert tenet_encrypt(m2, k2) == CT, "re-encryption mismatch"
                print(f"  end-to-end check: key={k2.hex()} re-encrypts to the exact ciphertext")
                flags.append(cand_flag)
        if len(flags) == 1:
            with open(os.path.join(os.path.dirname(os.path.abspath(__file__)), "flag.txt"), "w") as f:
                f.write(flags[0])
            print("FLAG:", flags[0])
        elif len(flags) == 0:
            print("no candidate matched the flag format")
        else:
            print("AMBIGUOUS:", flags)
