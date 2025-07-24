from enum import Enum
from os import getcwd, path

class Move(Enum):
    STOP = "stop"
    WAIT = "wait"
    STOAF = "stoaf"
    B = "b"
    C = "c"
    D = "d"
    E = "E"
    SSTO = "ssto"
    BOBS = "bobs"
    WORM = "worm"
    FOLD = "fold"


stop = Move.STOP
wait = Move.WAIT
stoaf = Move.STOAF
a = Move.STOAF
b = Move.B
c = Move.C
d = Move.D
e = Move.E
ssto = Move.SSTO
bobs = Move.BOBS
worm = Move.WORM
fold = Move.FOLD


class HipSeq6:
    piston_stack_depth = 4
    def __init__(self):
        self.moves: list[Move] = []
        self.stack_state = [False] * self.piston_stack_depth

    def __iadd__(self, moves: list[Move] | Move):
        if isinstance(moves, Move):
            self.moves.append(moves)
        elif isinstance(moves, list):
            self.moves.extend(moves)
        return self

    def closing(self):
        self += [
            wait,
            *[ssto, b, worm]*4,
            stoaf, ssto, d, d, b, stoaf,
            stop,
        ]

    def opening(self):
        self.retract(1)
        self += ssto
        self.row_high(2)

    def everything(self):
        self.closing()
        self.opening()

    def more_pistons(self, layer: int):
        """
        Adds another layer of pistons on top, spits it above to allow.
        """
        if any(self.stack_state[:layer]):
            raise ValueError(f"not all layers below {layer} are False.")
        if self.stack_state[layer]:
            raise ValueError(f"layer {layer} is already True.")

        self.stack_state[layer] = True

        match layer:
            case _:
                raise NotImplementedError

    def less_pistons(self, layer: int):
        if any(self.stack_state[:layer]):
            raise ValueError(f"Invalid stack: not all layers below {layer} are False.")
        if not self.stack_state[layer]:
            raise ValueError(f"layer {layer} is already False.")

        self.stack_state[layer] = False

        match layer:
            case 0:
                self += [d, c, c]
            case _:
                raise NotImplementedError

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
        self.extend(layer, pistons_very_high)
        self.retract(layer)

    def extend(self, layer: int, pistons_very_high: bool = False):
        match layer:
            case -1: self += b
            case 0: self += a
            case 1: self += [b, a]
            case _:
                raise NotImplementedError

    def retract(self, layer: int):
        if layer == -1:
            self += b
            return

        self.pull(layer - 2)
        self.row_high(layer - 1, True)

    def pull(self, layer: int):
        """
        Pulls pistons at row n-1 down.
        _____P -> ____P_
        """
        if layer == -2:
            self.less_pistons(0)
            return
        if layer == -1:
            self += b
            return

        self.more_pistons(layer // 2)
        self.extend_retract_obs(layer)

        # todo: base case

        # pull bottommost piston down
        self.full_row(layer - 2)
        # todo: less_pistons


def write_file(door_name: str):
    door = HipSeq6()
    door.closing()
    door.opening()
    moves = [m.value for m in door.moves]
    with open(path.join(getcwd(), "door_meta", door_name, "sequence.txt"), "w") as f:
        for m in moves:
            f.write(m)
        return 0
    return -1

# python -m gen.hip.hip6.py
if __name__ == "__main__":
    # write_file("hip6x6_sequence.txt")
    door = HipSeq6()
    door.opening()
    print(door.moves)
