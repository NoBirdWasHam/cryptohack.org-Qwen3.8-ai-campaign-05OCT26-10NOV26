import os, sys, types
os.environ["FLAG"] = "crypto{oracle_wraps_reveal_the_prime_DGHV_toystore}"
src = open("server_deployed.py", encoding="utf-8").read().replace("2**128 / N / 4", "2**128 // N // 4")
NL = chr(10)
src = src.replace(
    "p = Crypto.Util.number.getPrime(128)",
    "p = Crypto.Util.number.getPrime(128)" + NL
    + "        open('plog.txt','a').write(str(p) + chr(10))" + NL)
ni = types.ModuleType("ni"); ni.interfaces = lambda: []; ni.ifaddresses = lambda i: {}
sys.modules["netifaces"] = ni
sys.argv = ["server.py", "-p", "13338", "-v"]
g = {"__name__": "__main__", "__file__": "server.py"}
exec(compile(src, "server_plog.py", "exec"), g)
