from gen.util import gen, conversions, layouts, manip

def cart(ss: int, pos: list[float] = [0.5, 0.0, 0.5]):
    if ss == 0:
        return gen.cart(cart_type="furnace", pos=pos)
    cart = gen.cart(pos=pos)
    for i in range(conversions.chest()[ss]):
        manip.add_item_to_cart(cart, gen.item(i, "minecraft:wooden_shovel", 1))
    return cart

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
