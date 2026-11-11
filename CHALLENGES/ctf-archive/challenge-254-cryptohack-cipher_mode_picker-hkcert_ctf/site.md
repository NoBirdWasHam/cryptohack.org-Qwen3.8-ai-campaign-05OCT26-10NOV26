# Site notes — cipher_mode_picker-hkcert_ctf
- Category page: /challenges/ctf-archive/ card (data-challenge="cipher_mode_picker-hkcert_ctf"); no direct /challenge/<slug>/ page.
- Listener: archive.cryptohack.org 2951 (raw socket works; site pages 404).
- File link in card body: /static/challenges/chall_0095f51d1a465af2ef03fb394d971c4e.py
- Protocol: 5 rounds of `<mode> <data|flag> [hex]`, modes ecb/cbc/cfb/ofb/ctr each once; replies hex ciphertext line.
- Submit: python3 submit_flag.py cipher_mode_picker-hkcert_ctf "<flag>" from workspace root.
