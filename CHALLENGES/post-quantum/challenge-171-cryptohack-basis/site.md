# Size and Basis (`basis`)

- **Points:** 15
- **Category:** post-quantum
- **Status:** SOLVED (live-verified 2026-10-13 via user API)
- **Solved:** 2026-10-12
- **URL:** https://cryptohack.org/challenges/post-quantum/basis/

## Statement (from challenge_meta.json)
--> We say a set of vectors $v_{1}, v_{2}, \ldots, v_{k} \in V$ are linearly independent if the only solution to the equation: $a_{1} \cdot v_{1} + a_{2} \cdot v_{2} + \ldots + a_{k} \cdot v_{k} = 0$ is for $a_{1} = a_{2} = \ldots = a_{k} = 0$. To visualise this, think of a vector directed out of a point. Given a set of linearly independent vectors, the only way to return back to the original point is by moving along the original vector. No combination of any of the other vectors will get you there. A basis is a set of linearly independent vectors $v_{1}, v_{2}, \ldots, v_{n} \in V$ such that any vector $w \in V$ can be written as: $w = a_{1} \cdot v_{1} + a_{2} \cdot v_{2} + \ldots + a_{k} \cdot v_{n}$ The number of elements in the basis is also the dimension of the vector space. We define the size of a vector, denoted $||v||$, using the inner product of the vector with itself: $||v||^{2} = v \cdot v$. A basis is orthogonal if for a vector basis $v_{1}, v_{2}, \ldots, v_{n} \in V$, the inner product between any two different vectors is zero: $v_{i} \cdot v_{j} = 0, i \neq j$. A basis is orthonormal if it is orthogonal and $||v_{i}|| = 1$, for all $i$. That's a lot of stuff, but we'll be needing it. Time for the flag. Given the vector $v = (4, 6, 2, 5)$, calculate its size. -->
