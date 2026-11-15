---
name: cryptohack-aes-http-oracles
description: Use when solving CryptoHack aes.cryptohack.org challenges.
version: 1.0.0
author: Hermes Agent
license: MIT
metadata:
  hermes:
    tags: [ctf, crypto, cryptohack, aes]
    related_skills: [ctf-crypto-attacks, cryptohack-socket-challenges]
---

# CryptoHack AES-course HTTP oracle challenges (aes.cryptohack.org)

## When to Use
AES-course slugs on https://aes.cryptohack.org/<slug>/ (block_cipher_starter … bean_counter).
Statements need login, but the SERVICE root `https://aes.cryptohack.org/<slug>/` serves the
full server source (routes + code) unauthenticated — curl it and parse
`<pre class="sourceBlock"><code class="python">…`. Routes are GET-with-path-params
(`/slug/route/<param>/`), not POST JSON.

## Per-challenge (all verified 2026-11-14)
- block_cipher_starter / ecbcbcwtf / passwords_as_keys: starter bugs — ECB decrypt oracle
  over encrypt_flag output; CBC ct + ECB-decrypt oracle ⇒ P_i=D(C_i)^C_{i-1};
  key=md5(word from /usr/share/dict/words gist in source), offline brute vs 'crypto{' prefix.
- ecb_oracle: ECB byte-at-a-time on pad(pt+FLAG); LF from length probe (total=16*(floor((LF+L)/16)+1),
  first length jump ⇒ LF+L≡0 mod16). PITFALL: psz=(15-i)%16; when it is 0 use 16 (empty path
  segment → 404); candidate block may be queried as its own 16-byte plaintext.
- flipping_cookie: cookie 'admin=False;expiry=…'; flip IV bytes 6..10 F→T a→r l→u s→e e→; ⇒
  'admin=True;;' token after split(';'); padding untouched (only P0 changes). IV-only, no epoch guess.
- lazy_cbc: IV==KEY and /receive leaks full decrypted hex in the UnicodeDecodeError message.
  C1=encrypt(P); receive(C1||C1) block1 = P^KEY^C1 ⇒ KEY ⇒ get_flag/<KEY>.
- symmetry: OFB with attacker-chosen IV: encrypt_flag iv reused in /encrypt/<00..>/<iv>/ = keystream.
- bean_counter: StepUpCounter(step_up=False) bug `int(value)-self.stup` (False=0) ⇒ keystream is
  CONSTANT ⇒ PNG under 16-byte repeating XOR; KS from magic+IHDR length 0000000d+'IHDR'; flag is
  RENDERED in the image → vision_analyze (timeouts flaky — resize 2x LANCZOS, retry; verify by
  per-line crops).

## Pitfalls
- GET path params: empty hex ⇒ `route//` ⇒ 404.
- aes.cryptohack.org occasionally connect-timeouts mid-solve: retry loop in the oracle wrapper.
- vision_analyze on ~300px images times out often; upscale first, and always cross-check a flag
  read by vision with line-level crops.
- cryptohack.org challenge pages redirect logged-out requests to /challenges/; the AES category
  page embeds statements; source comes from the service root page, not cryptohack.org.
