from typing import Literal

from .schem_types import Item, Minecart

ss_to_num_stacks = {
    1: 1,
    2: 2,
    3: 4,
    4: 6,
    5: 8,
    6: 10,
    7: 12,
    8: 14,
    9: 16,
    10: 18,
    11: 20,
    12: 22,
    13: 24,
    14: 26,
    15: 27,
}

ss_to_disc = {
    1: "minecraft:music_disc_13",
    2: "minecraft:music_disc_cat",
    3: "minecraft:music_disc_blocks",
    4: "minecraft:music_disc_chirp",
    5: "minecraft:music_disc_far",
    6: "minecraft:music_disc_mall",
    7: "minecraft:music_disc_mellohi",
    8: "minecraft:music_disc_stal",
    9: "minecraft:music_disc_strad",
    10: "minecraft:music_disc_ward",
    11: "minecraft:music_disc_11",
    12: "minecraft:music_disc_wait",
    13: "minecraft:music_disc_pigstep",
    14: "minecraft:music_disc_otherside",
    15: "minecraft:music_disc_5",
}


def encode_as_cart(ss: int, pos: list[float]) -> Minecart:
    if ss == 0:
        return Minecart(cart_type="furnace", pos=pos)
    items = [
        Item(slot=slot, name="minecraft:wooden_shovel", count=1)
        for slot in range(ss_to_num_stacks[ss])
    ]
    return Minecart(pos=pos, items=items)


def encode_as_shulker(ss: int, slot: int) -> Item:
    items = [
        Item(slot=slot, name="minecraft:wooden_shovel", count=1)
        for slot in range(ss_to_num_stacks[ss])
    ]
    return Item.shulker(slot, items)


def encode_as_disc(ss: int, slot: int) -> Item:
    return Item(slot=slot, name=ss_to_disc[ss], count=1)


def encode_list_as_items(
    ss: list[int], medium: Literal["shulker", "disc"]
) -> list[Item]:
    gen_fn = encode_as_shulker if medium == "shulker" else encode_as_disc
    return [gen_fn(item, pos) for pos, item in enumerate(ss)]


def encode_rom1(
    carts: list[int], cart_pos: list[float], add_stop_move: bool
) -> list[Minecart]:
    carts = carts if not add_stop_move else carts + [0]
    return [encode_as_cart(ss, cart_pos) for ss in carts]


def encode_rom27(
    carts: list[list[int]], cart_pos: list[float], medium: Literal["shulker", "disc"]
) -> list[Minecart]:
    return [
        Minecart(pos=cart_pos, items=encode_list_as_items(cart, medium=medium))
        for cart in carts
    ]


def encode_rom729(
    carts: list[list[list[int]]], cart_pos: list[float]
) -> list[Minecart]:
    return [
        Minecart(
            pos=cart_pos,
            items=[
                Item.shulker(shulker_idx, encode_list_as_items(shulker, "disc"))
                for shulker_idx, shulker in enumerate(cart)
            ],
        )
        for cart in carts
    ]
