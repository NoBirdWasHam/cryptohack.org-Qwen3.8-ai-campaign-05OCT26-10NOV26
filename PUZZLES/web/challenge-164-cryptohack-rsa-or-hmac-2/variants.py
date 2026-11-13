import json, base64, hashlib, hmac, urllib.request
BASE = "https://web.cryptohack.org/rsa-or-hmac-2"
def get(url):
    with urllib.request.urlopen(url, timeout=30) as r: return r.read()
def b64u(b): return base64.urlsafe_b64encode(b).rstrip(b"=")

pem = open("pubkey_recovered.pem", "rb").read()
# extract DER back (between armor lines)
b64text = pem.split(b"-----", 3)[2]
der = base64.b64decode(b64text.replace(b"\n", b"").replace(b"\r", b""))
# SPKI: SEQUENCE{ SEQUENCE{ rsaEncryption OID, NULL }, BITSTRING der }
def der_len(L):
    if L < 0x80: return bytes([L])
    lb = L.to_bytes((L.bit_length()+7)//8, "big")
    return bytes([0x80 | len(lb)]) + lb
algid = b"\x30" + der_len(13) + bytes.fromhex("06092a864886f70d010101") + b"\x05\x00"
bits = b"\x03" + der_len(len(der)+1) + b"\x00" + der
spki_body = algid + bits
spki = b"\x30" + der_len(len(spki_body)) + spki_body

def armor(label, data, nl=b"\n", trailing=True, width=64):
    b64 = base64.b64encode(data)
    lines = [b64[i:i+width] for i in range(0, len(b64), width)]
    body = nl.join(lines)
    out = b"-----BEGIN " + label + b"-----" + nl + body + nl + b"-----END " + label + b"-----"
    if trailing: out += nl
    return out

variants = {}
variants["trad_lf_nl"]   = armor(b"RSA PUBLIC KEY", der)
variants["trad_lf_nonl"] = armor(b"RSA PUBLIC KEY", der, trailing=False)
variants["trad_crlf_nl"] = armor(b"RSA PUBLIC KEY", der, nl=b"\r\n")
variants["trad_crlf_nonl"] = armor(b"RSA PUBLIC KEY", der, nl=b"\r\n", trailing=False)
variants["spki_lf_nl"]   = armor(b"PUBLIC KEY", spki)
variants["spki_lf_nonl"] = armor(b"PUBLIC KEY", spki, trailing=False)
variants["spki_crlf_nl"] = armor(b"PUBLIC KEY", spki, nl=b"\r\n")
variants["raw_der"]      = der
variants["trad_oneline"] = armor(b"RSA PUBLIC KEY", der, nl=b"")

def forge(payload, secret):
    h = b64u(json.dumps({"typ":"JWT","alg":"HS256"}, separators=(",",":")).encode())
    p = b64u(json.dumps(payload, separators=(",",":")).encode())
    si = h + b"." + p
    return (si + b"." + b64u(hmac.new(secret, si, hashlib.sha256).digest())).decode()

payload = {"username":"admin","admin":True}
for name, sec in variants.items():
    tok = forge(payload, sec)
    try:
        resp = get(f"{BASE}/authorise/{tok}/").decode()
    except Exception as e:
        resp = str(e)
    print(f"{name:16s} -> {resp[:120]}", flush=True)
    if "flag" in resp:
        open("flag_response.json","w").write(resp)
        print("FLAG:", resp)
        break
