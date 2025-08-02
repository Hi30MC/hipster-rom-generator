from collections import deque

from nbtlib import File, tag

from gen.encode import encode_rom1, encode_rom27, encode_rom729
from gen.schem_types import Minecart, Schematic
from .params import Rom1, Rom27, Rom729, RomParams, Sequence


def gen_rom(sequence: Sequence, params: RomParams) -> File:
    if isinstance(params, Rom1):
        return gen_rom1(sequence, params)
    elif isinstance(params, Rom27):
        return gen_rom27(sequence, params)
    elif isinstance(params, Rom729):
        return gen_rom729(sequence, params)
    raise NotImplementedError


def carts_schem(carts: list[Minecart]) -> File:
    out = File(Schematic.empty(), gzipped=True)
    out.update({"Entities": tag.List(carts)})
    return out


def gen_rom1(sequence: Sequence, params: Rom1) -> File:
    ss_list = sequence.with_min_items(params.min_carts)
    carts = encode_rom1(
        ss_list, cart_pos=params.cart_pos, add_stop_move=params.add_stop_move
    )
    return carts_schem(carts)


# TODO: everything below here is yet untested


def gen_rom27(sequence: Sequence, params: Rom27) -> File:
    ss_list = sequence.with_min_items(params.min_items())
    if params.cut_wait_moves:
        partitions = partition_rom27_optimized(ss_list, sequence.wait_move)
    else:
        partitions = partition_rom27(ss_list, params)

    carts = encode_rom27(partitions, cart_pos=params.cart_pos, medium=params.medium)
    return carts_schem(carts)


def gen_rom729(sequence: Sequence, params: Rom729) -> File:
    moves = partition_rom729(sequence, params)
    carts = encode_rom729(moves, cart_pos=params.cart_pos)
    return carts_schem(carts)


def partition_rom27(ss_list: list[int], params: Rom27) -> list[list[int]]:
    queue = deque(ss_list)
    result = []
    min_items = params.min_items()

    while queue:
        if not result or len(result[-1]) == 27 or len(queue) <= min_items:
            result.append([])
            min_items -= params.min_items_per_cart
        else:
            result[-1].append(queue.popleft())
    return result


def split_list[T](inp: list[T], split_on: T) -> list[list[T]]:
    if not inp:
        return []

    result = [[]]

    for item in inp:
        if item == split_on:
            result.append([])
        else:
            result[-1].append(item)

    return result


def partition_rom27_optimized(
    ss_list: list[int],
    wait_move: int | None,
    max_cart_len: int = 27,
    min_items_per_cart: int = 3,
) -> list[list[int]]:
    if wait_move is None:
        raise ValueError("Wait move must be supplied for optimized rom")

    # assumes you have enough moves to fill min cart count
    assert ss_list[-1] != wait_move, "Last move cannot be a wait move"

    result = []
    segments = deque(split_list(ss_list, wait_move))
    queue = segments.popleft()

    # TODO: this can probably be optimized more

    while segments or queue:
        if len(queue) < max_cart_len:
            # entire queue can fit into one cart

            # pack as many extra wait moves as we can
            while len(queue) < max_cart_len and segments and segments[0] == []:
                queue.append(wait_move)
                segments.popleft()

            if len(queue) > min_items_per_cart:
                result.append(queue)
            else:
                # need to add more items
                queue.append(wait_move)
                queue += segments.popleft()
        elif len(queue) < max_cart_len + min_items_per_cart:
            # in the case(s) that subtracting 27 wouldn't leave enough items in next cart to cover minimum
            split_pos = len(queue) // 2
            result.append(queue[:split_pos])
            queue = queue[split_pos:]
        else:
            # safe to pop 27 from queue
            result.append(queue[:max_cart_len])
            queue = queue[max_cart_len:]
        if not queue and segments:
            if not segments[0]:
                queue.append(wait_move)
            queue += segments.popleft()

    return result


def partition_rom729(sequence: Sequence, params: Rom729) -> list[list[list[int]]]:
    """
    This code works in 95% of use cases, but fails with min_items_per_cart < 27 and less than full minimum carts (min carts * 729)
    due to crappy spaghetti logic used below. I will be reworking this algo to be less shit, but don't expect it to be in the final
    version any time soon. It works for literally everything else, so deal with it. Have you just tried making your sequence longer?
    """

    min_remaining_items = (
        params.min_carts * params.min_shulkers_per_cart * params.min_discs_per_shulker
    )
    min_remaining_shulkers = params.min_carts * params.min_shulkers_per_cart

    queue = deque(sequence.with_min_items(min_remaining_items))
    carts: list[list[list[int]]] = [[[]]]
    min_remaining_items -= params.min_discs_per_shulker
    min_remaining_shulkers -= params.min_shulkers_per_cart

    while queue:
        if (
            len(carts[-1][-1]) < 27
            and len(queue) > min_remaining_items
            and len(queue) / params.min_discs_per_shulker >= min_remaining_shulkers
        ):
            carts[-1][-1].append(queue.popleft())
        else:
            # new box
            if (
                len(carts[-1]) == 27
                or len(queue) // params.min_discs_per_shulker <= min_remaining_shulkers
            ):
                # new cart
                carts.append([])
                min_remaining_shulkers -= params.min_shulkers_per_cart
            carts[-1].append([])
            min_remaining_items -= params.min_discs_per_shulker

    return carts
