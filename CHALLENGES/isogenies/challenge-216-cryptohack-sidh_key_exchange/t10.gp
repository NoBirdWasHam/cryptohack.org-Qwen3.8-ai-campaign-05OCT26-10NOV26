f2 = ffinit(11, 2, 'x);
w = ffgen(f2, 'w);
z = 3*w + 5;
print(type(lift(z)));
print(type(lift(lift(z))));
print(lift(lift(z)));
print(polcoeff(lift(lift(z)), 1));
