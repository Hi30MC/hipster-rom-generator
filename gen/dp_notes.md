# DP Formulations for Cart Optimization

**Definitions:**

- `is_wait[i]`: boolean array of size N where `is_wait[i]` is true if the i-th move is a wait.
  One-indexed, e.g. is_wait[1] = first in sequence, to make DP work
- `valid k`: cart size constraints `min_size ≤ k ≤ max_size`

## Always working but inefficient

`DP[c, j, i]` = min time with c carts, j items in last cart, i items total

```
DP[c, j, i] = min(
    if j > 0:
        DP[c, j-1, i-1] + 1                    # add a disc
      min valid k: DP[c-1, k, i] + 1           # split cart on normal
    if is_wait[i]:
        min valid k: DP[c-1, k, i-1] + 1       # split cart, save a wait
)
DP[0, 0, 0] = 0
DP[0, j, i], j!=i = inf

ans = min DP[*, valid k, N]
```

**Runtime:** `O(N² * cart_size² / min_cart_size)`

The runtime comes from: `O(N/min_cart_size)` possible cart counts × `cart_size` choices for i × `N` items × `cart_size` choices for k.

## Ignore cart count

**Observation:** The number of carts doesn't affect optimality

`DP[j, i]` = min time with j items in last cart, i items total

```
DP[j, i] = min(
    if j > 0:
        DP[j-1, i-1] + 1
    min valid k: DP[k, i] + 1
    if is_wait[i]:
        min valid k: DP[k, i-1] + 1
)
DP[0, 0] = 0
DP[j, 0], j!=0 = inf
invalid indices are inf

ans = DP[valid k, N]
```

**Runtime:** `O(cart_size * N)`
Hmm, we only compute the range minimums when j=0; and all other values are trivially computed from j=0 values...

## One-dimensional optimization

**Observation:** `DP[k, i] = DP[0, i-k] + k`
This means we only need to store `DP[0, i]` values.

`DP[i]` = min time with i items total, cart was just split

```
DP[i] = min(
    min valid k: DP[i-k] + k + 1
    if is_wait[i]:
        min valid k: DP[i-k-1] + k + 1
)
DP[0] = 0

ans = DP[N] (includes last cart split)
```

**Runtime:** `O(cart_size * N)`

## Sliding window optimization

To make the range minimum O(1), add an auxiliary array:

Let `A[i] = DP[i] - i`. Then:

```
DP[i] = A[i] + i
DP[i-k] + k = A[i-k] + (i-k) + k = A[i-k] + i

min valid k: DP[i-k] + k + 1 = (min valid k: A[i-k]) + i + 1
min valid k: DP[(i-1)-k] + k + 1 = (min valid k: A[(i-1)-k]) + i -1+1
```

Fill in A as we fill in DP.
All range queries are now sliding window queries on A!
**Runtime:** `O(N)`

## Linear cost function extension

Let split cost be `f(k) = m*k + b` instead of constant 1.

```
DP[i] = min(
    min valid k: DP[i-k] + (m+1)*k + b
    if is_wait[i]:
        min valid k: DP[i-k-1] + (m+1)*k + b
)

DP[0] = 0
ans = DP[N]
```

The coefficient of k changes from 1 to (m+1), but the structure remains the same.

Let `A[i] = DP[i] - (m+1)*i`. Then:

```
DP[i] = A[i] + (m+1)*i
DP[i-k] + (m+1)*k
  = A[i-k] + (m+1)*(i-k) + (m+1)*k
  = A[i-k] + (m+1)*i
DP[(i-1)-k] + (m+1)*k
  = A[(i-1)-k] + (m+1)*(i-1-k) + (m+1)*k
  = A[(i-1)-k] + (m+1)*(i-1)

min valid k: DP[i-k] + (m+1)*k + b
= (min valid k: A[i-k]) + (m+1)*i + b
min valid k: DP[(i-1)-k] + (m+1)*k + b
= (min valid k: A[(i-1)-k]) + (m+1)*(i-1) + b
```

**Runtime:** `O(N)`

# Tracking splits are made

Let T[i] = the value of k that minimizes DP[i] in the recurrence.
Sliding window minimum now also needs to track index of the minimum value.

Recover cart sizes by iterating backwards starting at v=N;
`v -= T[v]` or `v -= T[v] + 1`, depending on is_wait[v].
