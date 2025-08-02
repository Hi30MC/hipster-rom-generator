from typing import Sequence
from .types import Minecart, Item

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


def cart_for_ss(ss: int, pos: Sequence[float] = (0.5, 0.0, 0.5)):
    if ss == 0:
        return Minecart(cart_type="furnace", pos=pos)
    items = [
        Item(slot=slot, name="minecraft:wooden_shovel", count=1)
        for slot in range(ss_to_num_stacks[ss])
    ]
    return Minecart(pos=pos, items=items)


def shulker_for_ss(slot: int, ss: int):
    items = [
        Item(slot=slot, name="minecraft:wooden_shovel", count=1)
        for slot in range(ss_to_num_stacks[ss])
    ]
    return Item.shulker(slot, items)


def disc_for_ss(slot: int, ss: int):
    return Item(slot=slot, name=ss_to_disc[ss], count=1)
