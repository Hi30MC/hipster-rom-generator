from nbtlib import CompoundSchema, schema
from nbtlib.tag import (
    Byte,
    ByteArray,
    Compound,
    Double,
    Float,
    Int,
    List,
    Short,
    String,
)
from typing import Literal, Sequence


class ShulkerItem(CompoundSchema):
    schema = {
        "item": schema(
            "",
            {
                "count": Int,
                "id": String,
            },
        ),
        "slot": Int,
    }

    def __init__(self, count: int, name: str, slot: int):
        super().__init__(
            {
                "item": {
                    "count": Int(count),
                    "id": String(name),
                },
                "slot": Int(slot),
            }
        )


class CartItem(CompoundSchema):
    schema = {"Count": Byte, "Slot": Byte, "id": String, "components": List[Compound]}

    def __init__(self, count: int, name: str, slot: int):
        super().__init__(
            {
                "Count": Byte(count),
                "Slot": Byte(slot),
                "id": String(name),
            }
        )

    @classmethod
    def shulker(cls, slot: int, items: Sequence[ShulkerItem] = ()):
        box = CartItem(count=1, slot=slot, name="minecraft:red_shulker_box")

        box["components"] = Compound({"minecraft:container": List(items)})
        return box

    def add_inner_item(self, item: ShulkerItem):
        self["tag"]["BlockEntityTag"]["Items"].append(item)


CartType = Literal["chest", "furnace", "hopper"]


class Minecart(CompoundSchema):
    schema = {
        "Data": schema(
            "",
            {
                "Motion": List[Double],
                "Invulnerable": Byte,
                "Air": Short,
                "OnGround": Byte,
                "PortalCooldown": Int,
                "Rotation": List[Float],
                "FallDistance": Float,
                "Pos": List[Double],
                "Fire": Short,
                "Items": List[CartItem],
                "FlippedRotation": Byte,
                "HasTicked": Byte,
            },
        ),
        "Id": String,
        "Pos": List[Double],
    }

    def __init__(
        self,
        cart_type: CartType = "chest",
        pos: Sequence[float] = (0.5, 0, 0.5),
        items: Sequence[CartItem] = (),
    ):
        super().__init__(
            {
                "Data": {
                    "Motion": [0, 0, 0],
                    "Invulnerable": 1,
                    "Air": 300,
                    "OnGround": 0,
                    "PortalCooldown": 0,
                    "Rotation": [90, 0],
                    "FallDistance": 0,
                    "Pos": List[Double](pos),
                    "Fire": -1,
                    "Items": List[Compound](items),
                    "FlippedRotation": 0,
                    "HasTicked": 0,
                },
                "Id": f"{cart_type}_minecart",
                "Pos": pos,
            }
        )

    def add_item(self, item: CartItem):
        self["Items"].append(item)


class Schematic(CompoundSchema):
    schema = {
        "Schematic": schema(
            "",
            {
                "Version": Int,
                "DataVersion": Int,
                "Metadata": Compound,
                "Width": Short,
                "Height": Short,
                "Length": Short,
                "Offset": List[Int],
                "Blocks": schema(
                    "",
                    {
                        "Palette": Compound,
                        "Data": ByteArray,
                        "BlockEntities": List[Compound],
                    },
                ),
                "Entities": List[Minecart],
            },
        ),
    }

    @classmethod
    def empty(cls) -> "Schematic":
        return Schematic(
            {
                "Schematic": {
                    "Version": 3,
                    "DataVersion": 4189,
                    # "Metadata": {
                    #     "Date": 0,
                    #     "WorldEdit": {
                    #         "Version": "7.3.10",
                    #         "EditingPlatform": "enginehub:fabric",
                    #         "Origin": [0, 0, 0],
                    #         "Platforms": {
                    #             "enginehub:fabric": {
                    #                 "Name": "Fabric-Official",
                    #                 "Version": "7.3.10+7004-768a436",
                    #             }
                    #         },
                    #     },
                    # },
                    "Width": 1,
                    "Height": 1,
                    "Length": 1,
                    "Offset": [0, 0, 0],
                    "Blocks": {
                        "Palette": {"air": Int(0)},
                        "Data": [0],
                        "BlockEntities": [],
                    },
                    "Entities": [],
                }
            }
        )

    def set_entities(self, entities: list[Minecart]):
        self["Schematic"]["Entities"] = entities
