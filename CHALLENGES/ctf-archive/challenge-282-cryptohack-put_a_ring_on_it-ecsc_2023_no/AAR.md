# AAR — put_a_ring_on_it (ECSC 2023 Norway, CryptoHack ctf-archive)

## Challenge
Monero-style *linkable ring signature* over Ed25519 (`chal.py` + provided `ed25519.py`).
16 rings × 16 members; the AES-128 key for the flag ciphertext is built from the
first byte of the **signer's** public key in each ring, so the goal is to break
signer anonymity in every ring (flag provenance: pure local derivation from
provided `data.json`; no service interaction needed).

## The bug
`random_scalar()` returns `SystemRandom().getrandbits(256)` — never reduced mod
the group order l ≈ 2^252.33. In `ring_sign`:
- Fake members store `sigc[i] = w`, `sigr[i] = q` **raw** → each ≥ l with
  probability ≈ 1 − l/2^256 ≈ 95%; both < l only ≈ 0.24% of the time.
- The real signer stores `sigc = (c−sumc) % l` and `sigr = (q − sigc·sk) % l`,
  both **always** < l.

So the signer index is exactly the one where `sigc[i] < l and sigr[i] < l`.
(Responses still verify fine since all equations hold mod l — the range leak is
invisible to a verifier, but fatal for anonymity here.)

## Attack
1. For each of 16 rings: candidate = indices with both responses < l.
   Result: 15 rings unique; ring 1 had one coincidental fake (expected ≈0.6
   collisions over 256 fakes) → 2 combos.
2. AES key = concat of first byte (hex [0:2]) of candidate pubkeys per ring.
3. CBC-decrypt `enc` with `iv`; the valid combo yields fully-printable plaintext.
   (chal.py does **not** PKCS7-pad; flag is exactly 32 bytes — first solve pass
   assumed padding and found nothing until that was relaxed.)

Key numbers: ring 1 real index = 15 (byte `a2`), the `b3` candidate at index 4
was the coincidental fake.

## Flag
Obtained by the derivation above and submitted; site accepted (ok:true,
solved count 271→272, score_delta 0 = archive value).

## Learning points
- Ring-size/leak aside, **scalar serialization range** is an anonymity channel:
  reduced vs unreduced mod-l responses perfectly separate real from simulated
  responses in this construction.
- Check the exact serialization/padding assumptions of the generator before
  trusting a plaintext oracle (no PKCS7 here).

## Limitations
- None material. Both candidates in ring 1 were exhausted (2 combos); uniqueness
  in the other 15 rings was confirmed by successful decryption of all 16 key
  bytes (single full-ASCII plaintext).

## Files
`statement.txt`, `site.md`, `chal.py`, `ed25519.py`, `data.json`,
`solve.py`, `flag_put_a_ring_on_it-ecsc_2023_no.txt`

## Sources
not recorded in run logs (pre-discipline solve)
