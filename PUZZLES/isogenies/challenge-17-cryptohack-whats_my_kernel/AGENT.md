---
record: agent-aar
puzzle: challenge-214-cryptohack-whats_my_kernel
category: isogenies
url: https://cryptohack.org/challenges/whats_my_kernel/
status: solved
date: 2026-10-16
flag_ref: "FLAGS/isogenies/challenge-17-cryptohack-whats_my_kernel/flag.txt"
flag_sha256: 423dad515b319cbe64db26fcb9fa2b02b49eef6330b927e653bc312a8106d1c0
skills: [ctf-isogenies]
human_twin: AAR.md
---

# AGENT — whats_my_kernel (What's My Kernel, 70 pts)
Machine-optimized twin of the human AAR in this directory (mechanically regenerated from it; carries no extra facts).
Epistemic tags: OBSERVED = artifact/evidence present in this dir · NOT OBSERVED = not recorded anywhere in the corpus.

## procedure — extracted from AAR section "Attack (self-solve, no external writeups)" [OBSERVED text; evidence tag applies to its source, not each claim]
The SIDH public key leaks the kernel when the two image points are collinear on the 2-primary subgroup.

1. **Data** (from server static files, verified byte-identical to local copies via `raw equal: True`):
   - E_0: y² = x³ + 1 over F_{p²}, p = 2^216·3^137 − 1 = 2443942366…73567 (434 bits), F_{p²} = F_p[i]
   - P_a, Q_a: order 2^216 (c_a = 3^137 times full generators); P_b = P_a, Q_b = Q_a
   - E_A, P_B = φ(P_a), Q_B = φ(Q_a), φ = isogeny with kernel R = P_a + n·Q_a
2. **Key observation**: Q_B ∈ ⟨P_B⟩ — the two public images lie on one cyclic subgroup.
3. **ECDLP**: solve Q_B = m·P_B in ⟨P_B⟩, ord(P_B) = 2^216 (verified: smallest s with 2^s·P_B = O is s = 216, i.e. 2^215·P_B ≠ O). Method: ℓ-adic (2-division) bit extraction, LSB-first, 216 bits, pure Python over F_{p²} (affine, one field inversion per doubling). Result:
   `m = 0xeac325184e820daac7ca1ea989e8002c894189e01e93b0e199c3a9`
   Verified by direct double-and-add: `m*P_B == Q_B : True` (two independent F_{p²} implementations agreed).
4. **Kernel relation**: φ(P_a + n·Q_a) = P_B + n·Q_B = (1 + n·m)·P_B = O. Since ord(P_B) = 2^216:
   `1 + n·m ≡ 0 (mod 2^216)` → `n ≡ −m⁻¹ (mod 2^216)`.
   (Consistency check via first-isomorphism-theorem: |im(φ|_{E[2^216]})| = 2^432/2^216 = 2^216 = |⟨P_B⟩| forces ord(P_B) = 2^216 — matches the computed s = 216.)
5. **Result**:
   `n = −m⁻¹ mod 2^216 = 0x77686f6f70735f746869735f7761735f6a7573745f615f646c6f67`
   `= bytes "whoops_this_was_just_a_dlog"` (27 bytes — exactly the 27-char FLAG slot: `n = bytes_to_long(FLAG[7:-1])`).
6. **Flag**: `[flag — recorded in FLAGS/isogenies/challenge-17-cryptohack-whats_my_kernel/flag.txt]` — accepted (+70).

The author planted the answer: the dlog recovers a 215-bit value that IS the 27-byte flag, reading "whoops_this_was_just_a_dlog" — the puzzle's own joke ("this was just a dlog").

## reusable-rules
- none recorded [NOT OBSERVED] — derive from procedure above

## anti-patterns / limits
- none recorded [NOT OBSERVED]

## artifacts [OBSERVED]
- code: solve.py, source_real.sage, velu2_test.py, verify_n.py
- data/logs: output.txt, output_real.txt, solve.log
- flag value: never in this file; sha256 against `FLAGS/INDEX.jsonl`

## references
Sources: challenge-provided materials only; self-derived per run logs.
