# build kernel lattice (Z-basis of {x in Z^50 : A x = 0 mod 256}) + particular solution
default(parisize,"512M");
A = read("Arows.gp");  A = Mat(A);
K = matkerMod(A, 256);
h = read("hvec.gp");
xp = matsolveMod(A, h, 256);
print("kerdim ", matsize(K)[2]);
write("K.gp.out", K);
write("xp.gp.out", xp);
d = mathnf(Mat(concat(K~, 0*Mat([1]))~));  \ dummy not used
