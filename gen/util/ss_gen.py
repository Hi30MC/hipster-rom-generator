from nbtlib import File, schema
from nbtlib.tag import *
from gen.util import main_gen, conversions, schemas, item_manip

def gen_ss_cart(ss: int, pos: [Double] = [0.5, 0, 0.5]):
    if ss == 0:
        return main_gen.gen_cart(cart_type="furnace", pos=pos)
    items = []
    for i in range(conversions.get_shulker_conversion()[ss]):
        items.append(main_gen.gen_item(i, "minecraft:wooden_shovel", 1))

    return main_gen.gen_cart(items=items, pos=pos)

def gen_ss_sb(slot: int, ss: int):
    box = main_gen.gen_shulker_box()

    for i in range(conversions.get_shulker_conversion()[ss]):
        item_manip.add_item_to_sb(box, main_gen.gen_item(i, "minecraft:wooden_shovel", 1))

    return box

def gen_ss_disc(slot: int, ss: int):
    return schemas.Item({
        "Count": 1,
        "Slot": slot,
        "id": conversions.get_disc_conversion()[ss]
    })
