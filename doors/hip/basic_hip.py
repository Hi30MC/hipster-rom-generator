import os
from doors.debug import FormatOptions, AutoLog
from doors.debug import CallTree


def write_file(path: str, content: str):
    os.makedirs(os.path.dirname(path), exist_ok=True)

    with open(path, "w") as f:
        f.write(content)


def write_call_tree(call_tree: CallTree, path: str):
    if not path.endswith(".yaml"):
        path += ".yaml"
    options = FormatOptions.yaml()
    options.skip_empty_methods = True
    content = call_tree.to_string(options)
    write_file(path, content)
    return content


def write_sequence[T](moves: list[T], path: str):
    write_file(path, "\n".join(map(str, moves)))


class BasicDoor[Move](metaclass=AutoLog):
    def __init__(self):
        self.moves: list[Move] = []
        self.call_tree = CallTree()

    def _add(self, *moves: Move):
        self.moves.extend(moves)
        self.call_tree.add_message(" ".join(map(str, moves)))

    def __iadd__(self, moves: list[Move] | Move):
        moves = moves if isinstance(moves, list) else [moves]
        self._add(*moves)
        return self

    def _write_call_tree(self, path: str):
        write_call_tree(self.call_tree, path)

    def _write_sequence(self, path: str):
        write_sequence(self.moves, path)


class BasicHip[Move](BasicDoor[Move]):
    piston_stack_depth: int
    max_obs: int

    def __init__(self):
        super().__init__()
        self.num_obs_out = 0
        self.stack_state = [False] * self.piston_stack_depth
