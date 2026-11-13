# Differential key-pair solver for diffecient (SekaiCTF 2022).
# Goal: K0 != K1 (both >=32 printable bytes, regex-valid) with
#   mmh3.hash(K1, i) % (2**32-5) == mmh3.hash(K0, f(i)) % (2**32-5)  for all seeds i,
# where f(i) = 46 - i (involution). Then: add K0 (option 2), admin K1 (option 3) -> FLAG.
#
# Construction: K0 = B_1..B_n || B_x || T0,  K1 = B_1..B_n || B_y || T1  (same prefix,
# same #blocks, same tail length). Prefix induces Phi(i)=L_i on 0..46 (random-ish).
# Need 5*(R_i ^ wx) + c3  ==  5*(R_j ^ wy) + c3  (XOR eq), R=rotl13(Phi), j = rev(i).
# Solve forward: set V_0 = {0..46} (bits of seed); layer1 XOR-const kills high bits
# (k with low13 bits 0 => Phi(i) = w ^ (i<<13) exact); layer2 XOR-const kills bits
# {1,2,3,5,6} (determined by c3+5w); layer3 XOR-const with bit0/4/7 pattern of
# (c3+5x) determines the remaining bit choice e_i. Verify final equality directly.
import os, sys, time, re

M = 0xFFFFFFFF
C3 = 0xE6546B64

def rotl(v, r): return ((v << r) | (v >> (32 - r))) & M
def mix32(x):
    x = (x * 0xCC9E2D51) & M
    x = rotl(x, 15)
    return (x * 0x1B873593) & M

def dig(data, seed):
    h = seed & M
    n = len(data)
    for off in range(0, n - n % 4, 4):
        k = int.from_bytes(data[off:off+4], 'little')
        k = mix32(k)
        h ^= k; h = rotl(h, 13); h = (h * 5 + C3) & M
    r = n % 4
    if r:
        k = int.from_bytes(data[n-r:], 'little')
        h ^= mix32(k)
    h ^= n
    h ^= h >> 16; h = (h * 0x85EBCA6B) & M
    h ^= h >> 13; h = (h * 0xC2B2AE35) & M
    h ^= h >> 16
    return h if h < 2**31 else h - 2**31

N = 47
REV = [46 - i for i in range(N)]

def layer_fwd(vals, k):
    out = []
    for h in vals:
        x = h ^ k
        x = (x * 0xCC9E2D51) & M
        x = rotl(x, 15)
        x = (x * 0x1B873593) & M
        out.append(x)
    return out

def layerC_fwd(vals, w):
    # C(h) = rotl13(h ^ w)*5 + c3
    return [(rotl(h ^ w, 13) * 5 + C3) & M for h in vals]

def solve_layer3(V):
    # V: 47 values < 2^8 (bits 0..7), with e_i := V[i] & 1 satisfying
    # V[rev(i)] = V[i] ^ 1 ^ 16 ^ 128  (bit4/bit7 already fixed by layer2 XOR-const)
    # return list of 13-bit low patterns p_i (bit0 = e_i, bits 1..3 free 0) s.t.
    # (C3 + 5*V[i]) ^ p_i == (C3 + 5*V[j]) ^ p_j  (j = rev(i))
    target = None
    p = [0]*N
    for i in range(N):
        a = (C3 + 5*V[i]) & M
        b = (C3 + 5*V[REV[i]]) & M
        if target is None:
            ei = V[i] & 1
            p[i] = ei | ((C3 + 5*V[i]) & 0xE)   # bits1..3 := c3+5V's bits (cancel on both sides)
            target = a ^ p[i]
        else:
            e = V[i] & 1
            pi = e | ((C3 + 5*V[i]) & 0xE)
            if (a ^ pi) != target:
                return None, None
            p[i] = pi
    return p, target

