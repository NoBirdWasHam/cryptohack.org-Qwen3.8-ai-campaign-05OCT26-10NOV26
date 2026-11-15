---
record: agent-aar
puzzle: challenge-133-cryptohack-rhetorical_oracle_2
category: aes
url: https://cryptohack.org/challenges/rhetorical_oracle_2/
status: solved
date: 2026-10-19
flag_ref: "FLAGS/aes/challenge-26-cryptohack-rhetorical_oracle_2/flag.txt"
flag_sha256: eb7b5524dfc08ff0968e9cba34781c6f60446594a60ca09e129fc5396c831a20
skills: []
human_twin: AAR.md
---

# AGENT — 133-cryptohack-rhetorical_oracle_2: Rhetorical Oracle 2 (CryptoHack)
Machine-optimized twin of the human AAR in this directory (mechanically regenerated from it; carries no extra facts).
Epistemic tags: OBSERVED = artifact/evidence present in this dir · NOT OBSERVED = not recorded anywhere in the corpus.

## procedure — extracted from AAR section "How it was solved" [OBSERVED text; evidence tag applies to its source, not each claim]
Server (from provided `13437.py`): `P = AES-CBC-decrypt(K, iv=FIXED, ct)`; if unpadding OK
(`good_pad`), it does `token = json.loads(P.decode("unicode_escape"), strict=False)` and
returns the flag when `token["user_id"]` is in `ADMINS`. Each connection has a fresh K,
a fixed per-connection `T1` (first ciphertext block, known once), and a query budget.

**Why v1 failed (subagent's attempt, `live_solve_log.txt`):** a 6-block ct
`[T1, c1..c5]` controls plaintext blocks P[0..4] but NOT P[1] = D(c1)⊕T1, which is
uncontrolled garbage sitting inside the first JSON string value → JSON malformed /
user_id never becomes the admin. good_pad True, no flag.

**v2 attack (`solve3.py`, 7 blocks):**
1. `ct = [T1, c1, c2, c3, c4, c5, c6]`.
2. P[0] = `{"user_id": "h1h2h3` (forced by T1 — the server's fixed first plaintext block).
3. P[1] = G = D(c1)⊕T1 — random 16 bytes; must contain no `"` (0x22) and no `\` (0x5c)
   so `unicode_escape` is the identity on it.
4. P[2..6] = T = `","user_id":"` + ADMIN + `"}` + 0x01 (80 bytes, fully controlled by
   c2..c6 via standard CBC chaining: c5 = D(c6)⊕P6, c4 = D(c5)⊕P5, ..., c1 = D(c2)⊕P2).
5. Resulting plaintext: `{"user_id": "h1h2h3<G>","user_id":"ADMIN"}` + valid padding.
   Duplicate JSON key — `json.loads` keeps the LAST value → user_id == ADMIN → flag.
6. Building each attempt needs D(c_i) for i=1..5 and G = D(c1)⊕T1 (the 6th recovery),
   each a byte-at-a-time padding-oracle recovery (~1200–2100 queries each, ~160–215 s).
7. G-clean probability (254/256)^16 ≈ 88% per attempt → expected ~1.1 attempts;
   attempt 1 succeeded: 12348 queries total, forged ct length 112, good_pad True, FLAG.

## reusable-rules
- **CBC gives you every plaintext block except the first one that follows a
  server-chosen block.** When the first block T1 is fixed per connection, P[1] =
  D(c1)⊕T1 is the one block you cannot directly control — either recover it (the 6th
  oracle round) or design the plaintext to tolerate it being garbage.
- **Duplicate JSON keys: last wins** (Python `json.loads`), so a corrupted/unknown
  prefix string can be neutralized by repeating the key with the clean value.
  `strict=False` + `unicode_escape` tolerates control characters in the unknown block —
  only `"` and `\` break the encoding, hence the 88% clean-G retry.
- **Budget math before the attack:** 6 D-recoveries × ~2k queries ≈ 12k < query cap;
  the ~88% clean-G probability means one attempt almost always suffices.

## anti-patterns / limits
- Worked from the statement + provided `13437.py` only. One connection per attempt;
  whole attack on ONE connection (fresh K per TCP connection).
- Did not consult writeups/solutions. v1 was a subagent attempt that failed on the P[1]
  control issue; v2 is the corrected design (documented in `solve3.py` header).

## artifacts [OBSERVED]
- code: 13437.py, solve.py, solve3.py
- data/logs: flag_rhetorical_oracle_2.txt, live_solve3_log.txt, live_solve_log.txt
- flag value: never in this file; sha256 against `FLAGS/INDEX.jsonl`

## references
- **Platform:** CryptoHack (https://cryptohack.org/)
- **Category page (statement read here):** https://cryptohack.org/challenges/aes/
- **Challenge:** "Rhetorical Oracle 2" (150 pts, slug `rhetorical_oracle_2`)
- **Service:** socket.cryptohack.org:13437 (JSON line protocol)
- **NOT consulted:** `/challenges/rhetorical_oracle_2/solutions/` page, search-engine writeups (no-cheat rule)
