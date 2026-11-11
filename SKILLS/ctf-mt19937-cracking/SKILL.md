---
name: ctf-mt19937-cracking
category: ctf
description: "Use for MT19937 / Python random.Random stream cracking."
version: 1.0.0
author: Hermes Agent
license: MIT
metadata:
  hermes:
    tags: [ctf, crypto, mt19937, prng, mersenne-twister]
    related_skills: [ctf-practice-runs, ctf-crypto-attacks]
---

# MT19937 (Python `random.Random`) state recovery

## When to Use
Challenges built on Python's `random` (Mersenne Twister): `bad_temper`, `bad_temper_2`, `jeff`,
`roulette`, `lcg2`-adjacent. 624 observed 32-bit words fully determine the state.

## Invariants (verified against CPython 3.12, 2026-10-12)
- Word = `temper(A[pos])`; twist when `pos >= 624`, then `pos = 0`.
- **temper (CPython)**: `x ^= x>>11; x ^= (x<<7) & 0x9d2c5680; x ^= (x<<15) & 0xefc60000; x ^= x>>18`.
  The masks `0x9d2c5680`/`0xefc60000` are TEMPER masks — NOT the twist masks
  (`0x80000000`/`0x7fffffff`). Reusing the twist masks in temper/untemper makes the
  round-trip "pass" (both directions wrong in matching ways) while every real comparison
  fails. Verify `temper(A[i]) == word_i` against a live CPython instance before trusting.
- **CPython's twist is the IN-PLACE variant**: for i in 0..623: `A[i] = A[(i+397)%624] ^ f(y)`
  with `y = (A[i]&0x80000000)|(A[(i+1)&623]&0x7fffffff)`, `f(y) = (y>>1)^(0x9908b0df if y&1)`,
  writing A[i] BEFORE later i's read it. It differs from the canonical out-of-place formula
  (397 of 624 words) and from the (i+227) variant.
- **The in-place twist loses low31(A[0]) going forward, but the NEXT-earlier twist leaks
  them back** (bad_temper SOLVED 2026-10-21, flag `crypto{8r0k3n_f0rw4rd5_4nd_84ck}`).
  Untwisting N->O once recovers O[1..623] + upper bit of O[0]; low31(O[0]) appears in no N
  equation. BUT the twist that produced N read the *new* word 0 in its last line:
  `N[623] = N[396] ^ f((O[623]&U)|(N[0]&L))`, so `low31(N[0]) = low31(inv_f(N[623]^N[396]))`.
  I.e. untwist one cycle further back and the hole closes: the bits twist k destroys, the
  equations of twist k itself (seen from the pre-image side) still contain. Never declare a
  31-bit wall from a single untwist — check the i=623 equation of the previous twist.
  (Earlier note here claimed A0[0..7] unrecoverable — that came from an out-of-place
  recovery formula `A0[k]=A1[227+k]^f(y)` misapplied to the in-place twist.)

## Untwist (in-place CPython, N = post-twist array fully known -> O)
```python
U,L,MA=0x80000000,0x7fffffff,0x9908b0df
def f(y): return (y>>1)^(MA if y&1 else 0)
def inv_f(z):
    b=(z>>31)&1
    return (((z^(MA*b))<<1)|b)&0xffffffff   # f is a bijection on 32-bit words
def untwist(N):
    O=[0]*624
    for i in range(227,624):                # N[i]=N[i-227]^f(y_i); i=623: N[623]=N[396]^f(y_623)
        y=inv_f(N[i]^N[i-227]) if i<623 else inv_f(N[623]^N[396])
        O[i]|=y&U
        if i<623: O[i+1]|=y&L
    for i in range(0,227):                  # N[i]=O[i+397]^f(y_i), O[397..623] now known
        y=inv_f(N[i]^O[i+397])
        O[i]|=y&U
        O[i+1]|=y&L
    return O   # O[1..623] exact, upper bit of O[0] exact, low31(O[0]) = 0 (see leak rule)
```
bad_temper recipe: seed(bytes) leaves pos=624, so first_seed = temper(A1[0..7]) and
get_seed leaks words 8+. Collect 155 blocks (words 8..1247 = A1[8..623] + full A2),
`A1=untwist(A2)`, `A1[0] |= inv_f(A1[623]^A1[396])&L`, first_seed = pack_le(temper(A1[0..7])),
next block = pack_le(temper(twist(A2)[0..7])). Validate the whole pipeline on local
CPython (10/10) before touching the live socket.

