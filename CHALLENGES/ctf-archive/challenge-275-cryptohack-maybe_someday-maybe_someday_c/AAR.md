# AAR — maybe_someday-maybe_someday_c (Maybe Someday CTF, ctf-archive)

**Solved: yes.** Flag obtained live from the service, accepted under this exact slug
(ok:true; user solved-count read back 272→273; archive = 0 pts, expected).

## What the challenge actually was
The card statement ("find a collision for my hash algorithm, 256-bit, discrete log,
no public parameters") is **wrong/mismatched text** — same mismatch exists on the
googlectf2022 sibling card. The provided `chall.py`
(chall_1da0bbcca674d9f5fdb078a93239dc14.py) is the real spec: the genuine
GoogleCTF 2022 "maybe someday" Paillier challenge, byte-identical (md5
`1da0bbcca674d9f5fdb078a93239dc14`) to the sibling's file.

Per round (16 rounds, one session): server prints `c0 = Enc(secret)` where
`secret = sha512(os.urandom(2)).hexdigest()` (16 bits entropy). Client sends 20
chosen ciphertexts; `fast_decrypt` answers 😀 iff PKCS#1 v1.5 unpadding
(`0x00 0x02 <≥8 nonzero> 0x00 m`) succeeds. A wrong final guess kills the session.

## Attack (derived in-campaign, in sibling folder 13391; reused here)
Paillier multiplicative malleability: `c0 * g^K * r^n mod n^2` decrypts to the same
padded message + K. Choosing 20 offsets K and reading the zero-byte/valid-padding
pattern of the shifted 2048-bit plaintext leaks enough about `S = int(padded(secret))`
to pin S down (precomputed query design `design3.json`, batched 20-query decoder with
monotone-noise handling: spurious 😀 only flips 0→1). All 16 secrets recovered, then
flag printed. Full math details + limitations live in
`../challenge-13391-cryptohack-maybe_someday-googlectf2022/AAR.md`.

## This run
- Designated port **56434 is dead**: 8+ connection attempts over ~7 minutes
  (archive.cryptohack.org, cryptohack.org, www.cryptohack.org) all
  `ConnectionRefusedError(10061)`; while port 14846 was alive seconds later —
  so not a client/network issue. Evidence: `solve_live.log` header + site.md.
- Since the card's own file is byte-identical to the backend running on 14846, the
  solver was run fresh against 14846 (`solve.py`, MAXTRY=12; session succeeded within
  the run). Flag was **handed over by the live service in this session** — see
  `solve_live.log` ("round 0..15 ok", `FLAG: ...`), not copied from any answer file.
- Flag is the same string as the googlectf2022 sibling's, which confirms CryptoHack
  treats these two cards as the same challenge instance (same file hash, shared flag).
- Submitted under slug `maybe_someday-maybe_someday_c` → accepted.

## Flag provenance
Comes solely from the live listener (`archive.cryptohack.org 14846`) during this
session's 16-round solve. No third-party writeups, no ctf_archive description.yml,
no answer files consulted.

## Limitations / honest notes
- Could not exercise the card's *listed* port 56434 (dead listener); solved against
  the identical-code instance on 14846 instead. Accepted-flag read-back proves the
  platform considers them the same flag, but if the platform ever spawns a separate
  56434 container with a *different* FLAG env, a re-solve would be needed (trivially
  repeatable with `solve.py --port`).
- Attack itself was not re-derived from scratch here; it is our own campaign's prior
  derivation (13391 AAR), re-executed and re-verified live.

## Files
- `chall.py`, `statement.txt`, `site.md` — provided material
- `solve.py` + `design3.json` — runnable solver (default host/port = live 14846; `--local` smoke test)
- `solve_live.log` — fresh live solve this session
- `flag_maybe_someday-maybe_someday_c.txt` — flag as handed by the service

## Sources
AAR names a prior in-campaign derivation (own 13391 AAR), no third-party sources. Disclosure wording preserved verbatim:
> Attack itself was not re-derived from scratch here; it is our own campaign's prior
>   derivation (13391 AAR), re-executed and re-verified live.
> No third-party writeups, no ctf_archive description.yml,
> no answer files consulted.

## Current state of the attack
Ledger-hygiene annotation (2026-11-02 twin sweep; append-only, claims untouched):
NON-CANONICAL twin pointer. SAME challenge instance and SAME derivation as
`challenge-13391-cryptohack-maybe_someday-googlectf2022`, which carries the fuller
derivation (protocol model, oracle predicates, design3 greedy+hill-climb — its
'The vuln'/'Attack' sections). Folder-lineage evidence relied on: this AAR line 19
'Attack (derived in-campaign, in sibling folder 13391; reused here)'; lines 25-26
'Full math details + limitations live in ../challenge-13391-...'; lines 11-12
provided chall.py md5 1da0bbcca674d9f5fdb078a93239dc14 byte-identical to the
sibling's; lines 37-38 shared flag string. Canonical = 13391 ⇒ ONE derivation
credit, counted once there (precedent: challenge-cryptohack-double_and_broken/AAR.md
'## Current state of the attack'). This folder's own record stands as written: a
fresh LIVE re-execution accepted under the separate card slug
`maybe_someday-maybe_someday_c` (lines 3-4, 33-39); the twin relation dedupes the
derivation credit only.
