from abc import ABC, ABCMeta
import os
from typing import Protocol
from doors.debug import SeqDebug, DebugMeta


class MoveProtocol(Protocol):
    @property
    def value(self) -> str: ...


class DebugABCMeta(DebugMeta, ABCMeta):
    pass


class BasicHip[Move: MoveProtocol](SeqDebug, ABC, metaclass=DebugABCMeta):
    piston_stack_depth: int
    max_obs: int

    def __init__(self):
        super().__init__()
        self.moves: list[Move] = []
        self.stack_state = [False] * self.piston_stack_depth
        self.num_obs_out = 0

    def __iadd__(self, moves: list[Move] | Move):
        moves = moves if isinstance(moves, list) else [moves]
        self.moves.extend(moves)
        self._log(*[move.value for move in moves])
        return self

    def _write_sequence(self, path: str):

        os.makedirs(os.path.dirname(path), exist_ok=True)

        with open(path, "w") as f:
            f.write("\n".join(move.value for move in self.moves))
