---
record: agent-aar
puzzle: challenge-13395-cryptohack-oofbleck-firebird_internal_ct
category: CTF Archive
url: https://cryptohack.org/challenges/oofbleck-firebird_internal_ct/
status: solved
date: 2026-11-02
flag_ref: "FLAGS/ctf-archive/challenge-62-cryptohack-oofbleck-firebird_internal_ct/flag.txt"
flag_sha256: 276fd9efe411b824f6fd1cb8cb7b1615fc3d19957fbcbbb51d323396700948c3
skills: []
human_twin: AAR.md
---

# AGENT — Oofbleck (Firebird Internal CTF) — AAR
Machine-optimized twin of the human AAR in this directory (mechanically regenerated from it; carries no extra facts).
Epistemic tags: OBSERVED = artifact/evidence present in this dir · NOT OBSERVED = not recorded anywhere in the corpus.

## procedure — extracted from AAR section "The vulnerability (first-principles read of chall.py)" [OBSERVED text; evidence tag applies to its source, not each claim]
`encrypt()` calls `AES.new(iv, AES.MODE_OFB, key)` — **key/IV arguments swapped**.
Consequences:
- The AES key is `iv = os.urandom(16)`, and `iv` is **prepended to the ciphertext** in output.txt → attacker knows the AES key.
- The secret `key` (unknown) is merely the OFB initial feedback state X0.
- Keystream chain over 5 blocks (flag = 68 B, PKCS7 → 80 B): X1=E_K(X0), X_{i+1}=E_K(X_i). OFB itself is fine; this is a pure API-misuse bug ("unfortunately it is so hard to get cryptography done right").

## reusable-rules
When a stream-like mode's block key is recoverable from output, hunt for *known keystream* (headers + PKCS7 + fixed delimiters); a chain of E_K inversions converts a 56-bit search into a 3-char brute force. Mind off-by-one flag layout before sizing a brute force.

## anti-patterns / limits
- First solve.py wrongly modelled flag bytes 64–67 as \w⁴ (forgot byte 67 is '}') → full \w⁴ scan (14.8M candidates, 2m49s) returned "not found". Fixed tail model → \w³ + '}' solved instantly.
- Initially wasted calls on archive.cryptohack.org: TLS `SEC_E_WRONG_PRINCIPAL` and 404 for /static/challenges/…; live cryptohack.org serves the files.
- Considered (and rejected) ~2⁴² direct brute force of the X1 tail and X3-MITM before spotting the padding-block anchor.

## artifacts [OBSERVED]
- code: solve.py
- data/logs: flag_oofbleck-firebird_internal_ct.txt, output.txt
- flag value: never in this file; sha256 against `FLAGS/INDEX.jsonl`

## references
Sources: challenge-provided materials only; self-derived per run logs.
