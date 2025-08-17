from typing_extensions import NewType
from doors.hip.basic_hip import BasicDoor
from typing import override
import collections

Move = NewType("Move", str)

A = Move("A")
BA = Move("BA")
BAC = Move("BAC")
OBAC = Move("OBAC")
FOBAC = Move("FOBAC")
FOBACW = Move("FOBACW")
STO = Move("STO")
E = Move("E")
WAIT = Move("WAIT")
STOP = Move("STOP")


# pseudo-moves, to assert that a_parity is a specific value
def up(move: Move) -> Move:
    return Move(f"up({move})")


def down(move: Move) -> Move:
    return Move(f"down({move})")


class Hip5JankSeq(BasicDoor[Move]):
    def __init__(self):
        super().__init__()
        self.a_parity_up = False
        self.move_count: collections.Counter[Move] = collections.Counter()

    @override
    def _add(self, *moves: Move):
        for move in moves:
            if move.startswith("up"):
                assert self.a_parity_up
                move = Move(move[3:-1])
            elif move.startswith("down"):
                assert not self.a_parity_up
                move = Move(move[5:-1])
            if "A" in move:
                self.a_parity_up = not self.a_parity_up
            self.move_count[move] += 1
            # Put stripped move in sequence
            self.moves.append(move)
        # Put pseudo-moves in call tree
        self.call_tree.add_message(" ".join(moves))

    def closing(self):
        # first move must be E to not break stuff
        self += [E, E, BAC, BA]
        self += [STO, down(BA), STO, E]


def main():
    door = Hip5JankSeq()
    door.closing()
    door._write_sequence("door_meta/5x5hip_jank/sequence.txt")
    yaml = door._write_call_tree("door_meta/5x5hip_jank/call_tree")
    print(yaml)


if __name__ == "__main__":
    main()
