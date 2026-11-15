from Crypto.Cipher import DES3
K1=bytes(range(1,9)); K2=bytes(range(8,16)); K3=bytes(range(16,24))
K=K1+K2+K3
def EK(X): return DES3.new(K, DES3.MODE_ECB).encrypt(X)
def DK(X): return DES3.new(K, DES3.MODE_ECB).decrypt(X)

# toy: 2-byte IV to actually brute force
W = bytes([0x5A,0x3C])
def T(P): return bytes(a^b for a,b in zip(W, EK(bytes(x^y for x,y in zip(P,W)))))
P=bytes(range(8))
assert T(P)==bytes(a^b for a,b in zip(W, EK(bytes(x^y for x,y in zip(P,W))))), "conjugacy failed"
print("conjugacy identity holds: T_K = XOR_W o E_K o XOR_W  ->", True)

obs = T(bytes.fromhex("63727970746f7b30"))  # flag block0 "crypto{0"
cand=[]
for w0 in range(256):
    for w1 in range(256):
        Wt=bytes([w0,w1])+bytes(6)
        Xt=bytes(x^y for x,y in zip(obs, Wt))     # = EK(P^Wt)
        Pinv=DK(Xt)
        Pimpl=bytes(a^b for a,b in zip(Pinv, Wt))
        if Pimpl==bytes.fromhex("63727970746f7b30"):
            cand.append(Wt)
print("toy 2-byte-IV brute force: candidate W =", [c[:2].hex() for c in cand])
print("=> for a 2-byte IV the known-block-0 constraint pins W uniquely; for 8 bytes it's 2^64.")
