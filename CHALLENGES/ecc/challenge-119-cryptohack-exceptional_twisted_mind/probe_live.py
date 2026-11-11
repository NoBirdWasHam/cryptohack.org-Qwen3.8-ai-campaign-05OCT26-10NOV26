#!/usr/bin/env python3
"""Probe live 13417 response behavior with throwaway sessions (fresh key each connect)."""
import json, socket, time

p0 = 115792089237316195423570985008687907853269984665640564039457584007913129639747
modulus = p0 * p0

def probe(x0, tag):
    s = socket.create_connection(("socket.cryptohack.org", 13417), timeout=40)
    f = s.makefile("rwb")
    for _ in range(3):
        f.readline()  # 3-line banner
    f.write(json.dumps({"option": "get_pubkey", "x0": x0}).encode() + b"\n"); f.flush()
    line = f.readline().decode().strip()
    try:
        d = json.loads(line)
        pk = d.get("pubkey", d)
        info = ""
        if isinstance(pk, int):
            info = f"bits={pk.bit_length()} modp_bits={(pk % p0).bit_length()} divp={pk % p0 == 0}"
        print(f"[{tag}] x0={x0 if abs(x0)<10**20 else hex(x0)[:24]+'..'} -> {line[:120]} {info}", flush=True)
    except Exception:
        print(f"[{tag}] RAW: {line[:200]}", flush=True)
    f.close(); s.close()

for tag, x0 in [("small2", 2), ("zero", 0), ("mult_p", p0), ("p_plus2", p0 + 2),
                ("huge", 2**600), ("neg", -5), ("offcurve", 123456789)]:
    try:
        probe(x0, tag)
    except Exception as e:
        print(f"[{tag}] ERROR {e}", flush=True)
    time.sleep(1)
