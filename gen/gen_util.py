import nbtlib
from nbtlib import File, schema
from nbtlib.tag import *
from ast import literal_eval
import os

# Read and import conversion dictionaries

with open(os.path.join(os.getcwd(), "gen", "conversions", "shulker.txt"), 'r') as f:
    shulker_data = f.read()

shulker_conversion = literal_eval(shulker_data)


def get_shulker_conversion():
    return shulker_conversion


with open(os.path.join(os.getcwd(), "gen", "conversions", "shulker.txt"), "r") as f:
    disc_data = f.read()

disc_conversion = literal_eval(disc_data)


def get_disc_conversion():
    return disc_conversion


# Schema for Items (in inventory)

Item = schema("Item", {
    "Count": Byte,
    "Slot": Byte,
    "id": String
})

# Schema for minecarts

Minecart = schema("Minecart", {
    "Air": Short,
    "FallDistance": Float,
    "Fire": Short,
    "Id": String,
    "Invulnerable": Byte,
    "Items": List[Item],
    "Motion": List[Double],  # check
    "OnGround": Byte,
    "PortalCooldown": Int,
    "Pos": List[Double],  # check
    "Rotation": List[Float]  # check
})

# Schema for schematic file

Schematic = schema("Schematic", {
    "BlockData": ByteArray,
    "BlockEntities": List[String],
    "DataVersion": Int,
    "Entities": List[Minecart],
    "Height": Short,
    "Length": Short,
    "Palette": Compound,
    "PaletteMax": Int,
    "Version": Int,
    "Width": Short
})


def gen_base():
    return File(Schematic({
        "BlockData": [0],
        "BlockEntities": [],
        "DataVersion": 3337,
        "Entities": [],
        "Height": 1,
        "Length": 1,
        "Version": 2,
        "Palette": {
            "air": Int(0)
        },
        "PaletteMax": 1,
        "Width": 1
    }), gzipped=True)


def gen_cart(cart_type: String = "chest", items: List = [], pos: List[Double] = [0.5, 0, 0.5]):
    return Minecart({
        "Air": 300,
        "FallDistance": 0,
        "Fire": -1,
        "Id": f"{cart_type}_minecart",
        "Invulnerable": 0,
        "Items": List[Compound](items),
        "Motion": [0, 0, 0],
        "OnGround": 0,
        "PortalCooldown": 0,
        "Pos": pos,
        "Rotation": [90, 0]
    })


def gen_item(slot: int, name: String, count: int = 1):
    return Item({
        "Count": count,
        "Slot": slot,
        "id": name
    })


def gen_shulker_box(slot: int, items: List = []):
    box = Item({
        "Count": 1,
        "Slot": slot,
        "id": "minecraft:red_shulker_box"
    })
    box.update({"tag": Compound({
        "BlockEntityTag": Compound({
                "Items": List[Compound](items),
                "id": String("minecraft:shulker_box")
                })
    }),
        "id": String("minecraft:red_shulker_box")})
    return box


def add_item_to_cart(cart, item):
    cart.update({"Items": List[Compound](cart["Items"] + [item])})
    return cart


def gen_ss_cart(ss: int, pos: [Double] = [0.5, 0, 0.5]):
    if ss == 0:
        return gen_cart(cart_type="furnace", pos=pos)
    items = []
    for i in range(shulker_conversion[ss]):
        items.append(gen_item(i, "minecraft:wooden_shovel", 1))

    return gen_cart(items=items, pos=pos)


def gen_ss_sb(slot: int, ss: int):
    box = Item({
        "Count": 1,
        "Slot": slot,
        "id": "minecraft:red_shulker_box"
    })

    items = []

    for i in range(shulker_conversion[ss]):
        items.append(gen_item(i, "minecraft:wooden_shovel", 1))

    # add generated item list to box data
    box.update({"tag": Compound({
        "BlockEntityTag": Compound({
                "Items": List[Compound](items),
                "id": String("minecraft:shulker_box")
                })
    }),
        "id": String("minecraft:red_shulker_box")})
    return box


def gen_ss_disc(slot: int, ss: int):
    return Item({
        "Count": 1,
        "Slot": slot,
        "id": disc_conversion[ss]
    })
