# Course lesson — Paper Plane (Symmetric Ciphers)

**Record type:** course lesson — completed as a graded course lesson during the run; the site lists this row under Symmetric Ciphers as challenge `paper_plane`.
**Status:** completed 2026-10-06 · **Points:** 120 · **Site:** https://cryptohack.org/challenges/paper_plane/
**Ledger row:** `course__paper_plane` (E1)

## Run record (working corpus, sanitized; written during the course run)
# AAR — Paper Plane (IGE padding oracle)

## 1. Result

**SOLVED** — flag ``flag — recorded in FLAGS/aes/course-paper_plane/flag.txt``, derived 2026-10-05 (UTC), submitted and
solved-star verified on the leaderboard 2026-10-06.

## 2. Source

- Statement + provided source: `https://aes.cryptohack.org/paper_plane/` (fetched 2026-10-06, verbatim in `site.md`)
- Category card: `https://cryptohack.org/challenges/aes/`
- Live service: `https://aes.cryptohack.org/paper_plane/` (`/encrypt_flag/`, `/send_msg/...`)
- **NOT consulted:** `/solutions/`, `/solves/`, the 8 published solutions, no writeups.

## 3. The flag and its verification

- Flag: ``flag — recorded in FLAGS/aes/course-paper_plane/flag.txt``
- Verified: (a) the recovered plaintext is a valid IGE decryption of the *server's own*
  `encrypt_flag()` ciphertext (the oracle accepted it as valid padding at every block, which is
  only possible if the bytes are the true decryption); (b) leaderboard `#check-paper_plane`
  star lit after `POST /submit/paper_plane/`.

## 4. How it was solved (reproducible)

1. `encrypt_flag()` → `(C, m0, c0)`; here `C` was **2 blocks** (40-byte FLAG + PKCS7 → 32B… actually 2 blocks).
   IGE decrypt: `P_i = D(C_i ⊕ P_{i-1}) ⊕ C_{i-1}`, `P_{-1}=m0`, `C_{-1}=c0`.
2. **Key observation:** for a *1-block* ciphertext `A` with attacker-chosen `m0'`, `c0'`:
   `P = D(A ⊕ m0') ⊕ c0'`. Choose `A = Z_i` (any 16 bytes) and `m0' = 0^16` ⇒
   `P = D(Z_i) ⊕ c0'`. The oracle ("Message received" iff PKCS7-valid) is then a **classic
   16-byte padding oracle** over `W = D(Z_i)`: `oracle(c0') = valid_padding(W ⊕ c0')`.
3. Per flag block `i`, set `Z_i = C_i ⊕ P_{i-1}` (with `P_{-1} = m0`). Then `W = D(Z_i) = P_i ⊕ C_{i-1}`
   (with `C_{-1} = c0`), so `P_i = W ⊕ C_{i-1}`. Recover `W` byte-by-byte (j=15..0): target padding
   value `v = 16 − j`, brute-force `w` in `c0'[j]` until the oracle accepts; standard ~256·16 queries/block.
4. Chain: `P_0` needs only `(C, m0, c0)`; `P_1` needs `P_0` (already recovered). Unpad PKCS7 → flag.

~2·256·16 ≈ 8192 oracle calls (measured ~a few thousand; see `run_log.txt`). Script: `solve.py`.

## 5. Learning points

- **IGE is just a padding oracle in disguise.** IGE's "one bad bit corrupts everything" is
  exactly the property that makes its decrypt a *chosen-ciphertext* function of the form
  `D(A ⊕ m0') ⊕ c0'` — the same shape as CBC's `D(C_i) ⊕ C_{i-1}`. Any mode whose single-block
  decryption is `D(·) ⊕ (attacker-controlled value)` is a textbook padding oracle.
- **Reduce to the canonical primitive.** Instead of reasoning about IGE's chaining, map each
  block to `D(Z_i) ⊕ c0'` and attack that with the well-understood 16-byte oracle. The chaining
  (recovering `P_{i-1}` to form `Z_i`) is bookkeeping on top.
- **Chosen `m0' = 0`** is the cleanest handle — it zeroes the first XOR and leaves `c0'` as the
  sole oracle knob.

