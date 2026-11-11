import json, sys, re
sys.path.insert(0, '.')
from aes import AES, Sbox, Rcon
from Crypto.Cipher import AES as FULLAES

no_op = lambda *x: None
D = json.load(open('collect.json'))
def hx(t):
    return bytes.fromhex(re.search(r'[0-9a-f]+', t).group(0))

flag_ct = hx(D['banner'].split('decrypt:')[1]) if False else None
import re
m = re.search(r'decrypt: ([0-9a-f]+)\.', D['banner'])
flag_ct = bytes.fromhex(m.group(1))

def stage_cipher(option, key=b'\x00'*16):
    c = AES(key)
    if option=='ark': c._add_round_key=no_op
    elif option=='sb': c._sub_bytes=no_op
    elif option=='sr': c._shift_rows=no_op
    else: c._mix_columns=no_op
    return c

# ---- stage 1: ark (keyless) -> k0..k3
slice0 = stage_cipher('ark').decrypt(hx(D['ark_sec']))
k = bytearray(16)
for i in range(4):
    b = slice0[4*i:4*i+4]
    assert len(set(b))==1, ('ark slice bad', slice0.hex())
    k[i] = b[0]
print('k0..3:', bytes(k[:4]).hex())

# ---- stage 2: sb affine -> k4..k7
c0 = stage_cipher('sb', b'\x00'*16); c1 = stage_cipher('sb', b'\x11'*16)
E0 = c0.encrypt(b'\x00'*16)
cols = []  # M as list of 128-bit column ints
for i in range(16):
    for bit in range(8):
        e = bytearray(16); e[i] = 1 << bit
        out = bytes(a^b for a,b in zip(c0.encrypt(bytes(e)), E0))
        cols.append(int.from_bytes(out,'big'))
# solve M x = t  (GF2) via row reduction
t = int.from_bytes(bytes(a^b for a,b in zip(hx(D['sb_sec']), hx(D['sb_zero']))), 'big')
# columns of M are images of basis vectors; build augmented system: sum x_j * col_j = t
rows = [(cols[j], 1<<j) for j in range(128)]
piv = {}
for v, xv in rows:
    while v:
        hb = v.bit_length()-1
        if hb in piv:
            v ^= piv[hb][0]; xv ^= piv[hb][1]
        else:
            piv[hb] = (v, xv); break
    else:
        if t and False: pass
xv = 0; vv = t
while vv:
    hb = vv.bit_length()-1
    if hb not in piv: print('M singular!'); sys.exit(1)
    vv ^= piv[hb][0]; xv ^= piv[hb][1]
slice1 = xv.to_bytes(16,'big')
for i in range(4):
    b = slice1[4*i:4*i+4]
    assert len(set(b))==1, ('sb slice bad', slice1.hex())
    k[4+i] = b[0]
print('k4..7:', bytes(k[4:8]).hex())

json.dump({'k8_11_partial': bytes(k[:8]).hex()}, open('partial.json','w'))
print('flag_ct:', flag_ct.hex())
