# a_spot_super: find the supersingular curve among 100 Montgomery curves y^2=x^3+A x^2+x over p=2^127-1
# Supersingular iff #E(F_p) = p+1 (Frobenius trace a = 0). PARI Schoof (ellcard) is the robust test.
import re, subprocess
src = open('curves_1e476e7d608576c05a13b269d1481602.sage').read()
As = [int(x) for x in re.search(r'A_coefficients = \[(.*?)\]', src, re.S).group(1).split(',')]
lines = ["default(parisizemax, 1<<30);", "p=2^127-1;"]
for i, A in enumerate(As):
    # PARI if() is a 3-arg function: if(cond, then, else)
    lines.append('E=ellinit(Mod([0, %d, 0, 1, 0], p)); if(ellcard(E)==p+1, print("SUPER idx=%d A=%d"), 0);' % (A, i, A))
open('ss_check.gp','w').write("\n".join(lines))
r = subprocess.run(['~/tools/gp64.exe','-f','-q','ss_check.gp'], capture_output=True, text=True)
print(r.stdout)
