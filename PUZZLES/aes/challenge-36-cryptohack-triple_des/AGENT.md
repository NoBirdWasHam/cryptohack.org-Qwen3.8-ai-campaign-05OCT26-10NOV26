---
record: agent-aar
puzzle: challenge-36-cryptohack-triple_des
category: Symmetric Ciphers
url: https://cryptohack.org/challenges/triple_des/
status: solved
date: 16 Oct 2026
flag_ref: "FLAGS/aes/challenge-36-cryptohack-triple_des/flag.txt"
flag_sha256: 52a0ed235b912f19d6ccb2cc5b7871ce3adcc17dd2e1b28bd9baca15b492fd8f
skills: []
human_twin: AAR.md
---

# AGENT — Challenge 36: Triple DES (CryptoHack Symmetric Ciphers / AES)
Machine-optimized twin of the human AAR in this directory (mechanically regenerated from it; carries no extra facts).
Epistemic tags: OBSERVED = artifact/evidence present in this dir · NOT OBSERVED = not recorded anywhere in the corpus.

## procedure — extracted from AAR section "Attack (weak key — "a strange weakness of DES which a secure block cipher should not have")" [OBSERVED text; evidence tag applies to its source, not each claim]
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

## reusable-rules
- none recorded [NOT OBSERVED] — derive from procedure above

## anti-patterns / limits
- none recorded [NOT OBSERVED]

## artifacts [OBSERVED]
- code: model.py, probe.py, probe2.py, recover.py, solve_weakkey.py, verify_id.py
- data/logs: flag_recovered.txt, solve_weakkey_log.txt
- flag value: never in this file; sha256 against `FLAGS/INDEX.jsonl`

## references
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
