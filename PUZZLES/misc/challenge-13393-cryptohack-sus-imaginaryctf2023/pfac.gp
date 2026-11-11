default(parisize,"512M");
n = read("nval.gp");
print("trialdiv/PM phase:");
f = factor(n);  \ pari: PM then ECM limited; prints progress
print(f);
