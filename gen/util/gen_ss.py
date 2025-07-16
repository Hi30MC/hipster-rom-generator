from nbtlib import File
from nbtlib.tag import *
from gen.util import gen, conversions, layouts, manip

def cart(ss: int, pos: [Double] = [0.5, 0, 0.5]):
    if ss == 0:
        return gen.cart(cart_type="furnace", pos=pos)
    items = []
    for i in range(conversions.chest()[ss]):
        items.append(gen.item(i, "minecraft:wooden_shovel", 1))

    return gen.cart(items=items, pos=pos)

def shulker(slot: int, ss: int):
    box = gen.shulker(slot)

    for i in range(conversions.shulker()[ss]):
        manip.add_item_to_sb(box, gen.item(i, "minecraft:wooden_shovel", 1))

    return box

def disc(slot: int, ss: int):
    return layouts.Item({
        "Count": 1,
        "Slot": slot,
        "id": conversions.disc()[ss]
    })
