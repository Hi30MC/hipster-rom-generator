from enum import Enum
from typing import Literal


class Move(Enum):
    ...

class HipSeq:
    def __init__(self):
        self.moves: list[Move] = []

    def __iadd__(self, moves: list[Move]):
        self.moves.extend(moves)
        return self

    def closing(self):
        ...

    def opening(self):
        ...

    def everything(self):
        self.closing()
        self.opening()

    def more_pistons(self, layer: int):
        """
        Adds another layer of pistons on top, spits it above to allow.
        """
        match layer:
            case 1:
                return []
            case _:
                raise ValueError

    def full_row(self, layer: int):
        """
        Does full row.
        _____B -> B_____
        """
        ...
        self.more_pistons(layer // 2)  # todo: check math
        self.row_high(layer)

    def row_high(self, layer: int, pistons_very_high: bool = False):
        """
        Does row, but with layer of pistons already up.
            _P___B -> B_____
        """
        self.extend_retract_obs(layer, pistons_very_high)
        self.retract(layer)

    def extend_retract_obs(self, layer: int, pistons_very_high: bool = False):
        """
        Extend, ending in "piston-obs stack" state.

        Example:
            _P___B -> ___PB*
        """
        self.extend(layer, pistons_very_high)
        self.retract_obs(layer)

    def extend(self, layer: int, pistons_very_high: bool = False):
        ...

    def retract_obs(self, layer: int):
        ...

    def retract(self, layer: int):
        self.pull(layer - 2)
        self.row_high(layer - 1, True)

    def pull(self, layer: int):
        """
        Pulls pistons at row n-1 down.
        _____P -> ____P_
        """
        if layer == 1:
            return

        self.more_pistons(layer // 2)
        self.extend_retract_obs(layer)

        # todo: base case

        # pull bottommost piston down
        self.full_row(layer - 2)
        # todo: less_pistons


if __name__ == "__main__":
    r = HipSeq()
    r.opening()
    r.closing()
    print(r.moves)