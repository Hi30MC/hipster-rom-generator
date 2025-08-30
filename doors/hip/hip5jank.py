from enum import Enum
from typing import Iterable

from doors.debug import AutoLog, CallTree, skip_logging
from doors.hip.basic_hip import write_call_tree, write_sequence
from typing import Callable


class Move(Enum):
    A = "A"
    BA = "BA"
    BACC = "BACC"
    FOBACC = "FOBACC"
    FOBACCW = "FOBACCW"
    S = "S"
    E = "E"
    WAIT = "wait"
    HALT = "halt"

    def __str__(self):
        return self.value

    def __iter__(self):
        return iter([self])


Moves = Iterable[Move]
Macro = Iterable[Move] | Callable[["Hip5JankSeq"], None]


WAIT = Move.WAIT
HALT = Move.HALT

E = Move.E
S = (Move.S, Move.WAIT)
SS = (Move.S, Move.S, Move.WAIT)

A = Move.A
BA = Move.BA
BACC = (Move.BACC, Move.WAIT)
BAC_BA = (Move.BACC, Move.BA)

FOBACC = (Move.FOBACC, Move.WAIT)
FOBAC_BA = (Move.FOBACC, Move.BA)

FOBACCW = (Move.FOBACCW, Move.WAIT)
FOBACW_BA = (Move.FOBACCW, Move.BA)


class WormState(Enum):
    Down = 0
    Up = 1
    Folded = 2


def low(door: "Hip5JankSeq"):
    assert not door.a_sand_high


def high(door: "Hip5JankSeq"):
    assert door.a_sand_high


def e_empty(door: "Hip5JankSeq"):
    assert door.e_empty


def e_full(door: "Hip5JankSeq"):
    assert not door.e_empty


class Hip5JankSeq(metaclass=AutoLog):
    initial_a_sand_high = False

    def __init__(self):
        self.moves: list[Move] = []
        self.call_tree = CallTree()
        self.e_empty = False
        self.worm_state = WormState.Down
        self.a_sand_high = self.initial_a_sand_high

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
                assert 0, "Pushing fold into worm"

    def _on_worm(self):
        match self.worm_state:
            case WormState.Down:
                self.worm_state = WormState.Up
            case WormState.Up:
                self.worm_state = WormState.Down
            case WormState.Folded:
                pass

    def _add(self, *elements: Move | Macro):
        row_message = []

        def pop_wait():
            if self.moves and self.moves[-1] == Move.WAIT:
                self.moves.pop()
                row_message.append("~~")

        def flatten_moves(elements: Iterable[Macro]) -> Iterable[Move]:
            for element in elements:
                if callable(element):
                    element(self)
                else:
                    yield from element

        for move in flatten_moves(elements):
            match move:
                case Move.A | Move.S:
                    pop_wait()
                case Move.E:
                    self.e_empty = not self.e_empty
                case Move.FOBACC:
                    self._on_fold()
                case Move.FOBACCW:
                    self._on_fold()
                    self._on_worm()

            if "A" in move.value:
                self.a_sand_high = not self.a_sand_high

            self.moves.append(move)
            row_message.append(move)

        self.call_tree.add_message(" ".join(map(str, row_message)))

    def __iadd__(self, other: list[Macro] | Macro):
        moves = other if isinstance(other, list) else [other]
        self._add(*moves)
        return self

    def closing(self):
        # first move needs to be E, for reasons
        # state after opening: piston right underneath floor
        self += [E, E, BACC, BA]
        self += [S, BAC_BA, BAC_BA, S]
        self += [E, BA, FOBACC, BA, FOBACCW, BA, BA, FOBACCW]
        self += [A, E, BA, BACC, BA]
        self += [S, BAC_BA, BAC_BA, S, BAC_BA]

    @skip_logging
    def everything(self):
        self.assert_retracted_state()
        assert self.a_sand_high == self.initial_a_sand_high

        self.opening()
        self += HALT
        self.closing()
        self += HALT

        self.assert_retracted_state()
        assert self.a_sand_high == self.initial_a_sand_high

    def assert_retracted_state(self):
        assert not self.e_empty
        assert self.worm_state == WormState.Down

    @skip_logging
    def opening(self):
        self.row1()
        self.row2()
        self.assert_retracted_state()
        self.row3()
        self.assert_retracted_state()
        self.row4()
        self.assert_retracted_state()
        self.row5()
        self.assert_retracted_state()

    def ba_sto(self):
        assert self.moves[-1] == Move.BA
        if not self.a_sand_high:
            # was high, need an extra BA
            self += [BA, S]
        else:
            self += S

    def row1(self):
        # start with E, because button powers E
        self += [E, E, A, BACC, low, BA]
        self.ba_sto()

    def dpe_retract(self):
        self += [A, BA, e_empty, E, BACC, BA]

    # note: tpe retract is just [FO]BAC_BA

    def row2(self):
        # We can take a shortcut, powering the floor block on row 2:
        # there's no storage block, so we can ignore parity
        self += [E, BA, S, low, BA, S]
        # finish from pull0
        self += BACC
        self.dpe_retract()
        self.ba_sto()

    def row3(self):
        self += [E, BA]
        self.row3_retract()
        self.dpe_retract()
        self.ba_sto()

    def row3_retract(self):
        self += [FOBAC_BA, A, BA, BA]
        self += [FOBAC_BA, BAC_BA]
        self += [FOBACC, BA, BA, BA, BA]
        if self.e_empty and self.worm_state == WormState.Down:
            self += [SS, BACC]
        else:
            self += FOBACC

    def row4_obs_or_block(self, pistons_high):
        self += FOBAC_BA
        if not pistons_high:
            self += [BAC_BA, A]
        self += [A, BAC_BA, BA]
        self += [FOBAC_BA, FOBACC, BA, BA]
        if not self.e_empty:
            self += SS
        else:
            self += FOBACC

        self += [e_full, E, BACC]
        self.dpe_retract()

    def row4(self):
        self += [E, BA]
        self.row4_obs_or_block(False)
        self.row3_retract()
        self.dpe_retract()
        # ba parity doesn't matter here
        self += S

    def row5(self):
        self += [E, BA, S, high, BA]
        self.row4_obs_or_block(False)
        self.ba_sto()
        # pull 3
        self += [E, BA, FOBAC_BA, A, BA, BA]
        self += [FOBAC_BA, BAC_BA, E, BACC, BA]
        self.row4_obs_or_block(True)
        self.row3_retract()
        self += [A, e_empty, E, BACC]


def main():
    door = Hip5JankSeq()
    try:
        door.everything()
    except Exception as e:
        print(f"An error occurred: {e}")
    finally:
        write_sequence(door.moves, "door_meta/5x5hip_jank/sequence.txt")
        write_call_tree(door.call_tree, "door_meta/5x5hip_jank/call_tree")
    print("Done")


if __name__ == "__main__":
    main()
