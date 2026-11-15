# AAR — Challenge 36: Triple DES (CryptoHack Symmetric Ciphers / AES)

**Result:** SOLVED (2026-10-16). Flag `[flag — recorded in FLAGS/aes/challenge-36-cryptohack-triple_des/flag.txt]` submitted and
accepted: score 8205 → 8265 (+60), solved 170 → 171.
**Date:** 2026-10-16 (UTC)

## Source
- Platform: CryptoHack (https://cryptohack.org/), account NoBirdWasHam
- Statement page: https://cryptohack.org/challenges/aes/ (card "Triple DES", slug `triple_des`, 60 pts, 3447 solves at time of run)
- Interactive service: https://aes.cryptohack.org/triple_des — GET `/encrypt/<key>/<plaintext>/`, `/encrypt_flag/<key>/` (2 endpoints; live page re-fetched this session, statement unchanged).
- Server source as provided on the challenge page (identical to the copy saved 2026-10-05):
  ```python
  IV = os.urandom(8)
  def encrypt(key, plaintext):
      key = bytes.fromhex(key); plaintext = bytes.fromhex(plaintext)
      plaintext = xor(plaintext, IV)
      ciphertext = DES3.new(key, DES3.MODE_ECB).encrypt(plaintext)
      ciphertext = xor(ciphertext, IV)
      ...
  def encrypt_flag(key):
      return encrypt(key, pad(FLAG.encode(), 8).hex())
  ```
- Not consulted for the solve: `/challenges/triple_des/solutions/`. (A web_search for the *technique*
  — allowed under the no-cheat rule — confirmed the "weak key" approach before the final run; the
  attack itself was derived and executed locally against the live service.)

## The structure
`C = W ⊕ E_K(P ⊕ W)`, W = 8-byte server IV (the only secret), K = fully attacker-chosen 3DES key.
The prior session (see git history of this folder) reduced the generic case to a 2^64 IV preimage
and correctly established that the complementation property is only a symmetry. That wall is
irrelevant: **the key is attacker-chosen, so we pick a DES weak key.**

## Attack (weak key — "a strange weakness of DES which a secure block cipher should not have")
1. **DES period-1 weak keys:** if all 16 round keys of a DES key are identical, the encryption and
   decryption key schedules coincide, so **E_K(X) = D_K(X)** — encryption is an involution.
   `0x00000000` and `0xFFFFFFFF` (8-byte DES keys) are both period-1 (C₀ = D₀ = constant 28-bit
   halves → every rotated copy is identical). AES has no analogous keys.
2. Use the 16-byte 3DES key `K = 0000000000000000 || FFFFFFFFFFFFFFFF` (K1 = 00×8, K2 = FF×8,
   K3 = K1). Both subkeys are involutions, so
   `T(X) = E_{K1}(D_{K2}(E_{K1}(X))) = E_{K1}(E_{K2}(E_{K1}(X)))` satisfies **T(T(X)) = X**
   (three involutions in palindromic order: T² = E_{K1}·E_{K2}·E_{K2}·E_{K1} = id).
   Verified locally before touching the server: `E==D` for both subkeys and `T(T(x))==x` (pycryptodome).
3. **Query 1:** `ct = enc_flag(K) = W ⊕ T(F ⊕ W)` where `F = pad(FLAG)` (40 bytes, 5 blocks).
4. **Query 2:** feed `ct` back as the plaintext: `pt = enc(K, ct) = W ⊕ T(ct ⊕ W)
   = W ⊕ T(T(F ⊕ W)) = W ⊕ (F ⊕ W) = F`. **The IV cancels because each application of the
   construction is (⊕W)∘E∘(⊕W) and (⊕W)∘(⊕W) = id.**
5. `pt = pad(FLAG) = [flag — recorded in FLAGS/aes/challenge-36-cryptohack-triple_des/flag.txt]‖0x06×6` → strip PKCS7 → flag.

Total: 2 oracle queries.

## Verification (exact commands + outputs)
```
$ "~/tools/crypto-ctf/venv/Scripts/python.exe" solve_weakkey.py
subkeys are involutions (E==D): [True, True]
T(T(x)) == x: True
weak key: 0000000000000000ffffffffffffffff
flag ct len: 40 blocks: 5
recovered pad(FLAG): b'[flag — recorded in FLAGS/aes/challenge-36-cryptohack-triple_des/flag.txt]\x06\x06\x06\x06\x06\x06'
FLAG: [flag — recorded in FLAGS/aes/challenge-36-cryptohack-triple_des/flag.txt]
format crypto{...}: True
```
Submission (from `~/Practice_runs/cryptohack_org`):
```
$ "~/tools/crypto-ctf/venv/Scripts/python.exe" submit_flag.py triple_des "[flag — recorded in FLAGS/aes/challenge-36-cryptohack-triple_des/flag.txt]"
{"submitted": "[flag — recorded in FLAGS/aes/challenge-36-cryptohack-triple_des/flag.txt]", "submit": {"ok": true, "status": 200, "body": "Flag submitted. Press back to return to the challenge. Please enable JavaScript for a better experience"}, "before": {"score": 8205, "solved": 170}, "after": {"score": 8265, "solved": 171}, "score_delta": 60}
```
score_delta = 60 > 0 → accepted (first solve; server response body is identical for right/wrong, so
the API score delta is the ground truth).

## Lessons
- **Chosen-key + weak key = free decryption.** Whenever the attacker chooses the block-cipher key
  of an E(K, ·) oracle, check the cipher for keys where E = D (DES period-1 weak keys) or where E
  has small order: then feeding a ciphertext back as plaintext inverts the construction, and any
  IV/key-whitening of the form `W ⊕ E(· ⊕ W)` cancels out.
- **The complementation property was a red herring for exploitation** (it only yields verifiable
  symmetries here); the exploitable DES weakness was the *weak key schedule*, not complementation.
  Two distinct "strange weaknesses" of DES; the challenge statement's phrasing fit either, and the
  weak-key one is the one that breaks the construction.
- **Verify the algebra locally before spending live queries**: `E==D` per subkey and `T(T(x))==x`
  were checked with pycryptodome first; the live attack then needed exactly 2 requests.
- pycryptodome rejects 24-byte DES3 keys with K1==K2 ("degenerates to single DES") — use 16-byte
  keys (K1||K2, K3=K1) or distinct weak subkeys to avoid the local crash the prior session hit.

## Evidence
- `solve_weakkey.py` — full solver (local verification + 2-query live attack + PKCS7 strip).
- `solve_weakkey_log.txt` — (first failed run, kept for the record; see Verification above for the good run).
- `flag_recovered.txt` — recovered flag string.
- `flag.txt` — exact submitted string.
- Prior-session artifacts (probe.py, model.py, recover.py, verify_id.py + logs) remain as the record
  of the 2^64-wall analysis that this session superseded.

## Configuration (environment for this run)
- **Date (UTC):** 2026-10-16
- **Host OS:** Windows 11, shell = git-bash/MSYS
- **User:** OWNER
- **Interpreter:** `~\tools\crypto-ctf\venv\Scripts\python.exe` (Python 3.12, pycryptodome)
- **Working dir:** `~\Practice_runs\cryptohack_org\challenge-36-cryptohack-triple_des`
- **Agent:** Hermes Agent (subagent)
- **No-cheat rule applied:** statement + provided source only for the solve; web_search used solely
  to confirm the weak-key technique; no solutions page, no third-party flag.

## Sources
- Case (c) — prior-material disclosure preserved verbatim from this AAR (line-wrapping only
  normalized): "(A web_search for the *technique* — allowed under the no-cheat rule — confirmed
  the "weak key" approach before the final run; the attack itself was derived and executed
  locally against the live service.)"
- No textbook/paper/RFC cited; no solutions page, no third-party flag (per the run logs).
