from enum import Enum
import collections
from doors.debug import AutoLog, CallTree
from doors.hip.basic_hip import write_call_tree, write_sequence
from typing import NamedTuple
from typing import Iterable
from typing import Generator
from typing import Sequence


class Move(Enum):
    A = "A"
    BA = "BA"
    BACC = "BAC"
    FOBAC = "OBAC"
    FOBACW = "FOBACW"
    STO = "STO"
    E = "E"
    WAIT = "WAIT"
    STOP = "STOP"

    def __str__(self):
        return self.value


A = Move.A
BA = Move.BA
STO = Move.STO
E = Move.E
WAIT = Move.WAIT
STOP = Move.STOP


class Macro(NamedTuple):
    name: str
    moves: tuple[Move, ...]

    def __str__(self):
        return self.name


BACC_0 = Macro("BACC_N", (Move.BACC, Move.WAIT))
BACC_BA = Macro("BACC_BA", (Move.BACC, Move.BA))
FOBAC_0 = Macro("FOBAC_N", (Move.FOBAC, Move.WAIT))
FOBAC_BA = Macro("FOBAC_BA", (Move.FOBAC, Move.BA))
FOBACW_0 = Macro("FOBACW_N", (Move.FOBACW, Move.WAIT))
FOBACW_BA = Macro("FOBACW_BA", (Move.FOBACW, Move.BA))


class WormState(Enum):
    Down = 0
    Up = 1
    Folded = 2


def flatten_moves(elements: Iterable[Move | Macro]) -> Generator[Move]:
    for element in elements:
        if isinstance(element, Move):
            yield element
        elif isinstance(element, Macro):
            yield from element.moves


class Hip5JankSeq(metaclass=AutoLog):
    def __init__(self):
        self.moves: list[Move] = []
        self.call_tree = CallTree()
        self.e_empty = False
        self.worm_state = WormState.Down

    def _on_fold(self):
        match self.e_empty, self.worm_state:
            case True, WormState.Down:
                self.worm_state = WormState.Folded
                self.e_empty = False
            case (True, WormState.Up) | (True, WormState.Folded):
                pass
            case False, WormState.Folded:
                self.worm_state = WormState.Down
                self.e_empty = True
            case (False, WormState.Down) | (False, WormState.Up):
                raise RuntimeError("Pushing fold into worm")

    def _on_worm(self):
        match self.worm_state:
            case WormState.Down:
                self.worm_state = WormState.Up
            case WormState.Up:
                self.worm_state = WormState.Down
            case WormState.Folded:
                pass

    def _add(self, *elements: Move | Macro):
        def pop_wait():
            if self.moves and self.moves[-1] == Move.WAIT:
                self.moves.pop()

        for move in flatten_moves(elements):
            match move:
                case Move.WAIT:
                    pop_wait()
                case Move.E:
                    self.e_empty = not self.e_empty
                case Move.FOBAC:
                    self._on_fold()
                case Move.FOBACW:
                    self._on_fold()
                    self._on_worm()

            self.moves.append(move)

        self.call_tree.add_message(" ".join(map(str, elements)))

    def __iadd__(self, other: Sequence[Move | Macro]):
        self._add(*other)
        return self

    def closing(self):
        self += []


def main():
    door = Hip5JankSeq()
    try:
        door.closing()
    finally:
        write_sequence(door.moves, "door_meta/5x5hip_jank/sequence.txt")
        write_call_tree(door.call_tree, "door_meta/5x5hip_jank/call_tree")


if __name__ == "__main__":
    main()
