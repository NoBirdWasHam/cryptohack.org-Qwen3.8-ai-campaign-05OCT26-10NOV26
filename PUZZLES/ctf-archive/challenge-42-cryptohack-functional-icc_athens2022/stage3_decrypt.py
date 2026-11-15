# Stage 3 final: parse jt from bmr.out, AES-ECB decrypt ciphertext from output.txt, show flag.
import json, hashlib, re
from Crypto.Cipher import AES
p = 2**142 - 111
txt = open('output.txt').read()
ct_hex = txt.split('Stage 3:')[1].split('========')[1].strip()
m = re.search(r'jt=(\d+)', open('bmr2.out').read())
assert m, "jt not found in bmr2.out"
jt = int(m.group(1))
assert jt < p
key = hashlib.sha256(str(jt).encode()).digest()
pt = AES.new(key, AES.MODE_ECB).decrypt(bytes.fromhex(ct_hex))
print("PLAINTEXT raw:", pt)
pad = pt[-1]
if 1 <= pad <= 16 and pt[-pad:] == bytes([pad])*pad:
    ptu = pt[:-pad]
    print("PAD OK, UNPADDED:", ptu)
    s = ptu.decode('latin1')
    if s.startswith('CH') or '{' in s or 'flag' in s.lower():
        json.dump({'flag': s}, open('flag.json', 'w'))
        print("FLAG:", s)
