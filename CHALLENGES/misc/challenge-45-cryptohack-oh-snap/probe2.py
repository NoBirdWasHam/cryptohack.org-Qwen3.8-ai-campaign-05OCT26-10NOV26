#!/usr/bin/env python3
"""oh_snap probes: (1) hidden commands, (2) confirm nonce cap mechanism.
To send cmd=X: nonce=N, keystream KS=RC4(N||FLAG) [get via ct=0], ciphertext=KS^X.
Server computes cmd=ciphertext^KS=X and responds ('Pong!' for ping, else echo / hidden cmd)."""
import urllib.request, json, urllib.error, time

def get_keystream(nonce_hex, m=32):
    ct="00"*m
    url="https://aes.cryptohack.org/oh_snap/send_cmd/%s/%s/"%(ct,nonce_hex)
    r=urllib.request.Request(url, headers={"User-Agent":"p/1.0"})
    d=json.loads(urllib.request.urlopen(r,timeout=30).read().decode())
    if "error" in d and d["error"].startswith("Unknown command:"):
        return bytes.fromhex(d["error"].split(":")[1].strip())
    raise RuntimeError(d)

def send_cmd(cmd_bytes, nonce_hex):
    KS=get_keystream(nonce_hex, max(len(cmd_bytes),4))
    ct=bytes(a^b for a,b in zip(cmd_bytes, KS)).hex()
    url="https://aes.cryptohack.org/oh_snap/send_cmd/%s/%s/"%(ct,nonce_hex)
    r=urllib.request.Request(url, headers={"User-Agent":"p/1.0"})
    try:
        return json.loads(urllib.request.urlopen(r,timeout=30).read().decode())
    except urllib.error.HTTPError as e:
        return {"_http":e.code}

N="0011223344556677"  # 8-byte nonce
print("=== (1) hidden-command probe (nonce=%s) ==="%N)
for cmd in [b"ping",b"flag",b"get_flag",b"getflag",b"help",b"whoami",b"cat flag",b"ls",
            b"read flag",b"flag.txt",b"show",b"print",b"dump",b"key",b"secret",b"admin",
            b"root",b"get",b"get_key",b"get_secret",b"reveal",b"answer",b"solve"]:
    d=send_cmd(cmd,N)
    tag=d.get("msg") or d.get("flag") or d.get("error") or d.get("_http")
    print("  %r -> %s"%(cmd, str(tag)[:80]))
    time.sleep(0.5)

print("\n=== (2) nonce cap mechanism (ct=1 byte vs ct=16 bytes) ===")
def captest(L, m):
    nonce="a1"*L; ct="00"*m
    url="https://aes.cryptohack.org/oh_snap/send_cmd/%s/%s/"%(ct,nonce)
    r=urllib.request.Request(url, headers={"User-Agent":"p/1.0"})
    try:
        d=json.loads(urllib.request.urlopen(r,timeout=30).read().decode())
        return "OK" if ("error" in d and d["error"].startswith("Unknown command:")) else "NORES"
    except urllib.error.HTTPError as e:
        return "HTTP%d"%e.code
for m in [1,16]:
    for L in [218,220,222,223,224]:
        print("  ct=%2dB L=%-4d -> %s"%(m,L,captest(L,m)))
        time.sleep(1)
