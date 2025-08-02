from nbtlib import CompoundSchema
from nbtlib.tag import (Byte, ByteArray, Compound, Double, Float, Int, List, Short, String)
from typing import Literal, Sequence


class Item(CompoundSchema):
    schema = {"Count": Byte, "Slot": Byte, "id": String}

    def __init__(self, count: int, name: str, slot: int):
        super().__init__(Count=count, Slot=slot, id=name)

    @classmethod
    def shulker(cls, slot: int, items: list["Item"] = []):
        box = Item(count=1, slot=slot, name="minecraft:red_shulker_box")

        box["tag"] = Compound(
            {
                "BlockEntityTag": Compound(
                    {
                        "Items": List[Compound](items),
                        "id": String("minecraft:shulker_box"),
                    }
                )
            }
        )
        return box

    # For shulker box
    def add_inner_item(self, item: "Item"):
        self["tag"]["BlockEntityTag"]["Items"].append(item)


CartType = Literal["chest", "furnace", "hopper"]


class Minecart(CompoundSchema):
    schema = {
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
        "Rotation": List[Float],  # check
    }

    @classmethod
    def simple(
            cls,
            cart_type: CartType = "chest",
            pos: Sequence[float] = (0, 0.5, 0),
            items: Sequence[Item] = (),
    ):
        return Minecart(
            {
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
            }
        )

    def add_item(self, item: Item):
        self["Items"].append(item)


class Schematic(CompoundSchema):
    schema = {
        "BlockData": ByteArray,
        "BlockEntities": List[String],
        "DataVersion": Int,
        "Entities": List[Minecart],
        "Height": Short,
        "Length": Short,
        "Palette": Compound,
        "PaletteMax": Int,
        "Version": Int,
        "Width": Short,
    }

    @classmethod
    def empty(cls):
        return Schematic(
            {
                "BlockData": [0],
                "BlockEntities": [],
                "DataVersion": 3337,
                "Entities": [],
                "Height": 1,
                "Length": 1,
                "Version": 2,
                "Palette": {"air": Int(0)},
                "PaletteMax": 1,
                "Width": 1,
            }
        )
