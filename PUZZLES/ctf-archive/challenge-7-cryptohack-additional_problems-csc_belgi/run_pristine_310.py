import os, sys, types
os.environ["FLAG"] = "[flag value withheld — real-flag strings live only under FLAGS/]"
src = open("server_deployed.py", encoding="utf-8").read()   # PRISTINE -- float typo intact
NL = chr(10)
src = src.replace(
    "p = Crypto.Util.number.getPrime(128)",
    "p = Crypto.Util.number.getPrime(128)" + NL
    + "        open('plog310.txt','a').write(str(p) + chr(10))" + NL)
sys.path.insert(0, ".")   # for the local netifaces stub
sys.argv = ["server.py", "-p", "13339", "-v"]
g = {"__name__": "__main__", "__file__": "server.py"}
exec(compile(src, "server_pristine310.py", "exec"), g)