## 6. What I did / did not do

- Did: fetched statement + source verbatim; derived the IGE→padding-oracle reduction; ran
  `solve.py` (one clean pass); saved `run_log.txt`, `flag.txt`, `solve.py`; submitted and
  verified the star.
- Did not: open solutions/writeups; hammer beyond the needed ~few-thousand oracle calls; touch
  anything beyond the two stated endpoints.

## 7. Limitations

- The flag was derived from the live service (the intended source for an interactive
  challenge) and then leaderboard-verified; no independent offline re-derivation was possible
  (KEY unknown), but the per-block oracle acceptance is itself the proof the bytes are the true
  decryption.

## 8. Configuration

- **Date:** solved 2026-10-05; star verified 2026-10-06 (UTC)
- **Host OS / shell:** Windows 11 (MSYS_NT-10.0-26200), git-bash
- **User:** <USER>
- **Interpreter:** python3 = Python 3.10.11 (pycryptodome available)
- **Working dir:** `~\Practice_runs\cryptohack_org\challenge-46-cryptohack-paper-plane\`
- **Agent / model:** Hermes Agent (Nous Research), qwen38-27b, custom provider, desktop
- **Tools:** terminal (python3), browser (submit + star verification via in-page sync XHR)
- **Network contacts:** `https://aes.cryptohack.org/paper_plane/` (encrypt_flag + send_msg), `https://cryptohack.org/challenges/aes/` (submit/verify)
- **Key files:** `solve.py` (solver), `run_log.txt` (per-block W recovery transcript), `flag.txt`, `site.md`

## Vulnerability (plain words)

IGE decryption is `P_i = D_K(C_i XOR P_{i-1}) XOR C_{i-1}`, with the attacker-supplied initial
pair `(m0, c0)`. The service decrypts attacker-chosen messages and leaks one bit: whether the
PKCS#7 padding is valid ("Message received"). Submitting a *one-block* message `(Z, m0', c0')`
with `m0' = 0^16` makes the server compute `D_K(Z) XOR c0'` and report padding validity -- the
CBC padding-oracle shape `D(.) XOR (attacker-chosen value)`, with `c0'` as the oracle knob. The
cross-block chaining is bookkeeping: choosing `Z_i = C_i XOR P_{i-1}` makes `D_K(Z_i) = P_i XOR
C_{i-1}`, i.e. a flag block XORed by a known constant.

## How the answer follows

Per flag block, the standard 16-byte padding-oracle walk recovers `W = D_K(Z_i)` byte-by-byte:
for position j = 15..0 with target padding value `v = 16 - j`, fix bytes j+1..15 of `c0'` to the
already-recovered `W` bytes XOR `v`, brute-force `c0'[j]` over at most 256 values until the oracle
accepts; then `W[j] = w_j XOR v` and `P_i[j] = W[j] XOR C_{i-1}[j]`. `P_0` uses the given
`(m0, c0)`; `P_1` uses recovered `P_0`; PKCS#7 unpadding yields
``flag — recorded in FLAGS/aes/course-paper_plane/flag.txt`` (`flag.txt`). Cost worst-case 2 blocks x 16 bytes x 256 = ~8192 oracle
calls (AAR section 4; `run_log.txt` holds the per-block W transcript). Leaderboard star after
`POST /submit/paper_plane/`.

## Limitations / attempts that failed

- No offline re-derivation is possible (the KEY is unknown); the proof the bytes are the true
  decryption is that only the true decryption produces valid PKCS#7 under the server's key,
  consistently, at every block (AAR section 7).
- AAR section 4 records fewer live queries than the 8192 worst case (correct bytes found early).
  No other failed attempts are recorded in run logs.

## Sources

- `https://aes.cryptohack.org/paper_plane/` (statement + provided source, verbatim in `site.md`);
  category card `https://cryptohack.org/challenges/aes/`.
- Self-derived per logs (`solve.py`, `run_log.txt`). NOT consulted: `/solutions/`, `/solves/`,
  published solutions, writeups (AAR section 2).
- Upgrade note: mechanism restated from AAR section 4 + `solve.py`; live service NOT re-run at
  upgrade time (offline editor unit).

