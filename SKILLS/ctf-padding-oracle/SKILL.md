---
name: ctf-padding-oracle
category: ctf
description: "Use for CBC padding oracle attacks and forges in CTFs."
version: 1.0.0
author: Hermes Agent
license: MIT
metadata:
  hermes:
    tags: [ctf, crypto, padding-oracle, block-cipher, forge]
    related_skills: [ctf-crypto-attacks, ctf-practice-runs, cryptohack-socket-challenges]
---

# Padding oracle → decryption & forgery recipes

## When to Use
Any challenge where a server accepts/rejects ciphertexts based on PKCS7 validity, and the
flag either sits behind decryption (read the flag) or behind a *signature* the oracle lets you
forge (get_flag with a crafted (message, signature) pair).

## Always-on rules
- **One TCP connection per full attempt** (CryptoHack spins a fresh challenge per connect).
  ~10k queries on one connection is fine (measured ~25 min); on a drop, restart the whole
  attack. Never silently reconnect inside a query loop.
- **Read the server source first** — the exact `decrypt_flag`/`check_padding` code decides
  the byte-mapping (which block is prepended, what plaintext charset is expected, whether
  `pos` is 0 or 1-based).

## 1. Read the flag (byte-at-a-time)
For byte `p` of block `b` (15→0), target padding `v = 16-p`:
- `F[q] = D_b[q] ^ v` for `q>p`, `F[p] = g ^ v` for candidate `g`, `F[q] = 0` for `q<p`.
- The unique accepted `g` is `D_b[p]`; plaintext char = `D_b[p] ^ prev[p]` (prev = IV or C_{b-1}).
- **Candidate sets are SHIFTED by the previous block**: if plaintext must be hex/ASCII, search
  `{c ^ prev[p] for c in charset}`, NOT the raw charset. Searching the unshifted set makes the
  survivor count hit 0.
- If the message is a clean multiple of the block size there is NO final padding block.

## 2. Forge: Beaulieu–Desmedt (Rhetorical Oracle family — SOLVED 2026-10-12)
Target: `sign(M) = S(M) = E_K(M padded, IV=0…)` style — you can ask the oracle to encrypt
`M ‖ FLAG` and it returns the ciphertext; `get_flag(ct, pos)` decrypts ct at block `pos` and
tells you the plaintext char there (or a padding check). To forge `sign(M*)` for a chosen
`M*` containing `admin=True`:
- Recover `D(c[i])` for each flag block via the padding oracle (step 1, with `pos` pointed at
  block `i`'s position in the target ciphertext).
- **The off-by-one that bites everyone**: `c[i-1] = D(c[i]) ⊕ P[i]` — the forged previous
  block XORs the plaintext of the SAME block index `i`, not `i-1`. (With `pos` = the block
  whose char you read, `c[pos-1] = D(c[pos]) ⊕ P[pos]`.)
- Determine the exact `pos` semantics with a distinguishing probe: encrypt a known 2-block
  message, read `pos=0` vs `pos=1`, see which returns the expected char. Don't assume.
- Build the target: choose `M*` so the flag block lands where you can forge its predecessor
  (pad `M*` to an exact block count, e.g. 80-byte target → 5 blocks); `c*[i-1] = D(c[i]) ⊕ P*[i]`;
  first block `c*[0] = D(0…0) ⊕ P*[0]` (IV=0).
- Verify `good_pad` on the assembled ciphertext before submitting.

## 3. Noisy / biased oracles
- invalid→True w.p. 0.6, valid→always True: **eliminate on False**, re-query all survivors
  each round, the survivor is the byte. Never "first true wins".
- 60% FLIP (oracular_spectacular style: correct answer inverted most of the time): a single
  query is 0.4-useful — you MUST average (≥20 queries, majority vote) or the whole recovery
  collapses; budget the query cap accordingly (32-byte message ≈ 24k single-query equivalents
  may exceed a 12k cap → use bit-parallel probes or accept it's borderline).

## Pitfalls
- Padding oracle gives `D(C_b)`, not plaintext — unchain at the end (`P_b = D_b ⊕ prev_b`).
- A forge that "works" locally but fails server-side is almost always the `P[i]` vs `P[i-1]`
  off-by-one or a wrong `pos` base — re-probe, don't re-tune the math.
- Budget: 15 candidate bytes/byte × ~4 blocks × 2 passes ≈ 5–10k queries; check the server's
  cap and rate before starting.
