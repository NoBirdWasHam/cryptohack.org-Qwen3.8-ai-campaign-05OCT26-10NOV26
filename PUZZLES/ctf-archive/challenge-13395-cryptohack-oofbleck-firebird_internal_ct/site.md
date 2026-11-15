Archive: https://archive.cryptohack.org/challenges/oofbleck-firebird_internal_ct/
Card source: cat_ctfarch.html data-challenge="oofbleck-firebird_internal_ct"
Files fetched from https://cryptohack.org/static/challenges/<hash> (archive.cryptohack.org 404s them; TLS cert wrong-principal there too).
chall.py: AES.new(iv, MODE_OFB, key) -> args SWAPPED: AES key = random iv (sent in clear), OFB IV = secret key.