def attempt(seed):
    rng = os.urandom
    # layer 1: k1 with low13 zero -> Phi(i) = w ^ (i<<13), w = (k1>>13)<<13 ^ ... actually
    # rotl13(i ^ k1) with k1 = W (W % 2^13 == 0): i^W = W + i (i<64 bits0..5 vs W bits13+)
    # -> rotl13(W + i) = ((W+i)<<13 | (W+i)>>19) = (W<<13) + (i<<13) + ((W>>19)) ... W>>19
    # careful: (W+i)>>19 = W>>19 for i<2^13 ✓; low13 bits of rotl = bits19+ of (W+i) = W>>19.
    # rotl13(W+i) = ((W+i) << 13 mod 2^32) | (W >> 19) = (W<<13 + i<<13) | (W>>19)
    # (W<<13 bits >=13; W>>19 bits 0..12) -> Phi1(i) = ((W<<13) | (W>>19)) + (i << 13) + 0? XOR?
    # (W<<13)|(W>>19) has bits>=13 from W<<13; i<<13 adds into bits 13..18 -> carry if overlap
    # (W>>5 & 31) + i >= 32. So NOT clean. Instead just do generic layer-1 with random k1
    # and require the *pair* structure: Phi1(i) = 5... wait our structure works at layer C:
    # after block layer1: S1(i) = rotl13(i^k1)*5 + c3: rotl13(i^k1) = rotl13(i)^rotl13(k1)
    # = (i<<13) ^ w  (w = rotl13(k1)): choose w = 0 (k1 = 0!): rotl13(i) = i<<13 for i<2^19 ✓
    # S1(i) = 40960*i + c3 EXACT (Z).
    k1 = rng(4)
    # k1 = 0 forced for the clean path:
    S1 = [40960*i + C3 for i in range(N)]  # == C block layer w/ k1=0
    # layer2 block const k2 kills bit0 and bits2-4 of (S1 ^ k2): S1 low5 = c3&31 = 4.
    # want (S1^k2)&1 = 0: bit0(S1)=0 -> k2 bit0 = 0. bits1..4: S1 bits1-4 = c3 bits1-4 = 2
    # -> k2 bits1..4 = 2. bits 2..4 zero; bit22 := (5*(4^2)>>2)=5 -> bit2=1; bit23=bit3=0.
    # so S2(i) = 5*((c3 ^ 40960*i ^ k2) >> 2) + c3 + 40 with (x&31) = 8^? => x bits0..4 = k2^S1:
    # choose k2 = (c3 & ~0x1F) ^ (c3 ^ 8) ^ (1<<0)?? simpler: choose x_low5 = 8 (bit3=1, rest 0)
    # -> e = (8>>2)&1 = 2&1 = 0 -> bit22=0, bit23=0, and S2 = 5*((x - 8)>>... ugh: x = S1^k2:
    # we need x & 31 == 8 and x bits>=5 == S1 bits>=5 ^ k2's: choose k2 = (8 ^ (c3 & 31)) ^ ((c3 & ~31) ^ (c3 & ~31))...
    # x = S1 ^ k2: set k2 = ((c3 & 31) ^ 8) | (rand high bits ^ S1's high ^ desired high).
    # The layer-2 high-bit kill: k2 bits >=5 cancel S1 bits >=5 exactly: S2 = 5*(8 + (S1>>5 ^ k2h))
    # choose k2h = S1>>5 (const!) => S2(i) = 5*(8 + (i*1280 + (c3>>5) ^ (c3>>5))... NO:
    # S1 = c3 + 40960 i: S1>>5 = (c3>>5) + 1280*i VARIES with i (Z vs XOR).
    # So layer2: x = S1 ^ k2 with k2 = const: x(i) = (c3 ^ k2) + 40960*i if no carry between
    # (c3^k2) low 13 and 40960 i... bits: S1 bits0..12 = c3&8191 const; k2 bits0..12 const
    # -> x bits0..12 = const L12! bits13.. = (S1>>13) ^ (k2>>13) with S1>>13 = (c3>>13)+5i:
    # (A + 5i) ^ B: choose B = 0 (k2 bits>=13 = 0): = A + 5i (A=c3>>13=460: A+5i <= 775: bits:
    # A=111001100: +5i varies bits >=0 with carries) -> x = (A+5i)*8192 + L12 EXACT.
    # x & 31 = L12 & 31 = c3&31 ^ k2&31 = 4 ^ (k2&31): want == 8 -> k2&31 = 12. bit22 :=
    # bit2 of ((x>>2))·5... 5*(x>>2): x>>2 = (A+5i)*2048 + (L12>>2): bit22 of 5*(x>>2) =
    # 5*2048*(A+5i) = 10240*(A+5i): bit22 = bit10 of 5(A+5i) +carry... VARIES with i ✗✗
    # unless we kill: bit22 of (5*(x>>2) + c3): bits>=13 of S2 = 5*(x>>2) bits>=13 ^ ... NO
    # S2 = 5*(x>>2) + c3: bits >= 13: (5*(x>>2))>>13 + (c3>>13): 5*(x>>2) = 10240*(A+5i) + 5(L12>>2):
    # >>13: (10240(A+5i) + f)>>13 = (5(A+5i)) + (f>>13) + carry: VARIES with i ✗.
    # => layer-2 "kill" only works if the 5i term sits in bits we're killing: layer1 must put
    # the i-dependence into bits 1..4 region! i.e. layer1 k1 with rotl13(k1) = w, 5*((i<<13)^w):
    # (i<<13)^w: bits0..12 = w's; bits 13..18: i ^ (w>>13): 5*that: 5(i ^ w') ∈ 0..315 bits 0..8
    # at offset 13: bits 13..21 vary. Layer2 kills bits 0..4 & 22 & 23 only... doesn't reach 13..21 ✗.
    # REVISED kill layer: kill bits 0..8 (5*(x>>2)'s dependence from x bits 2..8) requires
    # layer1 to emit dependence at bits 2..8: rotl13 puts seed dependence at bits 13-18 & 0-2
    # (i>>19 = 0 -> just 13..18): shift to 2..8 requires rotl by 13*? fixed. BUT the *2^? trick:
    # dependence at bits 13..18 -> multiply C (odd) → spreads. XOR-const can kill bits 13..18
    # region instead: choose layer2-const k with x^k bits13..18 = desired pattern & the OTHER
    # killed set: 5*(y) bits depend on y bits0..27 -> kill y's bits0..8?? conflict again.
    # CONCLUSION: kill-layer must kill EXACTLY the bits the previous layer made variable:
    # var bits after layer1: {13..21} (from 5(i^w')<<13). kill layer: k bits13..21 = target
    # pattern bits13..21: x^k = const ^ (carry junk from below?) x(i) = (A+5(i^w'))*8192 + C:
    # bits0..12 = C const: no carry up ✓ bits13+ = A + 5(i^w'): XOR k's >=13: (A + 5(i^w')) ^ B:
    # to be const need (A+5(i^w')) ^ B const: A+5(i^w') ∈ A+5*(0..63): 64 values 111..: XOR
    # constant iff all in one coset: A+5v vs A+5v': need them equal ✗✗✗ (they differ!).
    # => XOR-const CANNOT kill a bit that varies via Z-addition. The whole "kill" idea requires
    # the variation to be XOR-linear (bitwise free) — Z-linear variation (5i) is XOR-nonlinear.
    # The ONLY XOR-linear variation available after 5*(x>>2)+c3 comes from KILLED bits of x —
    # but that's where constancy was needed. => pure XOR-const chain IMPOSSIBLE. Must use
    # block-pair structure: layer 8 = pair layer (wx,wy free 32+32 bits): layers 1-7 = SAME
    # blocks both sides: U_i = W_j needed. Layers 1..7: 224 bits, target: 46 pair-equalities
    # (32 bits each) + U_23 freedom => 1472 constraints ✗✗✗ counting again... UNLESS
    # prefix is only 1-2 blocks: layers 1-2 = common: need C_{k2}(C_{k1}(i)) = L(rev(i)) with
    # k1,k2 shared?? 64 bits vs target L: 1472 ✗.
    # => accept: L must be engineered: L(i) = rev-antisymmetric AFTER some common map:
    # the pair layer needs U_i ^ wx = U_j ^ wy: i.e. U_i ^ U_j = d CONST for all pairs!
    # U = C_{k7}..C_{k1}(seed): 7 shared blocks (224 bits) to make 23 pairwise XOR-differences
    # equal the same d: U_i ^ U_{rev(i)} = d: fix d, fix pairs: constraints: 22 * 32 = 704 vs
    # 224 ✗ — but we can also choose the seed-side: U = F(i) with 7 layers... 704 constraints
    # ✗✗. Give up on full-structure; go DYNAMIC with 1-bit/iter:
    return None

