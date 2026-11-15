# Oofbleck (Firebird internal CTF): chall.py calls AES.new(iv, MODE_OFB, key) --
# key/IV args SWAPPED: the AES key is the random iv which is PREPENDED in output.txt,
# so the attacker knows the AES key. The secret `key` is only the OFB initial state.
# Keystream: X1=E_K(X0), X_{i+1}=E_K(X_i). Known keystream: X1[:9] via header
# 'firebird{'; X5[3:16] via PKCS7 pad (flag len 68 -> 0x0c*12); X5[2]? -> flag byte 67
# is '}', bytes 64..66 are \w -> X5[:3] has 62^3 candidates. Brute those, walk back
# X1 = D^4(X5), require X1[:9]==known and \w tail; forward-decrypt flag. 238k AES ops.
import base64, itertools, re, string
from Crypto.Cipher import AES
raw = base64.b64decode(open('output.txt').read().strip())
iv, ct = raw[:16], raw[16:]
enc = AES.new(iv, AES.MODE_ECB); E, dec = enc.encrypt, enc.decrypt
W = (string.ascii_letters + string.digits + '_').encode(); Wset = set(W)
x1_known = bytes(a ^ b for a, b in zip(ct[:9], b'firebird{'))
x5_tail = bytes(a ^ 0x0c for a in ct[68:])
p6467 = ct[64:67]; b67 = ct[67] ^ ord('}')
for combo in itertools.product(W, repeat=3):
    x5 = bytes(a ^ b for a, b in zip(p6467, combo)) + bytes([b67]) + x5_tail
    x1 = dec(dec(dec(dec(x5))))
    if x1[:9] == x1_known and all((x ^ c) in Wset for x, c in zip(x1[9:], ct[9:16])):
        x = x1; pt = b''
        for i in range(5):
            pt += bytes(a ^ b for a, b in zip(ct[16*i:16*i+16], x)); x = E(x)
        flag = pt[:-pt[-1]].decode()
        assert re.match(r'^firebird\{\w{58}\}$', flag)
        print("FLAG:", flag)
        open('flag_oofbleck-firebird_internal_ct.txt', 'w').write(flag)
        break
