---
record: agent-aar
puzzle: challenge-54-cryptohack-pekobot-ais3_pre-exam2022
category: ctf-archive
url: https://cryptohack.org/challenges/pekobot-ais3_pre-exam2022/
status: solved
date: 2026-11-02
flag_ref: "FLAGS/ctf-archive/challenge-54-cryptohack-pekobot-ais3_pre-exam2022/flag.txt"
flag_sha256: 6f8bc37d1c5df448de339a552459ded5b17a874d9055713cf14808be420d7b9b
skills: []
human_twin: AAR.md
---

# AGENT — pekobot (AIS3 Pre-Exam) / pekobot-ais3_pre-exam2022
Machine-optimized twin of the human AAR in this directory (mechanically regenerated from it; carries no extra facts).
Epistemic tags: OBSERVED = artifact/evidence present in this dir · NOT OBSERVED = not recorded anywhere in the corpus.

## procedure — extracted from AAR section "Vulnerability (self-derived from provided server.py)" [OBSERVED text; evidence tag applies to its source, not each claim]
Option 1 computes `S = Point(E, x, y) * d` with **no curve-membership check**, and quotes are a fixed public list (known plaintext). The key move:
1. Option 2 returns `C1 = rG`, `C2 = flag_pad XOR point_to_bytes(rP)`.
2. Feed `C1`'s coordinates into option 1: server returns `quote XOR point_to_bytes(C1*d)`, and `C1*d = r(dG) = rP` — exactly the flag keystream point. No ECDLP needed.
3. XOR the ct against each of the 8 known quotes (padding `ljust(64, b"\0")` makes the keystream exact); only the right quote yields `C2 XOR key` starting `AIS3{` and printable through `}`.

Twist/small-subgroup attack on d was considered and ruled out: #twist = 3·5·13·179·(241-bit prime) → only ~15 bits of d reachable via F_p oracle; irrelevant once the C1→rP oracle is noticed.

## reusable-rules
- none recorded [NOT OBSERVED] — derive from procedure above

## anti-patterns / limits
- Twist/small-subgroup recovery of d was considered and *ruled out on paper* before the oracle was noticed: `#twist = 3*5*13*179*(241-bit prime)` gives only ~15 reachable bits of d via an F_p oracle — irrelevant once C1 -> rP composition was seen.
- First live run had a parsing desync (prompt echo glued to the ciphertext line); fixed by parsing only the post-`y` response.
- gmpy2/kernel-python mismatch forced math onto terminal python3. No further failures.

## artifacts [OBSERVED]
- code: elliptic_curve.py, harness.py, solve.py
- data/logs: none
- flag value: never in this file; sha256 against `FLAGS/INDEX.jsonl`

## references
- Self-derived per logs from the challenge-provided `server.py` / `elliptic_curve.py` only; no CryptoHack /solutions//solves or third-party writeups consulted; no external math reference was needed (ECDH algebra is in the provided file).
- Upgrade-time comprehension check (batch #9, 2026-11-02): re-derived the `C1*d = rP` collapse and the XOR triple from the AAR record and `solve.py`/`harness.py` offline — no live re-run, claims/flag untouched.
