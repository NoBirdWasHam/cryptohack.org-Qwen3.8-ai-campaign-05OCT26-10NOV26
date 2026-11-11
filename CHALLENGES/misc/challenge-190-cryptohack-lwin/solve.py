# L-Win: LFSR with unknown taps. Output = s[768..2815] of a sequence with
# linear complexity L <= 384. BM recovers the minimal connection polynomial;
# run it backwards to get s[0..383] = flag bits.
from Crypto.Util.number import long_to_bytes

bits = [int(ch) for ch in open(__import__("sys").argv[1] if __import__("sys").argv[1:] else "output.txt").read().strip()]
assert len(bits) == 2048

def berlekamp_massey(s):
    n = len(s)
    C = [1] + [0]*n
    B = [1] + [0]*n
    L, m = 0, -1
    for N in range(n):
        d = s[N]
        for i in range(1, L+1):
            d ^= C[i] & s[N-i]
        if d:
            T = C[:]
            for i in range(len(B)):
                if B[i]:
                    C[N-m+i] ^= 1
            if 2*L <= N:
                L = N + 1 - L
                m = N
                B = T
    return C[:L+1], L

C, L = berlekamp_massey(bits)
print("linear complexity L =", L)

# Forward consistency check: regenerate window from first L bits
seq = bits[:L]
for i in range(len(bits) - L):
    nb = 0
    for j in range(1, L+1):
        nb ^= C[j] & seq[i + L - j]
    seq.append(nb)
assert seq == bits, "BM forward check failed"
print("forward check OK")

# Backwards: s[n-L] = s[n] + c1 s[n-1] + ... + c_{L-1} s[n-L+1]  (c_L = 1)
ext = bits[:]  # ext[k] = s[base + k]
base = 768
for n in range(768 + L - 1, -1, -1):
    # s[n] = s[n+L] + c1 s[n+L-1] + ... + c_{L-1} s[n+1]  (c_L = 1)
    v = ext[n + L - base]
    for j in range(1, L):
        v ^= C[j] & ext[n + L - j - base]
    ext = [v] + ext
    base -= 1
# now ext[0] = s[0]; ext[k] = s[k]
flag_bits = ext[:384]
val = int("".join(map(str, flag_bits)), 2)
fb = long_to_bytes(val)
print("flag bytes:", fb)
if fb.startswith(b"crypto{") and fb.endswith(b"}"):
    print("FLAG:", fb.decode())
    open("flag_lwin.txt", "w").write(fb.decode())
else:
    print("not a flag; check")
