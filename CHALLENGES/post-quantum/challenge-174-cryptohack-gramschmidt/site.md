# Gram Schmidt (`gramschmidt`)

- **Points:** 30
- **Category:** post-quantum
- **Status:** SOLVED (live-verified 2026-10-13 via user API)
- **Solved:** 2026-10-12
- **URL:** https://cryptohack.org/challenges/post-quantum/gramschmidt/

## Statement (from challenge_meta.json)
--> In the last challenge we saw that there is a special kind of basis called an orthogonal basis. Given a basis $v_{1}, v_{2}, \ldots, v_{n} \in V$ for a vector space, the Gram-Schmidt algorithm calculates an orthogonal basis $u_{1}, u_{2}, \ldots, u_{n} \in V$. In "An Introduction to Mathematical Cryptography", Jeffrey Hoffstein, Jill Pipher, Joseph H. Silverman , the Gram-Schmidt algorithm is given as: Algorithm for Gram-Schmidt $u_{1} = v_{1}$ Loop $i = 2,3\ldots,n$ &nbsp;&nbsp; Compute $\mu_{ij} = v_{i} \cdot u_{j} / ||u_{j}||^2, 1 \leq j &nbsp;&nbsp; Set $u_{i} = v_{i} - \mu_{ij} \cdot u_{j}$ (Sum over $j$ for $1 \leq j End Loop To test your code, let's grab the flag. Given the following basis vectors: $v_{1} = (4,1,3,-1), \;\; v_{2} = (2,1,-3,4), \;\; v_{3} = (1,0,-2,7), \;\; v_{4} = (6, 2, 9, -5)$. use the Gram-Schmidt algorithm to calculate an orthogonal basis. The flag is the float value of the second component of $u_{4}$ to 5 significant figures. Note that this algorithm doesn't create an ortho normal basis! It's a small change to implement this. Think about what you would have to change. If you're using someone else's algorithm and the flag is incorrect, this might be the issue. If everything seems good and you're still not having your answer accepted, check your rounding when you take 5.s.f. for the solution. -->
