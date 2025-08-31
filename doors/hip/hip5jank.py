from enum import Enum
from collections import Counter
from typing import Iterable

from doors.debug import AutoLog, CallTree, skip_logging
from doors.hip.basic_hip import write_call_tree, write_sequence
from typing import Callable


class Move(Enum):
    A = "A"
    BA = "BA"
    BACC = "BACC"
    OBACC = "OBACC"
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
BAC_BCA = (Move.BACC, Move.BA)


OBACC = (Move.OBACC, Move.WAIT)
OBAC_BCA = (Move.OBACC, Move.BA)

FOBACC = (Move.FOBACC, Move.WAIT)
FOBAC_BCA = (Move.FOBACC, Move.BA)

FOBACCW = (Move.FOBACCW, Move.WAIT)
# FOBACW_BA = (Move.FOBACCW, Move.BA)


class WormState(Enum):
    Down = 0
    Up = 1
    Folded = 2


def low(door: "Hip5JankSeq"):
    assert not door.a_sand_high


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
                case Move.A | Move.S | Move.HALT:
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

    def assert_retracted_state(self):
        assert not self.e_empty
        assert self.worm_state == WormState.Down

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

    def closing(self):
        # state after opening: piston right underneath floor
        self += [BAC_BCA, BA]
        self += [S, BAC_BCA, A, BAC_BCA, BA, S]
        self += [E, BA, FOBACC, BA, FOBACCW, BA, FOBACCW, BA, FOBACCW, BA, BA, FOBACC]
        self += [A, A, E, BA, BACC, BA]
        self += [S, BAC_BCA]
        self += [E, FOBACCW, BA, BA, FOBACC]
        self += [A, A, E, BA, BACC, BA]
        self += [S, BAC_BCA]

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

    def dpe_retract(self):
        self += [A, BA, e_empty, E, BACC, BA]

    def row1(self):
        self += [E, E, A, BACC, low, BA, S]

    def row2(self):
        # We can take a shortcut, powering the floor block on row 2:
        # so we
        self += [E, BA, S, low, BA, S]
        self += BACC
        self.dpe_retract()
        self += S

    def row3(self):
        self += [E, BA]
        self.row3_high(True)

    def row3_high(self, is_special=False):
        self.row3_retract(is_special)
        self.dpe_retract()
        self += S

    def row3_pull(self):
        self += [OBACC, BA, BA, OBACC, A, BA]  # piston parity fix
        self += [OBACC, BA, BA, BA, BA, OBACC]

    def row3_retract(self, is_special: bool = False):
        if is_special:
            self += FOBACCW
        else:
            self += FOBACC

        self += [WAIT, A, A, BA, BA]

        if is_special:
            self += FOBAC_BCA
        else:
            self += OBAC_BCA
        self += [A, BAC_BCA, BA]
        self.row3_pull()

    def row4_obs_or_block(self, pistons_high=False):
        a_moves = [] if pistons_high else [A]
        self += [OBACC, WAIT, A, BAC_BCA, a_moves, BAC_BCA, BA, BA]
        if self.e_empty:
            self += FOBACC
        else:
            self += OBACC
        self += [e_full, E, BA]
        self.row3_pull()
        self.dpe_retract()

    def row4(self):
        self += [E, BA]
        self.row4_obs_or_block()
        self.row3_high()
        # self += A  # sand parity fix

    def row5(self):
        self += [E, BA, S, BAC_BCA, A, BAC_BCA, BA]
        self.row4_obs_or_block()
        self += S
        # pull 3
        self += [E, BA, OBACC, A, A, BA, BA]
        self += [OBAC_BCA, A, BAC_BCA, BA, E, BACC, BA]
        self.row4_obs_or_block(True)
        self.row3_retract()
        self += [A, e_empty, E, BACC]


def main(method="everything", out_file="sequence.txt"):
    door = Hip5JankSeq()
    try:
        getattr(door, method)()
    except Exception as e:
        print("An error occurred:", e)
        import traceback

        print(traceback.format_exc())
    finally:
        write_sequence(door.moves, f"door_meta/5x5hip_jank/{out_file}")
        write_call_tree(door.call_tree, f"door_meta/5x5hip_jank/call_tree_{method}")

        move_counts = Counter(door.moves)
        print("Move Counts:")
        for move, count in move_counts.items():
            print(f"{move}: {count}")
    print("Done")


if __name__ == "__main__":
    main()
