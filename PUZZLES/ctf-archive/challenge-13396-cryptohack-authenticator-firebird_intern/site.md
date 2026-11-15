# Authenticator (Firebird Internal CTF) — archive.cryptohack.org

- Slug: `authenticator-firebird_intern`
- Service: `archive.cryptohack.org:40156` (single-shot mutual-auth handshake, 10 s alarm)
- Source: chall.py (downloaded from cryptohack /static/challenges/chall_850a94d7e3ab9d1a46eb9d921e29e43e.py)
- Protocol (password = 6 distinct chars from [0-9a-zA-Z], ~36 bits, fresh per connection per source):
  1. attacker sends 16-byte challenge_client (hex)
  2. server prints response_server = blake3(P || b"HANDSHAKE_FROM_SERVER" || challenge_client).hex()
     and challenge_server = os.urandom(16) (hex)
  3. attacker must send response_client = blake3(P || b"HANDSHAKE_FROM_CLIENT" || challenge_server)
  4. correct => "Congrats! {flag}"

## Analysis notes (first principles)
- P||S1||C1 = 6+21+16 = 43 bytes: single blake3 block, zero-padded to 64. S1/S2 same length,
  identical first 15 bytes ("HANDSHAKE_FROM_"), differ in the last 6 (SERVER vs CLIENT, block offsets 21..26).
- No classic length-extension (blake3 root flag), target message is not an extension of the oracle message.
- Oracle range = {H(P||S1||x)}; target H(P||S2||C2) is outside it (RO-model secure design).
- 62P6 = 44,261,653,680 passwords; 10 s live alarm makes naive in-session brute force impossible.
- Therefore probe the service for: password persistence across connections, alarm behavior, remote-vs-local source mismatch.
