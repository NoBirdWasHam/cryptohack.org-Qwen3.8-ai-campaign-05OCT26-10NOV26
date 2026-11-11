#!/usr/bin/env python3
# rsa-or-hmac (160): jwt.decode(token, PUBLIC_KEY, algorithms=['HS256','RS256'])
# -> forge HS256 token with the PUBLIC KEY PEM as the HMAC secret, admin:true -> FLAG.
import base64, hmac, hashlib, json, urllib.request

B = "https://web.cryptohack.org/rsa-or-hmac"
pub = json.load(urllib.request.urlopen(B + "/get_pubkey/", timeout=30))["pubkey"]
if isinstance(pub, str):
    pub = pub.encode()
print("pubkey head:", pub[:40])

def b64u(x): return base64.urlsafe_b64encode(x).rstrip(b"=")
header = b64u(json.dumps({"alg": "HS256", "typ": "JWT"}, separators=(",", ":")).encode())
payload = b64u(json.dumps({"username": "gtf", "admin": True}, separators=(",", ":")).encode())
signing_input = header + b"." + payload
sig = b64u(hmac.new(pub, signing_input, hashlib.sha256).digest())
token = (signing_input + b"." + sig).decode()

r = json.load(urllib.request.urlopen(B + "/authorise/" + token + "/", timeout=30))
print("RESPONSE:", r)
