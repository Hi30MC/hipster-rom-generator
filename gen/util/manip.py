from nbtlib import File
from nbtlib.tag import *

def add_item_to_cart(cart, item):
    cart.update({
            "Items": List[Compound](cart["Items"] + [item])
        })
    return cart

def add_item_to_sb(sb, item):
    sb["tag"]["BlockEntityTag"].update({
            'Items': List[Compound](sb["tag"]["BlockEntityTag"]["Items"] + [item])
        })
    return sb