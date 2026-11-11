import sys, os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from hamiltonicity import comm_params
from Crypto.Util.number import isPrime, inverse
P,q,h1,h2 = comm_params
print("P prime:", isPrime(P))
print("q prime:", isPrime(q))
print("P == 2q+1:", P == 2*q+1)
print("P-1 == 2q:", P-1 == 2*q)
print("h1 % P == 1:", h1 % P == 1)
print("h2 % P == 1:", h2 % P == 1)
print("h1^q == 1:", pow(h1,q,P) == 1)
print("h2^q == 1:", pow(h2,q,P) == 1)
print("h1 order divides 2:", pow(h1,2,P)==1)
print("h1 == h2:", h1==h2)
print("h1*h2 inv == 1 (dlog 0?):", (h1*inverse(h2,P))%P == 1)
# is h1 a QR? (order-q subgroup = QRs for safe prime)
print("h1 QR:", pow(h1,(P-1)//2,P)==1)
print("h2 QR:", pow(h2,(P-1)//2,P)==1)
# small-order check: does h1 have order exactly q? check h1^(q/r) != 1 for small factors r of q
print("q bitlen:", q.bit_length())
