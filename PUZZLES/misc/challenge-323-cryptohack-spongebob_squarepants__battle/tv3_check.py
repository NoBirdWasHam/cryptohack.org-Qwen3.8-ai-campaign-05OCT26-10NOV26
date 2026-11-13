# tv3_check.py — byte-verify walker3's cap2 kernel against the reference python H.
# walker3 mode 9 prints: <32-hex 16-byte message> <cap2 lo64 hex> <cap2 hi16 hex>
# Required equality (little-endian convention, cf. harvest.py AAR lesson):
#   H(msg)[8:16]  == lo.to_bytes(8,'little')   and   H(msg)[16:18] == hi.to_bytes(2,'little')
import subprocess, sys
from spongebob import H

out = subprocess.run([sys.argv[1] if len(sys.argv) > 1 else "./walker3.exe",
                      sys.argv[2] if len(sys.argv) > 2 else "50", "9"],
                     capture_output=True, text=True, cwd=".").stdout
n_ok = 0
for i, ln in enumerate(out.strip().splitlines()):
    mh, clo, chi = ln.split()
    m = bytes.fromhex(mh)
    assert len(m) == 16
    h = H(m)
    lo = int(clo, 16).to_bytes(8, "little"); hi = int(chi, 16).to_bytes(2, "little")
    ok = h[8:16] == lo and h[16:18] == hi
    print(("OK  " if ok else "FAIL"), mh, "-> cap2", (lo + hi).hex(), "python", h[8:].hex())
    n_ok += ok
print("TV3: %d/%d match python H (cap2, little-endian)" % (n_ok, len(out.strip().splitlines())))
sys.exit(0 if n_ok == len(out.strip().splitlines()) else 1)
