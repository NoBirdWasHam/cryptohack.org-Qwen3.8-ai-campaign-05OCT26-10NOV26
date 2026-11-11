v=[1,2,3,4,5];
w = v[Vecsmall([1,3,5])]; print(w);
u = vector(#v\2+1, i, if(2*i-1<=#v, v[2*i-1], 0)); print(u);
