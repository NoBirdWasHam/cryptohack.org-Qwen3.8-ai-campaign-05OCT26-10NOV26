# AAR — broken_oracle (HackTM CTF 2023), CryptoHack archive

**Solved: yes.** Flag: `HackTM{h4v3_y0u_r34lly_f0und_4ll_7h3_bu65...?}`
Submit verified: `ok:true`, challenge solves counter incremented 247→248 (score_delta 0 — archive challenge, expected).

## The system
Server implements the Kurosawa–Itoh–Takeuchi "Rabin with reciprocal" scheme (ref: gasarch
rabinwithrecip.pdf). Privkey p,q ≡ 3 mod 4, 1024-bit; c has Jacobi −1 mod both. Enc(m) =
(r = m + c·m⁻¹ mod n, s = (m|n), t = [c/m < m]). Decryption solves x² − rx + c mod p and
mod q (via x^((p−1)/2) in the quotient ring), CRTs roots, filters by (m|n)==s, picks
max/min by t. **The oracle**: server returns Enc(Dec(r,s,t)) for any input triple.
Public key (n, c) is never sent — only the flag ciphertext.

## The bug
`solve_quad` is only correct when Δ = r²−4c is a quadratic residue mod the prime. When Δ
is a QNR the ring is GF(p²) and the returned "roots" a1, a2 = garbage (with a1+a2 ≡ r,
a1a2 = c+e, e unknown). Encrypting a garbage-root m then breaks the identity
Enc(Dec(r)) = r on that prime only.

## Attack (all against one live session)
1. **Factor n.** For a random r with Δ QR mod exactly one prime ("mixed" query), the
   returned r′ satisfies r′ ≡ r mod the *good* prime, differs mod the garbage prime.
   So d = r′−r is a multiple of exactly one prime; pairwise gcd(d_i, d_j) over ~12 mixed
   queries yields p and q (1024-bit clusters). ~15 queries.
2. **Recover c mod each prime (the real step).** Query the *same* r twice, with t=0 and
   t=1. The two decrypted candidates m₀,m₁ are distinct, and mod the garbage prime their
   components are {u, v} = {a1, a2}, so the responses are r′₀ = u + c/u, r′₁ = v + c/v
   (in some order) with u+v ≡ r and uv = c+e. Let σ = r′₀+r′₁, π = r′₀·r′₁ mod (garbage
   prime). Then
   - σ = r + cr/(c+e)
   - π = (c+e) + c(r² − c)/(c+e) − c … eliminating e gives a **linear** equation:
     c · (σ−2r)² = (π − r(σ−r)) · r(σ−r), i.e.
     **c = (π − r·d)·r·d·(σ−2r)⁻² mod prime, d = σ−r.**
   Clean side has σ = 2r (denominator 0 → skip); run the formula against both known
   primes; the garbage side yields c mod that prime. Consistency across queries confirms
   (verified exactly against true c locally). ~10 queries for both sides.
3. **Decrypt**: c = CRT(c_p, c_q); n = p·q; own solve_quad on the banner's r_f (Δ = (m−c/m)²
   is a QR mod both), CRT roots, filter (m|n)==s, t picks min (t=0) → flag bytes + urandom
   tail; regex-extract HackTM{...}.

Reference used: the scheme paper itself (linked in server.py) — allowed academic source.

## Key numbers
p, q 1024-bit each (n ≈ 2^2047); ~15 queries for factoring, ~10 for c; total < 40 oracle
calls. Local 512-bit end-to-end test (`t5.py`): c recovered correctly on first hits,
decrypt MATCH: True.

## Files
- `solve_live.py` — full solver (Conn class, c_from_pair, decrypt_full; `python3 solve_live.py live`)
- `t5.py` — local end-to-end verification; `t4.py` — single-query prime-leak verification
- `live1.py` — banner + clustering probe; `live2_out.txt` — decrypted bytes
- `flag_broken_oracle-hacktm_ctf2023.txt` — exact flag string

## Limitations / dead ends (evidence)
- The prior solver's lead ("gcd(r′−r, n) leaks the prime directly") fails because n is
  **unknown** (server sends no public key) — gcd needs a modulus; and for double-garbage
  queries (Δ QNR at both primes) the diffs are pseudorandom, which is why their pairwise
  gcds were ~1023-bit junk, not p/q. Fix: gcd *between* two mixed diffs (their t3 clustering, which worked).
- t3.py had a SyntaxError and was never actually run (its "no leak" conclusion was from t1/t2).
- Algebraic structure probe of the garbage value e = a1a2−c (`probe3.py`): e is a
  Lucas-sequence value res = x^((p−1)/2) with res² = r/x − 1 — no closed form in (r, c);
  brute-forcing per-prime c from single queries is ruled out (2^1024). The linearization
  trick in step 2 is what makes extraction possible.
- Error channel is uniformly "Something wrong..." — no per-failure discrimination; mixed
  queries essentially never error (jacobi filter always yields exactly 2 candidates unless
  a garbage value is 0 mod p).
