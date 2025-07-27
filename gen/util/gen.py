from nbtlib import File
from nbtlib.tag import *
from gen.util import layouts

def base_file():
    return File(layouts.Schematic({
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

def cart( pos: list[float], cart_type: str = "chest", items: list = []):
    return layouts.Minecart({
        "Air": 300,
        "FallDistance": 0,
        "Fire": -1,
        "Id": f"{cart_type}_minecart",
        "Invulnerable": 1,
        "Items": List[Compound](items),
        "Motion": [0, 0, 0],
        "OnGround": 0,
        "PortalCooldown": 0,
        "Pos": List[Double](pos),
        "Rotation": [90, 0],
    })

def shulker(slot: int, items: list = []):
    box = layouts.Item({
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

def item(slot: int, name: str, count: int = 1):
    return layouts.Item({
        "Count": count,
        "Slot": slot,
        "id": name
    })
