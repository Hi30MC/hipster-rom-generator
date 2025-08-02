from nbtlib.path import NamedTuple
from typing import Sequence
import json


class GenParams(NamedTuple):
    density: int

    cart_pos: Sequence[float] = [0.5, 0, 0.5]

    cut_wait_moves: bool = False

    min_carts: int = 0
    min_items_per_cart: int = 0
    min_items_per_shulker: int = 0

    @classmethod
    def parse(cls, contents: str) -> "GenParams":
        return GenParams(**json.loads(contents))
