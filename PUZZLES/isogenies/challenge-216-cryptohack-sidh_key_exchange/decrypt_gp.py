#!/usr/bin/env python3
# Run gpsidh.gp, parse j in w-basis + alpha/beta, convert to i-basis, decrypt flag.
import subprocess, re, sys
from Crypto.Cipher import AES
from Crypto.Hash import SHA256
from Crypto.Util.Padding import unpad

p = 2**110 * 3**67 - 1
IV = bytes.fromhex("05a4cfbce59acb952128af83c9694390")
CT = bytes.fromhex("755b72b2e3bef2e7a4b2ce4a370f287ad04c1359bace25f3def8be23c0c49e89b4302408ad2dcb02d4875fe58c543d91")

out = open("gpsidh.out").read()
if "JW " not in out:
    print("need fresh gp run"); sys.exit(1)
mw = re.search(r"JW\s+(\d+)\*w \+ (\d+)", out)
ma = re.search(r"ALPHA\s+(\d+)", out)
mb = re.search(r"BETA\s+(\d+)", out)
v, u = int(mw.group(1)), int(mw.group(2))
alpha, beta = int(ma.group(1)), int(mb.group(1))
binv = pow(beta, p-2, p)
jimag = v * binv % p
jreal = (u - v * alpha % p * binv) % p
# verify: (jreal + jimag*i) should equal u + v*w under i = alpha+beta*w
print("jreal:", jreal)
print("jimag:", jimag)
variants = {
    "sage-str": f"{jimag}*i + {jreal}",
    "sage-str-rev": f"{jreal}*i + {jimag}",
    "real": str(jreal),
    "imag": str(jimag),
}
for desc, ss in variants.items():
    key = SHA256.new(data=ss.encode()).digest()
    try:
        pt = unpad(AES.new(key, AES.MODE_CBC, IV).decrypt(CT), 16)
    except Exception as e:
        print(desc, "-> no (pad)", str(e)[:40]); continue
    print(desc, "->", pt[:60])
    if b"crypto" in pt:
        open("flag.txt", "wb").write(pt)
        print("FLAG:", pt.decode())
        break
