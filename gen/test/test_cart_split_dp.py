import pytest
from gen.cart_split_dp import cart_split_dp


@pytest.mark.parametrize(
    "is_wait,min_k,max_k,m,b,expected_cart_sizes",
    [
        # Basic wait optimization
        ([False, False, True, False], 1, 3, 0, 1, [-3, 1]),
        # No waits
        ([False, False, False, False, False], 2, 3, 0, 1, [3, 2]),
        # All waits, cart cheap
        ([True, True, True, True], 1, 2, 0, 0.5, [-2, -2]),
        # Linear cost function
        ([False, False, False, True, False, False], 1, 4, 0.5, 2, [-4, 2]),
        # Empty input
        ([], 1, 3, 0, 1, []),
        # Single item
        ([False], 1, 2, 0, 1, [1]),
        # Single wait, 0-size cart allowed
        ([True], 0, 2, 0, 1, [-1]),
        # Single wait, 0-size cart not allowed
        ([True], 1, 2, 0, 1, [1]),
        # Alternating pattern
        ([False, True, False, True, False], 1, 3, 0, 1, [-2, -2, 1]),
        # Must split
        ([False] * 10, 3, 5, 0, 1, [5, 5]),
        # Could split, but not because of min_k
        ([False, False, False, True, False, False], 3, 4, 0, 1, [3, 3]),
        # Forced carts with 2 items
        ([False, False, False, False], 2, 2, 0, 1, [2, 2]),
        # Forced carts with 2 items with a wait optimization
        ([False, False, True, False, False], 2, 2, 0, 1, [-3, 2]),
        # Impossible
        ([False, False, False, False, False], 2, 2, 0, 1, []),
    ],
)
def test_cart_split_dp(is_wait, min_k, max_k, m, b, expected_cart_sizes):
    result = cart_split_dp(is_wait, min_k, max_k, m, b)
    assert result == expected_cart_sizes

    if not expected_cart_sizes:
        return
    assert sum(map(abs, expected_cart_sizes)) == len(is_wait)
    for cart_size in result:
        cart_size = cart_size if cart_size > 0 else -cart_size - 1
        assert min_k <= cart_size <= max_k
