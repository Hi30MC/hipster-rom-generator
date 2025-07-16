from nbtlib import schema
from nbtlib.tag import *

Item = schema("Item", {
        "Count": Byte,
        "Slot": Byte,
        "id": String
    })

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