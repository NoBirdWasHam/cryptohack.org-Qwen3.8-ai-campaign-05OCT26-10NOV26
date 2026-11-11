# AAR — Find the Lattice (challenge-182-cryptohack-find)

100 pt, post-quantum. Recover the private key `(f, g)` of a toy "LWE-ish" scheme and
decrypt `e` to the flag.

## Protocol (from provided source)

- q = 512-bit prime; f ∈ [2, √(q/2)), g ∈ [√(q/4), √(q/2)), gcd(f,g)=1
- public key h ≡ g·f⁻¹ (mod q)  ⇒  **h·f = g + s'·q** (s' = ⌊h·f/q⌋ < 2^255)
- ciphertext e ≡ r·h + m (mod q), r < √(q/2), m = flag (27 bytes = 216 bits)
- decrypt: a = (f·e) mod q;  m = a·f⁻¹ (mod g)

Only (q, h, e) are known. All secrets (f, g, r) are ≈ 2^254.8.

## Attack (the "hidden 2D lattice")

The key relation h·f = g + s'·q means the vector **(g, f) lies in the 2D lattice**

    L = ⟨ (h, 1), (q, 0) ⟂  ⊂ Z²,   since (g, f) = f·(h, 1) − s'·(q, 0).

det(L) = q ≈ 2^511.6, so a *random* 2D lattice of this determinant has shortest
vector ≈ 2^255.8 — and (g, f) sits right at that scale (‖(g,f)‖ ≈ 2^255). 2D
Gaussian reduction is provably optimal, so it finds (g, f) exactly.

Solve script: `solve.py` (pure Python, 2D Gauss, no fpylll needed).

Result:

    g = 43997957885147078115851147456370880089696256470389782348293341937915504254589
    f = 47251817614431369468151088301948722761694622606220578981561236563325808178756

Verified against all structural constraints (each checked in code):
- (h·f) mod q == g ✓
- 2 ≤ f < isqrt(q//2) ✓
- isqrt(q//4) ≤ g < isqrt(q//2) ✓
- gcd(f, g) == 1 ✓

## Decryption — one wrong formula, then the protocol's

Wrong (first attempt): `m = (f*e) % g` → 255 bits of non-ASCII garbage.
That is NOT the scheme's decrypt; the modulus q in `a = (f*e) % q` matters.

Correct (exactly as the source's `decrypt`):

    a = (f * e) % q
    m = (a * pow(f, -1, g)) % g

→ m = 231 bits = 29 bytes → **`crypto{Gauss_lattice_attack!}`**

## Result

**SOLVED 2026-10-14** — flag live-verified via user API (`submit_flag.py find ...`):
`ok: true`, score 7005 → **7105** (+100), solved 152 → **153**.

## What went wrong along the way (lessons)

1. **Blind lattice guessing costs real time.** I first tested ⟨(q,h),(e,1)⟩,
   ⟨(q,e),(h,1)⟩, ⟨(q,0),(e,h)⟩, ⟨(h,e),(q,1)⟩, ⟨(q,h),(q,e)⟩ — all had
   random-scale (~2^511–2^512) shortest vectors, no structure. The right move was to
   derive the lattice *from a protocol relation*: each "x ≡ y (mod q) with y short"
   relation lifts to a lattice vector (y, x-coefficient). The relation g = h·f mod q
   gives (g, f) ∈ ⟨(h,1),(q,0)⟩ directly.
2. **2D Gaussian must be implemented with dot-product nearest-plane reduction**
   (m = round(⟨v2,v1⟩/‖v1‖²), v2 ← v2 − m·v1, swap on norm). A coordinate-wise
   heuristic version silently failed to reduce (returned an input vector).
3. **Never invent the decryption formula.** The source defines `decrypt`; use it
   verbatim. `(f*e) % g` vs `((f*e) % q) * f⁻¹ % g` differ by the q-reduction and
   one gives 255 bits of noise.
4. **Sanity-check a candidate secret against every bound** (congruence, range, gcd)
   before decrypting — here all four checks passed, which is what justified the
   (initially suspicious) SVP as the true key.

Files: `solve.py`, `find_output.txt`, `find_source.py` (copies of `_pq/`), `flag.txt`.

## Sources
Sources: challenge-provided materials only; self-derived per run logs.