## untemper (exact inverses)
```python
def inv_rshift_xor(y,s):
    x=y;m=s
    while m<32: x^=y>>m; m*=2
    return x&0xffffffff
def inv_lshift_xor(y,s,mask):
    x=[(y>>i)&1 for i in range(32)]
    for i in range(s,32):
        if (mask>>i)&1: x[i]^=x[i-s]
    return sum(x[i]<<i for i in range(32))&0xffffffff
def untemper(y):
    x=inv_rshift_xor(y,18)
    x=inv_lshift_xor(x,15,0xefc60000)
    x=inv_lshift_xor(x,7,0x9d2c5680)
    return inv_rshift_xor(x,11)
```

## Seed recovery: CPython init_by_array is analytically invertible
(bad_temper_2 SOLVED 2026-10-23, flag `crypto{533d5_0f_d357ruc710n}` — server demanded the
original 32-byte seed, not just predictions). No z3 needed:
- `Random.seed(bytes)` first maps `X = int.from_bytes(b + sha512(b).digest(), 'big')`
  (Lib/random.py), then splits X into LE 32-bit words = init_by_array key. For 32-byte
  seeds: 24 words; words 23..16 (big-endian) = the secret, words 15..0 = sha512 tail
  (free checksum of the recovered secret).
- loop1 `mt[i]=(mt[i]^T1(mt[i-1]))+key[j]+j`, T1(x)=(x^(x>>30))*1664525; loop2 same with
  T2(x)=(x^(x>>30))*1566083941 and `- i`. Both loops mix only with the just-written
  neighbour -> triangular. From post-seed state F (untwist once; F[0]=0x80000000 const):
  `L1[i]=(F[i]+i)^T2(F[i-1])` for i=623..3; `L1[1]=(F[1]+1)^T2(F[623])`;
  `L1[2]=(F[2]+2)^T2(L1[1])`; then
  `key[(i-1)%kl] = L1[i] - (S0[i]^T1(L1[i-1])) - ((i-1)%kl)` for i=3..623 where
  S0=init_genrand(19650218) (known). Each key word is over-determined ~26x.
- CRITICAL quirk: loop2 does NOT reset `i` after loop1 — it runs i=2..623 then 1, so
  step 2 uses the OLD mt[1] and step 1 uses mt[0]=mt[623] set at the wrap. A forward
  model that resets i=1 mismatches getstate(); mirror the exact order in the inverse.
- Get the real C source when mirrors are blocked: raw.githubusercontent/jsDelivr/GitHub
  API can 404 or block plain HTTP clients while a real browser session fetches
  raw.githubusercontent.com fine — try the browser before giving up on the source.

## numpy legacy RandomState variant (import_numpy_as_mt, Zh3r0 CTF V2 — SOLVED 2026-10-26)
- `numpy.random.RandomState(32bit_seed)` = init_genrand (A[0]=seed) but it **twists
  BEFORE the first output** (pos starts 624): word_i = temper(T[i]) with canonical
  OUT-OF-PLACE twist `T[i]=A[(i+397)%624]^f((A[i]&U)|(A[i+1]&L))`. untemper(word0) is
  NOT the seed — verify the twist model against a live RandomState first.
- `RandomState.bytes(n)` = n/4 uint32 words, **little-endian per word** (numpy 1.23
  and 2.x legacy path identical). So a transmitted iv leaks 4 FULL post-twist words.
