# AAR — pekobot (AIS3 Pre-Exam) / pekobot-ais3_pre-exam2022

## Result
SOLVED. Flag: `[flag — recorded in FLAGS/ctf-archive/challenge-54-cryptohack-pekobot-ais3_pre-exam2022/flag.txt]` — submitted, accepted (site solved count 289→290; archived challenge, 0 score pts).

## Vulnerability (self-derived from provided server.py)
Option 1 computes `S = Point(E, x, y) * d` with **no curve-membership check**, and quotes are a fixed public list (known plaintext). The key move:
1. Option 2 returns `C1 = rG`, `C2 = flag_pad XOR point_to_bytes(rP)`.
2. Feed `C1`'s coordinates into option 1: server returns `quote XOR point_to_bytes(C1*d)`, and `C1*d = r(dG) = rP` — exactly the flag keystream point. No ECDLP needed.
3. XOR the ct against each of the 8 known quotes (padding `ljust(64, b"\0")` makes the keystream exact); only the right quote yields `C2 XOR key` starting `AIS3{` and printable through `}`.

Twist/small-subgroup attack on d was considered and ruled out: #twist = 3·5·13·179·(241-bit prime) → only ~15 bits of d reachable via F_p oracle; irrelevant once the C1→rP oracle is noticed.

## Validation
- In-process harness (`harness.py`) replicating server logic from the provided `elliptic_curve.py` recovered a planted local flag → trick verified on provided data before touching the service.
- Live fingerprint: `archive.cryptohack.org:45328` banner/menu matched server.py exactly (session prints `watashi no public key`, then `AIS3{`-flag decrypted on first attempt).

## Files
- `statement.txt`-equivalent: challenge description captured in cat_ctfarch.html grep (host/port/files quoted below in solve notes).
- `elliptic_curve.py`, `server.py` — downloaded from cryptohack static links in the card.
- `harness.py` — offline replica + attack validation.
- `solve.py` — live exploit (prompt-token-synced socket).
- `AAR.md` — this file.

## Issues
- First live run desynced parsing: concatenating the `y: `-prompt response with the post-input response glued prompt+ct on one line; fixed by parsing only the post-`y` response.
- gmpy2 kernel/python mismatch (kernel python lacks gmpy2) — ran math via terminal python3.
- Budget used: ~15 calls.

---

<!-- AAR batch #9 quality upgrade (2026-11-02): publication sections appended; everything above this marker byte-identical to the pre-append AAR (hash in aar_batch9_pre.sha). -->

## Vulnerability (plain words)
The server's quote-signing path multiplies *any* (x, y) pair you hand it by the secret key d without checking the point lies on the curve, and the flag-encryption path hands you `C1 = rG` in the clear. Scalar multiplication still evaluates on off-curve coordinates, so feeding `C1`'s coordinates into the quote path returns `quote XOR point_to_bytes(C1*d)`, and `C1*d = (rG)d = r(dG) = rP` — exactly the keystream point masking the flag. The secret is never extracted; the two oracles compose.

## How the answer follows
1. From the flag-encryption option: `C2 = flag_pad XOR point_to_bytes(rP)`, with `C1 = rG` public.
2. Feed coords of `C1` to the quote option: response `= quote XOR point_to_bytes(C1*d) = quote XOR point_to_bytes(rP)` (curve-membership unchecked, ECDLP never needed).
3. XOR out: `C2 XOR response XOR quote = flag_pad` for the *correct* quote; the 8 quotes are a fixed public list and padding `ljust(64, b"\0")` makes the keystream byte-exact. The unique candidate starting `AIS3{` and printable through `}` is the flag: `[flag — recorded in FLAGS/ctf-archive/challenge-54-cryptohack-pekobot-ais3_pre-exam2022/flag.txt]`.
4. Validation chain: offline replica `harness.py` recovered a planted local flag from the provided `elliptic_curve.py` *before* touching the service; live `archive.cryptohack.org:45328` menu matched `server.py`, flag decrypted on first live attempt (solved count 289 to 290).

## Limitations / attempts that failed
- Twist/small-subgroup recovery of d was considered and *ruled out on paper* before the oracle was noticed: `#twist = 3*5*13*179*(241-bit prime)` gives only ~15 reachable bits of d via an F_p oracle — irrelevant once C1 -> rP composition was seen.
- First live run had a parsing desync (prompt echo glued to the ciphertext line); fixed by parsing only the post-`y` response.
- gmpy2/kernel-python mismatch forced math onto terminal python3. No further failures.

## Sources
- Self-derived per logs from the challenge-provided `server.py` / `elliptic_curve.py` only; no CryptoHack /solutions//solves or third-party writeups consulted; no external math reference was needed (ECDH algebra is in the provided file).
- Upgrade-time comprehension check (batch #9, 2026-11-02): re-derived the `C1*d = rP` collapse and the XOR triple from the AAR record and `solve.py`/`harness.py` offline — no live re-run, claims/flag untouched.