# ---- fallback: dynamic programming over layer-3-style single-bit choices at EVERY block
# layer using FREE per-i bits (not achievable with XOR-const) => use 4-byte blocks to make
# per-i independent k-values: KEY: a block's mix32 output k is a bijection of the 4 block
# bytes => k is FREE. "Blocks that process only seed i" = impossible (all seeds see all
# blocks). BUT: h ^= k makes k XOR a CONST into h — variation is always via Z-mult. Hence
# the differential must be carried through *5 as Z-difference: 5u - 5u' = 5(u-u') and
# XOR-equality A==B (not xor): final equality z_i == z_j needs 5*(R_i^wx)+c3 == 5*(R_j^wy)+c3
# => R_i ^ wx == R_j ^ wy => R_i ^ R_j = d (pair layer, XOR-diff must survive *5 XOR-equal:
# 5x == 5y XOR-equal only if x==y). So U_i == U_j EXACTLY (pair layer). U = 7 common layers.
# Search strategy: random 7-block prefix, check if any pair has U_i == U_j: P ~ 46*2^-32 per
# prefix — hopeless. USE: layers 1..6 common with engineered structure so that
# U'_i = C6..C1(seed) has the pair-symmetry U'_i == U'_rev(i): build backward! U' target set
# with symmetry built in: A6 = {a_i} with a_i = a_rev(i) (24 values + U_23) and backward-solve
# layers: at each layer we have const k (32 bits) AND the set must map 47 seeds in:
# backward chain: A_r known 47-point symmetric set; need C_k(A_{r-1}-from-seeds)... forward
# from seeds: S_r = C_{k_r}(S_{r-1}): need S_6 = A6: choose A7... doable as: S0 = {0..46}
# backward target S6 = A6: at each step S_{r} = C_{k}(S_{r-1}): S_r fully determined by S_{r-1},k
# — forward deterministic; we need to hit a symmetric set at step 6: choose A6 freely?! NO —
# A6 = S_6 determined. => the pair-differential requires solving 8 k's such that
# C8..C1(i) pairs match: counting 1472 vs 256 ✗✗ => SEED SET IS TOO BIG.
# FINAL structural idea: exploit that we don't need ALL pairs matched: t misses cost rho^t:
# 0 misses needed...
print("STATIC approach failed structurally; see analysis in AAR.")
