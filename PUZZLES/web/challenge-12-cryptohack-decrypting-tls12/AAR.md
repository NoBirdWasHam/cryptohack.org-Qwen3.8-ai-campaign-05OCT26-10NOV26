# AAR — Challenge 158: Decrypting TLS 1.2

**Result:** **SOLVED + leaderboard-verified** (account NoBirdWasHam, 2026-10-13) — flag
`[flag — recorded in FLAGS/web/challenge-12-cryptohack-decrypting-tls12/flag.txt]` accepted via submit_flag.py; score
6470→6500, solved 140→141. (Slug: `decrypting-tls12`.)
**Date:** 2026-10-13 (UTC)

## Source
- **Platform:** CryptoHack (https://cryptohack.org/)
- **Category:** Web (https://cryptohack.org/challenges/web/)
- **Challenge:** "Decrypting TLS 1.2" (30 pts, slug `decrypting-tls12`); solution page
  `/challenges/decrypting-tls12/solutions/` NOT consulted — no-cheat rule.
- **Provided files (downloaded to `_web_pcap/`):** `tls2.cryptohack.org.pcapng`,
  `privkey.pem` (2048-bit RSA, **PKCS#8** `-----BEGIN PRIVATE KEY-----` header).

## The flag
Recorded in `FLAGS/web/challenge-12-cryptohack-decrypting-tls12/flag.txt` — kept out of AAR prose per the flag-separation rule; sha256 in `FLAGS/INDEX.jsonl`.

## How it was solved
Intended path is the challenge's own: decrypt the TLS 1.2 RSA-key-exchange stream using the
leaked server private key, then read the flag out of the HTTP/2 body. The tool that does this
correctly is **tshark** (Wireshark's CLI).

Steps (all executed, all verified):
1. Installed tshark 4.6.9 (see `wireshark-tshark` skill for the no-admin Windows install path).
2. Confirmed ground truth against tshark before trusting any hand parse:
   `tshark -r tls2.cryptohack.org.pcapng -Y "tls.handshake.type==1" -T fields -e tls.handshake.random`
   → ClientHello random `70d5bf9e…`, ServerHello random `1c1ecca9…` (matched my scapy parser).
3. **Converted the key to PKCS#1** — this was the actual blocker:
   `openssl rsa -in privkey.pem -traditional -out privkey_pkcs1.pem`
   (tshark's `uat:rsa_keys` rejects the PKCS#8 header with `Error processing rsa_privkeys`.)
4. Decrypted the whole stream:
   ```
   tshark -r tls2.cryptohack.org.pcapng \
     -o 'tls.desegment_ssl_records:TRUE' \
     -o 'tls.desegment_ssl_application_data:TRUE' \
     -o 'uat:rsa_keys:"privkey_pkcs1.pem",""' -Y http2 -x
   ```
   → full handshake + HTTP/2 frames decrypted; `HEADERS[1]: GET /`, then `DATA[1]` carrying the flag.
5. Extracted the flag from the `Decrypted TLS (70 bytes)` DATA block; submitted; accepted.

No writeup, solution page, or external source was consulted for the solve.

## The hand-rolled detour (and why it failed)
Before installing tshark, ~50 tool calls were spent hand-rolling the TLS 1.2 stack (PRF, key
schedule, AES-256-GCM) in Python. Every independently-verified piece was correct:
- cipher `0x009d = TLS_RSA_WITH_AES_256_GCM_SHA384` (IANA-confirmed; RSA key exchange);
- CKX ciphertext decrypts under `privkey.pem` to a clean 48-byte PKCS#1 v1.5 premaster
  (`0303…`), so the key + premaster are genuinely correct;
- leaf cert (CN=tls2.cryptohack.org) matches `privkey.pem`;
- record walk byte-exact (single connection, 8 server records);
- PRF formula read verbatim from RFC 5246 §5/§6.3.

Yet **no** combination of (PRF ±seed, random order for master & key_block, MAC-key present/absent,
nonce order, AAD on/off) authenticated the Finished or the first app-data record in either
pycryptodome or the `cryptography` library.

**Decisive diagnosis:** tshark decrypted the *same* first-server-app-data record (8 nonce + 40 ct
+ 16 tag) that my keys turned into garbage — same framing, different keys. Critically, tshark's
decrypted **Finished carries a 12-byte verify_data** (`a5ab0560c42468905b8eedd4`), which is
SHA-1-sized. The advertised GCM-SHA384 suite requires a **48-byte (SHA-384) verify_data**. That
inconsistency means the capture's generator computed the Finished with a different PRF hash than
the suite advertises — a non-standard/custom TLS 1.2 stack. A strict SHA-384 hand-rolled schedule
therefore cannot reproduce the generator's auth tags, regardless of how many key-schedule variants
are tried. tshark follows the generator's *actual* key schedule and authenticated every record.

*(Labeled: the exact PRF-hash mismatch is inferred from the 12-byte verify_data, not confirmed
against the generator's source. What is fully verified is that tshark decrypted the stream and the
flag was accepted.)*

## Learning points
- **Use the purpose-built tool.** For "decrypt a TLS 1.2 stream with a leaked private key,"
  tshark's `uat:rsa_keys` + desegment options is the entire solve. Hand-rolling PRF+GCM is a
  rabbit hole — it burned ~50 calls and still failed, while tshark did it in 2 commands.
- **Key format gotcha:** tshark `uat:rsa_keys` needs **PKCS#1** (`RSA PRIVATE KEY`), not PKCS#8
  (`PRIVATE KEY`). `openssl rsa -in key.pem -traditional -out key_pkcs1.pem` converts it. A
  PKCS#8 key fails *silently-ish* (`Error processing rsa_privkeys`) and nothing decrypts.
- **Cross-check the tool against your parser** (tshark's `tls.handshake.random` vs your own)
  before trusting offsets.
- **A Finished whose verify_data length doesn't match the suite's PRF hash** is a red flag for a
  non-standard capture. When you see it, stop hand-deriving and lean on the reference decoder.
- **Verify by submission**, not by local auth success alone — the accepted flag is the ground truth.

## Documentation / tooling added
- New skill `wireshark-tshark` (research category) capturing the install path, the
  `uat:rsa_keys` CTF workflow, and the key-format/desegment pitfalls.
- tshark 4.6.9 installed at `~\tools\wireshark\` (user-level, no admin).