- Every post-twist word is a pure function of the 32-bit seed (init_genrand chain
  A[i]=1812433253*(A[i-1]^(A[i-1]>>30))+i reaches A[0..8] and A[397..400]). So skip
  state recovery: brute-force 2^32 seeds in C (OpenMP + 4-way ILP chains, ~100 s)
  checking the 4 untempered iv words against the twist equations — 128 bits of
  constraint, zero false positives; confirm by regenerating the iv.
- Pitfall that cost 2 cycles: challenge `pad()` ran ONCE before a 2-round AES loop —
  outer layer plaintext is `iv1||ct1` UNPADDED. Symptom: iv-regen assert passes but
  unpad(outer_pt) fails. Also: never paste hex from truncated terminal previews —
  write socket output to a file programmatically.

## Full-state setstate + one period (twist_and_shout, Zh3r0 CTF V2 — SOLVED 2026-10-27)
Server does `setstate((3,flag_state+(624,),None))` then prints 624 `getrandbits(32)`:
untemper all → N, untwist once → state bytes (BE-pack) with flag in the clear. The single
destroyed low31(A[0]) is irrelevant when the flag sits at a uniform random offset — P(touch
word0)≈(len+3)/2496, just reconnect for fresh padding. Validate on local CPython first
(20/20 here); 'twist' in the title ≠ twist variant (siblings import_numpy_as_mt/real_mersenne
are the real variants).

## partial-output recovery via GF(2) (probability-seetf2022 SOLVED 2026-10-27, flag SEE{1337_card_counting_24ca335ed1cabbcf})
Server prints every `random.random()` double: leaks temper(w_{2j}) top 27 bits + temper(w_{2j+1}) top 26 bits.
Parametrize each base word by its 5/6 unknown low bits (3432 unknowns), propagate 32 symbolic bit-rows
(big-ints, +constant column) through the LINEAR twist+temper, every observed twist-word top bit = one
equation; bitset Gaussian takes 0.1 s at 630 doubles. Key facts:
- Stream recurrence (verified vs live CPython): `w[j] = w[j-227] ^ f(w[j-624], w[j-623])`, NOT j-624-based.
- Untemper traps: `for _ in range(2): y ^= y>>18` is an INVOLUTION (= no-op); masked-shift inverses must
  read the accumulator, not a frozen copy. Run an untemper(temper(w))==w self-test at import, always.
- Exact rank floor: free bits of word i first appear in equations at j=i+624, so full rank needs
  T=624 doubles; kernel = 4 w0 columns (low31(A0) leak) and is provably prediction-invariant -> zero it.
- To replay doubles from recovered STATE words: apply temper() first (doubles use output words).
- Game layer: if rounds share one RNG stream and player choices consume draws, per-round optimal play
  (0.523 win/round) < 800/1337 threshold; a global forward DP over (round, stream position) exploiting
  phase control reaches ~800-850. Retry connections until a stream is favorable (~3/4 needed).

## Pitfalls
- CPython `getstate()` inner tuple: `[int, [624 ints + pos], gauss_next]` — state[1][624] is
  the position; the array is the logical A (not rotated) at snapshot time.
- `randbytes(n)` consumes `ceil(n/4)` words; 32-byte outputs = 8 words each. Map the byte
  stream to word indices BEFORE recovering anything.
- When a single untwist leaves a 31-bit hole, do NOT declare a wall: the previous twist's
  i=623 equation recovers it (see leak rule above). bad_temper was solved exactly this way.

## Canonical references (owner list 2026-11-02)
[R11] Matsumoto–Nishimura, "Mersenne Twister: A 623-Dimensionally Equidistributed Uniform Pseudo-Random
Number Generator", ACM TOMS 24(1):1-30, 1998 — the GF(2)-linear structure exploited by every attack in this
skill is the paper's own construction property. https://dl.acm.org/doi/10.1145/272991.272995
