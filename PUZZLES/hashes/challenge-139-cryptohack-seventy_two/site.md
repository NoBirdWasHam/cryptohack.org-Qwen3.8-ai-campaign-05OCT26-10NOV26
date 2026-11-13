# Seventy-Two (seventy_two) — SOLVED

- **Platform:** CryptoHack · **Category:** Hash Functions → Key Derivation · **Points:** 50
- **Slug:** `seventy_two` · **Folder:** `challenge-139-cryptohack-seventy_two`
- **Service:** socket.cryptohack.org 13433 (JSON line protocol) · **Files:** `13433.py` (in this folder)
- **Solved:** 2026-10-14 by NoBirdWasHam · **Flag:** `[flag — recorded in FLAGS/hashes/challenge-139-cryptohack-seventy_two/flag.txt]`
- **Verification:** `submit_flag.py` → score 7195 → 7245 (+50), solved 155 → 156.

## Statement (verbatim)

> Blue Rock's directory service binds every credential to the tenant and the account name
> before hashing it. A hash stolen from one tenant's database should be worthless when
> replayed against another. But there is a flaw in the scheme.
>
> bcrypt was introduced back in 1999 and several better key derivation functions exist now
> such as Argon2id.
>
> Connect at socket.cryptohack.org 13433
>
> Challenge files: 13433.py

## The flaw (one line)

`material = f"{TENANT}|{username}|{password}".encode()` is fed to **bcrypt**, which
**silently truncates its input to 72 bytes** (the title's "Seventy-Two"). For the account
`k.barrymore@corp.bluerock.example` the prefix `TENANT|username|` is **71 bytes**, so only
the **first byte** of the 32-char random password ever affects the hash → **62 possible
logins total** → trivial brute force (hit on guess 51: password starts with `Y`).

## Per-account effective password budget (72 − len("TENANT|user|"))

| account | prefix | pw bytes hashed | guesses |
|---|---|---|---|
| root | 42 | 30 | 62^30 (infeasible) |
| backup@corp.bluerock.example | 66 | 6 | 5.7e10 (infeasible) |
| m.laurent@corp.bluerock.example | 69 | 3 | 238,328 (feasible but slow) |
| **k.barrymore@corp.bluerock.example** | **71** | **1** | **62** ← used |

## Files

- `solve.py` — the brute force (62 sequential logins, ~25 s).
- `13433.py` — challenge source (server).
- `flag.txt` — the flag.
