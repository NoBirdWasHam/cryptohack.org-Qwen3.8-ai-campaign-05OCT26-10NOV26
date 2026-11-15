import sys, os, json
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from hashlib import sha512
from Crypto.Util.number import bytes_to_long
from params import p, q, g

def RO(a0,a1,e,e0,e1,z0,z1):
    H = sha512(b'my')
    H.update(str(a0).encode()); H.update(b'very')
    H.update(str(a1).encode()); H.update(b'cool')
    H.update(str(e).encode());   H.update(b'random')
    H.update(str(e0).encode());  H.update(b'oracle')
    H.update(str(e1).encode());  H.update(b'for')
    H.update(str(z0).encode());  H.update(b'fischlin')
    H.update(str(z1).encode())
    return bytes_to_long(H.digest())

BOUND = 2**(512-6)

def replay_b0(proof, w0):
    """Assume b=0 (side 0 real, witness w0). Reconstruct prover path.
    Returns (hit_found, first_hit_e, final_ok). hit_found => hypothesis b=0 contradicted => b=1."""
    a0,a1,e,e0,e1,z0,z1 = (proof["a0"],proof["a1"],proof["e"],
                           proof["e0"],proof["e1"],proof["z0"],proof["z1"])
    e_sim = e1                      # b=0 => side1 simulated => e1 = e_sim
    r_b   = (z0 - e0*w0) % q        # b=0 => z0 = r_b + e0*w0
    hit = None; final_ok = False
    for ee in range(e+1):
        e0p = ee ^ e_sim
        z0p = (r_b + e0p*w0) % q
        small = RO(a0,a1,ee,e0p,e1,z0p,z1) < BOUND
        if ee == e:
            final_ok = small
        elif small and hit is None:
            hit = ee
    return hit, final_ok
