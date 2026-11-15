# Collider (collider) — SOLVED

- **Platform:** CryptoHack · **Category:** Hash Functions → Collisions · **Points:** 50
- **Source file:** `13389.py` (in this folder) · **Service:** socket.cryptohack.org 13389
- **Solved:** 2026-10-14 by NoBirdWasHam · **Flag:** `[flag — recorded in FLAGS/hashes/challenge-3-cryptohack-collider/flag.txt]`
- **Verification:** `submit_flag.py` → score 7245 → 7295 (+50), solved 156 → 157.

## Statement (verbatim)

> Check out my document system about particle physics, where every document is uniquely
> referenced by hash.
>
> Connect at socket.cryptohack.org 13389
>
> Challenge files: 13389.py

## The system (from 13389.py)

Per connection the server holds:

```python
self.documents = {
    "508dcc4dbe9113b15a1f971639b335bd": b"Particle physics ...",   # 440 B
    "cb07ff7a5f043361b698c31046b8b0ab": b"The Large Hadron Collider ...",  # 349 B
}
```

For each submitted `document` (hex), it computes `md5(document)`:

- hash in dict, same content → "Document already exists in system"
- hash in dict, **different content** → "Document system crash, leaking flag: …" ← goal
- new hash → added (max 5 docs)

## Why a generic collision pair works (the crux)

1. **Live probing established per-CONNECTION state**: the same random document sent on
   two separate connections returns "added" both times (a shared instance would answer
   "already exists"). The two pre-stored hashes are therefore the only pre-existing keys
   per session — and their keys match their content exactly (verified by extracting the
   bytes from the source with `ast`), so hitting them needs a **second preimage** on MD5
   (~2^123 — infeasible). A generic collision pair across two connections does nothing.
2. **But the connection stays open and processes multiple JSON lines per session.**
   Within ONE connection the documents I add persist: send A → "added"; send B with
   `md5(B) == md5(A)`, `B != A` → **crash → flag**. No second preimage required.

## The collision pair

Generated locally with `md5fastcoll` (Marc Stevens' hashclash core, built from source —
see `md5fastcoll/BUILD.md`):

- `msg1.bin`, `msg2.bin`: 128 bytes each, `md5 = 3778dd67655b79828307612d215f560a`, distinct.
- Verified locally with `hashlib.md5` before sending.

## Files

- `solve.py` — single-connection two-request exploit (re-runnable; state is per-connection).
- `13389.py` — server source (provided by the challenge).
- `msg1.bin` / `msg2.bin` — the collision pair used.
- `md5fastcoll/` — unmodified hashclash core + minimal driver + built exe + build notes.
- `flag.txt` — the flag.
