#!/usr/bin/env python3
"""oh_snap probe: extract RC4 keystreams for controlled nonces, look for structure.
  send_cmd(ct, nonce): cipher=ARC4.new(nonce+FLAG); cmd=cipher.decrypt(ct); error echoes cmd.hex()
  => ct=0x00*m  =>  echoed cmd = RC4 keystream for key (nonce||FLAG), first m bytes.
We control nonce. FLAG is the secret suffix. Look for a peelable structure."""
import urllib.request, json

def ks(nonce_hex, m=64):
    ct = "00"*m
    r = urllib.request.Request("https://aes.cryptohack.org/oh_snap/send_cmd/%s/%s/" % (ct, nonce_hex),
                               headers={"User-Agent":"practice-run/1.0"})
    d = json.loads(urllib.request.urlopen(r, timeout=30).read().decode())
    if "error" in d and d["error"].startswith("Unknown command:"):
        return bytes.fromhex(d["error"].split(":")[1].strip())
    return None

data = {}
# vary nonce length (all zeros)
for L in [1,2,4,8,16,24,32,48,64,128,200,250,300,400]:
    data["z%03d"%L] = ks("00"*L, 48)
    print("nonce 0x00*%-3d -> ks[0:16]=%s" % (L, data["z%03d"%L][:16].hex()), flush=True)

# fixed length 16, vary the LAST nonce byte
base = "00"*15
print("\n-- vary last byte of 16-byte nonce --")
for b in [0,1,2,3,0xff]:
    nonce = base + ("%02x"%b)
    k = ks(nonce, 48)
    print("last=0x%02x ks[0:16]=%s" % (b, k[:16].hex()), flush=True)
    data["16L_b%02x"%b] = k

# fixed length 16, vary FIRST byte
print("\n-- vary first byte of 16-byte nonce --")
tail = "00"*15
for b in [0,1,2,3]:
    nonce = ("%02x"%b) + tail
    k = ks(nonce, 48)
    print("first=0x%02x ks[0:16]=%s" % (b, k[:16].hex()), flush=True)
    data["16F_b%02x"%b] = k

import json as J
open("probe_ks.json","w").write(J.dumps({k:v.hex() for k,v in data.items()}))
print("\nsaved probe_ks.json")
