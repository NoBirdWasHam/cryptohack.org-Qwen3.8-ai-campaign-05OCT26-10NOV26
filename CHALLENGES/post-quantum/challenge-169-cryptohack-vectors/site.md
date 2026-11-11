# Vectors (`vectors`)

- **Points:** 10
- **Category:** post-quantum
- **Status:** SOLVED (live-verified 2026-10-13 via user API)
- **Solved:** 2026-10-12
- **URL:** https://cryptohack.org/challenges/post-quantum/vectors/

## Statement (from challenge_meta.json)
--> Before defining a lattice or talking about how lattices appear in cryptography, let's review some of the basics of linear algebra. The following challenges should be considered as revision, if this is totally new to you, you might need to do a bit of background reading. As usual, we recommend "An Introduction to Mathematical Cryptography" by Hoffstein, Pipher, Silverman, as well as this introduction to lattices and their applications. A vector space $V$ over a field $F$ is a set defined with two binary operators. For a vector $v \in V$, and a scalar $a \in F$, vector addition takes two vectors and produces another vector: $v + w = z,$ for $v, w, z \in V$ and scalar multiplication takes a vector and a scalar and produces a vector: $a \cdot v = w,$ for $v, w \in V, a \in F$. You will probably have first seen vectors in the context of a two dimensional vector space defined over the reals. We'll use this here too as an example! Let's consider a two dimensional vector space over the reals. A vector $v \in V$ can be considered as a pair of numbers: $v = (a,b)$ for $a,b \in R$. Vector addition works as $v + w = (a,b) + (c,d) = (a+c, b+d)$, and scalar multiplication by $c \cdot v = c \cdot (a,b) = (c \cdot a, c \cdot b)$. One can also define the inner product (also called the dot product ), which takes two vectors and returns a scalar. Formally we think of this as $v \cdot w = a$ for $v,w \in V, a \in F$. In our two-dimensional example, the inner product works as $v \cdot w = (a,b) \cdot (c,d) = a \cdot c + b \cdot d$. Time for the flag! Given a three dimensional vector space defined over the reals, where $v = (2,6,3)$, $w = (1,0,0)$ and $u = (7,7,2)$, calculate $3 \cdot (2 \cdot v - w) \cdot 2 \cdot u$. -->
