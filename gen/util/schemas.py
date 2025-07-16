from nbtlib import schema
from nbtlib.tag import *

# Schema for Items (in inventory)
def get_item_schema():
    return schema("Item", {
        "Count": Byte,
        "Slot": Byte,
        "id": String
    })

# Schema for minecarts

def get_minecart_schema():
    return schema("Minecart", {
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

def get_schematic_schema():
    return schema("Schematic", {
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