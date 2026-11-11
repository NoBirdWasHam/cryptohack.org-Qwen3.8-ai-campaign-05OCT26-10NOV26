import os, hashlib, random, sys
sys.path.insert(0, ".")
import solve

FLAG = b"crypto{test_flag_local_1234567890abcdefgh}"

def _and(a,b): return bytes([x&y for x,y in zip(a,b)])
def _xor(a,b): return bytes([x^y for x,y in zip(a,b)])
def shuffle(ma, mx): return bytes([mx[i%len(mx)] for i in ma])

class MockSrv:
    def mix(self, data_hex):
        data = bytes.fromhex(data_hex)
        if len(data) < len(FLAG): data += os.urandom(len(FLAG)-len(data))
        ma = _and(FLAG, data)
        mx = _xor(_xor(FLAG, data), os.urandom(len(FLAG)))
        return hashlib.sha256(shuffle(ma, mx)).hexdigest()

if __name__ == "__main__":
    solve.Srv = MockSrv
    solve.main()
    got = open("flag_mixed_up.txt").read().encode()
    print("MATCH" if got == FLAG else f"MISMATCH: {got!r} vs {FLAG!r}")
