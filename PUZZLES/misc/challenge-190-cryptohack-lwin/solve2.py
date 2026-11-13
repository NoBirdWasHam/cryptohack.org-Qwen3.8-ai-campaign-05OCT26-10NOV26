# L-Win solve v2.
# s[n+384] = XOR_{t in T} s[n+t] for all n>=0; window = s[768..2815] known.
# Step 1: for n in [768, 2431] all indices n+t, n+384 are in-window ->
#   linear system in tap-indicator v (384 unknowns): sum_t v_t*s[n+t] = s[n+384].
# Step 2: backward-extend with q(x)=p(x)/x^(384-tmax): s[m] = s[m+tmax] + sum_{t!=tmax} s[m+tmax-t].
# Step 3: flag = s[0..383].
import sys
from Crypto.Util.number import long_to_bytes

def solve(src):
    bits = [int(ch) for ch in open(src).read().strip()]
    assert len(bits) == 2048
    S = lambda i: bits[i - 768]  # s[i] for i in [768,2815]

    # Step 1: [flag — recorded in FLAGS/post-quantum/challenge-168-cryptohack-lwe-intro/flag.txt] over GF(2), rows as (mask, rhs)
    rows = []
    for n in range(768, 2432):
        mask = 0
        for t in range(384):
            if S(n + t):
                mask |= 1 << t
        rhs = S(n + 384)
        rows.append((mask, rhs))
    piv = {}  # col -> (mask, rhs)
    for mask, rhs in rows:
        stored = False
        for col in range(383, -1, -1):
            if not (mask >> col) & 1:
                continue
            if col in piv:
                m2, r2 = piv[col]
                mask ^= m2
                rhs ^= r2
            else:
                piv[col] = (mask, rhs)
                stored = True
                break
        if not stored and mask == 0 and rhs == 1:
            raise RuntimeError("inconsistent system")
    print("rank:", len(piv))
    # particular solution (free vars = 0)
    v = 0
    for col in range(384):
        if col in piv:
            m2, r2 = piv[col]
            val = r2
            for c2 in range(col):  # pivot row's other bits are < col
                if (m2 >> c2) & 1 and (v >> c2) & 1:
                    val ^= 1
            if val:
                v |= 1 << col
    taps = [t for t in range(384) if (v >> t) & 1]
    print("taps (particular sol):", taps)
    # check nullspace dimension: free columns
    free = [c for c in range(384) if c not in piv]
    print("free vars:", len(free))
    return bits, taps, piv, free

def backward(bits, taps):
    tmin = min(taps)
    ext = {i: bits[i - 768] for i in range(768, 2816)}
    for m in range(767, -1, -1):
        v = ext[m + 384 - tmin]
        for t in taps:
            if t != tmin:
                v ^= ext[m + t - tmin]
        ext[m] = v
    return ext

def verify(bits, taps, ext):
    # forward simulate from s[0..383] with taps, compare window
    st = [ext[i] for i in range(384)]
    out = []
    for _ in range(2816):
        out.append(st[0])
        c = 0
        for t in taps:
            c ^= st[t]
        st = st[1:] + [c]
    ok = out[768:2816] == bits
    return ok

if __name__ == "__main__":
    src = sys.argv[1] if len(sys.argv) > 1 else "output.txt"
    bits, taps, piv, free = solve(src)
    if len(taps) != 4:
        print("WARNING: not 4-sparse; need nullspace search over", len(free), "free vars")
    ext = backward(bits, taps)
    ok = verify(bits, taps, ext)
    print("forward-verify:", ok)
    val = int("".join(str(ext[i]) for i in range(384)), 2)
    fb = long_to_bytes(val)
    print("bytes:", fb)
    if fb.startswith(b"crypto{") and fb.endswith(b"}") and ok:
        print("FLAG:", fb.decode())
        open("flag_lwin.txt", "w").write(fb.decode())
