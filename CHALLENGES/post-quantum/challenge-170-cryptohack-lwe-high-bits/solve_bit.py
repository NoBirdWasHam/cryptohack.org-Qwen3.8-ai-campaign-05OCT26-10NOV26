# bit: ElGamal per-bit where me = 2^(8e+1+bit). q-1 = 4*r, g is QR (g^((q-1)/4) = -1),
# J = 2^((q-1)/4) has order 4. Map everything to the 2-Sylow {1,J,J^2,J^3}:
#   c1^m = (-1)^y, h^m = (-1)^x, c2^m = J^k * (-1)^{xy},  m=(q-1)/4
# => J^k = c2^m * (-1)^{xy};  k mod 4 = 1 -> bit 0 ; = 2 -> bit 1.
import re
from Crypto.Util.number import long_to_bytes

q = 117477667918738952579183719876352811442282667176975299658506388983916794266542270944999203435163206062215810775822922421123910464455461286519153688505926472313006014806485076205663018026742480181999336912300022514436004673587192018846621666145334296696433207116469994110066128730623149834083870252895489152123
g = 104831378861792918406603185872102963672377675787070244288476520132867186367073243128721932355048896327567834691503031058630891431160772435946803430038048387919820523845278192892527138537973452950296897433212693740878617106403233353998322359462259883977147097970627584785653515124418036488904398507208057206926
m = (q - 1) // 4
J = pow(2, m, q)
assert pow(J, 2, q) == q - 1  # J order 4

txt = open("output_1078aca02f2ab796a8c51773f3c332ee.txt").read()
pubs = [int(x, 16) for x in re.findall(r"public_key=0x([0-9a-f]+)", txt)]
cs = [(int(a, 16), int(b, 16)) for a, b in re.findall(r"c1=0x([0-9a-f]+), c2=0x([0-9a-f]+)", txt)]
print("pairs:", len(pubs), len(cs))

bits = []
for h, (c1, c2) in zip(pubs, cs):
    px = 1 if pow(h, m, q) == q - 1 else 0     # x odd?
    py = 1 if pow(c1, m, q) == q - 1 else 0    # y odd?
    v = pow(c2, m, q)
    if px and py: v = v * (q - 1) % q          # divide out (-1)^{xy}
    # v = J^k ; find k mod 4
    kmod = None
    acc = 1
    for i in range(4):
        if acc == v: kmod = i; break
        acc = acc * J % q
    assert kmod is not None, "v not in <J>"
    assert kmod in (1, 2), f"unexpected k mod 4 = {kmod}"
    bits.append(0 if kmod == 1 else 1)

val = 0
for b in reversed(bits): val = (val << 1) | b
flag = long_to_bytes(val)
print("FLAG:", flag.decode(errors="replace"))
open("flag_bit.txt", "w").write(flag.decode())
