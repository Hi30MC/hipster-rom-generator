from nbtlib import File, schema
from nbtlib.tag import *
from gen.util import schemas

def gen_base():
    return File(schemas.Schematic({
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
    return schemas.Minecart({
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

def gen_shulker_box(slot: int, items: List = []):
    box = schemas.Item({
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

def gen_item(slot: int, name: String, count: int = 1):
    return schemas.Item({
        "Count": count,
        "Slot": slot,
        "id": name
    })