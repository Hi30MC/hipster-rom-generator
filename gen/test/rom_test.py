import pytest

NORMAL_MOVE = 1
WAIT_MOVE = 2


def gen_ss_list(moves_between_waits: list[int], min_len: int):
    ss_list = []
    for i in moves_between_waits:
        ss_list += [NORMAL_MOVE] * i
        ss_list.append(WAIT_MOVE)
    ss_list.pop()
    return ss_list


@pytest.mark.parametrize(
    "moves_between_waits, min_len, expected",
    [
        [
            [21, 4, 0, 4, 0, 3, 1, 6, 5],
            10,
            [
                10,
            ],
        ],
        [[4, 8, 16, 2, 17, 1, 30, 10], 27, []],
    ],
)
def test_partition_rom_27_optimized(
    moves_between_waits: list[int], min_len: int, expected: list[list[int]]
):
    ss_list = gen_ss_list(moves_between_waits, min_len)
    assert 0
