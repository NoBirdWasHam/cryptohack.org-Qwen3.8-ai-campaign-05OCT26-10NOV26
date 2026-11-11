# U-turn (Breizh CTF 2025) — cryptohack archive card
- URL: https://cryptohack.org/challenges/ctf-archive/ (card data-challenge="u-turn-breizh_ctf2025")
- Statement: "HaSh functIonS are one-way, right?"
- Files: /static/challenges/u-turn_2d7c5948514be946984b77efddca3aa0.zip (saved as u-turn.zip)
- No listener; offline second-preimage task. Flag format BZHCTF{[0-9a-f]{16}}.
- Hash: PKCS7-pad + XOR-fold -> 16 bytes; balanced-quinary digits ([-2..2]) truncated to 50; h = A*x mod 256, A 48x50 from A.txt. output.txt = target hash.
