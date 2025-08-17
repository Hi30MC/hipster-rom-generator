import os
from doors.debug import FormatOptions, AutoLog
from doors.debug import CallTree


def write_file(path: str, content: str):
    os.makedirs(os.path.dirname(path), exist_ok=True)

    with open(path, "w") as f:
        f.write(content)


class BasicHip[Move: str](metaclass=AutoLog):
    piston_stack_depth: int
    max_obs: int

    def __init__(self):
        self.call_tree = CallTree()
        self.moves: list[Move] = []
        self.stack_state = [False] * self.piston_stack_depth
        self.num_obs_out = 0

    def __iadd__(self, moves: list[Move] | Move):
        moves_list: list[Move] = moves if isinstance(moves, list) else [moves]
        self.moves.extend(moves_list)
        self.call_tree.add_message(" ".join(str(msg) for msg in moves_list))
        return self

    def _write_call_tree(self, path: str):
        if not path.endswith(".yaml"):
            path += ".yaml"
        content = self.call_tree.to_string(FormatOptions.yaml())
        write_file(path, content)

    def _write_sequence(self, path: str):
        write_file(path, "\n".join(self.moves))
