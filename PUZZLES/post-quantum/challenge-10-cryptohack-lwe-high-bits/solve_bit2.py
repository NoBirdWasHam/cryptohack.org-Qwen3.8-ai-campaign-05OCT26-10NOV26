# bit v2: q-1 = 2*r. g is a QR => h = g^x is a QR => L(h^y)=1.
# me = 2^(8e+1+bit) => L(me) = (-1)^(1+bit). L(c2) = (-1)^(1+bit):
#   L(c2) = -1 -> bit 0 ;  L(c2) = +1 -> bit 1.
import re
from Crypto.Util.number import long_to_bytes

q = 117477667918738952579183719876352811442282667176975299658506388983916794266542270944999203435163206062215810775822922421123910464455461286519153688505926472313006014806485076205663018026742480181999336912300022514436004673587192018846621666145334296696433207116469994110066128730623149834083870252895489152123
txt = open("output_1078aca02f2ab796a8c51773f3c332ee.txt").read()
cs = [int(b, 16) for _, b in re.findall(r"c1=0x([0-9a-f]+), c2=0x([0-9a-f]+)", txt)]
print("ciphertexts:", len(cs))
bits = [0 if pow(c2, (q - 1) // 2, q) == q - 1 else 1 for c2 in cs]
val = 0
for b in reversed(bits): val = (val << 1) | b
flag = long_to_bytes(val)
print("FLAG:", flag.decode(errors="replace"))
open("flag_bit.txt", "w").write(flag.decode())
