from nbtlib import File, schema
from nbtlib.tag import *

def add_item_to_cart(cart, item):
    cart.update({
            "Items": List[Compound](cart["Items"].append(item))
        })
    return cart

def add_item_to_sb(sb, item):
    sb["tag"]["BlockEntityTag"].update({
            'Items': List[Compound](sb["tag"]["BlockEntityTag"]["Items"].append(item))
        })
    return sb