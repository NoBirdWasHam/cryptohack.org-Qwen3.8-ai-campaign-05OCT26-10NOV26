read("params.gp");
D = read("bytes.gp");
print("type D: ", type(D));
for(i=1,2, d = D[i]; print(type(d)));
