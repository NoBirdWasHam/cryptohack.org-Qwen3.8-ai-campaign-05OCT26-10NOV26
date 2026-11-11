R = read("_R.txt");
forprime(p=2,10000000, if(R%p==0, print("factor ", p); while(R%p==0, R\=p)));
print("remaining digits: ", length(Str(R)));
