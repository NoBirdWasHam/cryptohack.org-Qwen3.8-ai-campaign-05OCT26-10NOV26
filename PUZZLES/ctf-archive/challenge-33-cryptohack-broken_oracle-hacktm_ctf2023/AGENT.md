---
record: agent-aar
puzzle: challenge-33-cryptohack-broken_oracle-hacktm_ctf2023
category: ctf-archive
url: https://cryptohack.org/challenges/broken_oracle-hacktm_ctf2023/
status: solved
date: 2026-10-26
flag_ref: "FLAGS/ctf-archive/challenge-33-cryptohack-broken_oracle-hacktm_ctf2023/flag.txt"
flag_sha256: 388a85cd431a88cfc7c111edce4f30597ee6fcfb02a83d547c96e4a4125b8ee4
skills: []
human_twin: AAR.md
---

# AGENT — broken_oracle (HackTM CTF 2023), CryptoHack archive
Machine-optimized twin of the human AAR in this directory (mechanically regenerated from it; carries no extra facts).
Epistemic tags: OBSERVED = artifact/evidence present in this dir · NOT OBSERVED = not recorded anywhere in the corpus.

## procedure — extracted from AAR section "Attack (all against one live session)" [OBSERVED text; evidence tag applies to its source, not each claim]
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

## reusable-rules
- none recorded [NOT OBSERVED] — derive from procedure above

## anti-patterns / limits
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

## artifacts [OBSERVED]
- code: live1.py, probe.py, probe2.gp, probe3.py, solve_live.py, t3.py, t4.py, t5.py
- data/logs: flag_broken_oracle-hacktm_ctf2023.txt, live2_out.txt
- flag value: never in this file; sha256 against `FLAGS/INDEX.jsonl`

## references
- see AAR.md `Sources`
