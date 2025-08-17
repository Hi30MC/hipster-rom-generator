from abc import ABC, ABCMeta
import os
from doors.debug import SeqDebug, DebugMeta


class DebugABCMeta(DebugMeta, ABCMeta):
    pass


class BasicHip[Move: str](SeqDebug, ABC, metaclass=DebugABCMeta):
    piston_stack_depth: int
    max_obs: int

    def __init__(self):
        super().__init__()
        self.moves: list[Move] = []
        self.stack_state = [False] * self.piston_stack_depth
        self.num_obs_out = 0

    def __iadd__(self, moves: list[Move] | Move):
        moves_list: list[Move] = moves if isinstance(moves, list) else [moves]
        self.moves.extend(moves_list)
        self._log(*moves_list)
        return self

    def _write_sequence(self, path: str):

        os.makedirs(os.path.dirname(path), exist_ok=True)

        with open(path, "w") as f:
            f.write("\n".join(self.moves))
