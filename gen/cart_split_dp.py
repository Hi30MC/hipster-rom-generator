from collections import deque


class SlidingWindowMin:
    def __init__(self):
        # Store (value, original_index) pairs
        self.deque = deque()
        self.left_idx = 0

    def add(self, value: float, idx: int):
        while self.deque and self.deque[-1][0] >= value:
            self.deque.pop()

        self.deque.append((value, idx))

    def remove_left(self):
        if self.deque and self.deque[0][1] == self.left_idx:
            self.deque.popleft()
        self.left_idx += 1

    def get_min(self) -> tuple[float, int]:
        if not self.deque:
            return float("inf"), -1
        return self.deque[0]

    def __repr__(self):
        return f"SlidingWindowMin(deque={self.deque}, left_idx={self.left_idx})"


def cart_split_dp(
    is_wait: list[bool], min_k: int, max_k: int, m: float, b: float
) -> list[int]:
    """
    Parameters:
        is_wait: list of bools indicating whether each item is a wait move
        min_k: minimum items in a cart
        max_k: maximum items in a cart
        m: cost function linear
        b: cost function constant

    Returns: list of cart sizes, or -(size+1) if wait move optimization was used.
    """
    N = len(is_wait)
    if N == 0:
        return []

    is_wait = [False] + is_wait  # make 1-indexed

    # DP[i] = min time with i items total, cart was just split
    DP = [float("inf")] * (N + 1)
    DP[0] = 0
    # A[i] = DP[i] - (m+1)*i
    A = [float("inf")] * (N + 1)
    A[0] = 0
    # T[i] = the value of k that achieves DP[i]
    #      = or -(k+1) if wait move optimization was used
    T = [-1] * (N + 1)

    window = SlidingWindowMin()

    if min_k == 0:
        window.add(A[0], 0)
    prev_min = window.get_min()

    for i in range(1, N + 1):
        # Maintain sliding window for A[i-max_k] to A[i-min_k]
        if i - min_k >= 0:
            window.add(A[i - min_k], i - min_k)
        while window.left_idx < max(0, i - max_k):
            window.remove_left()

        cur_min = window.get_min()
        min_val, min_idx = cur_min
        if min_val != float("inf"):
            # min valid k: DP[i-k] + (m+1)*k + b
            # = (min valid k: A[i-k]) + (m+1)*i + b
            DP[i] = min_val + (m + 1) * i + b
            # k = i - (i-k)
            T[i] = i - min_idx

        if is_wait[i]:
            prev_val, prev_idx = prev_min
            # min valid k: DP[(i-1)-k] + (m+1)*k + b
            # = (min valid k: A[(i-1)-k]) + (m+1)*(i-1) + b
            val2 = prev_val + (m + 1) * (i - 1) + b
            if val2 < DP[i]:
                DP[i] = val2
                # k+1 = i-(i-1-k)
                # negate to indicate wait move
                T[i] = -(i - prev_idx)

        A[i] = DP[i] - (m + 1) * i

        prev_min = cur_min

    if DP[N] == float("inf"):
        return []

    # Backtrack to find cart sizes
    cart_sizes = []
    v = N
    while v > 0:
        k = T[v]
        cart_sizes.append(k)
        if k > 0:
            v -= k
        else:
            v -= -k
    cart_sizes.reverse()
    return cart_sizes
