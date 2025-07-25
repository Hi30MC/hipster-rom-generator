from enum import Enum
from os import getcwd, path
import functools
import hashlib
import os

class Move(Enum):
    STOP = "stop"
    WAIT = "wait"
    A = "a"
    B = "b"
    C = "c"
    D = "d"
    E = "e"
    SSTO = "ssto"
    BOBS = "bobs"
    WORM = "worm"
    FOLD = "fold"

stop = Move.STOP
wait = Move.WAIT
a = Move.A
b = Move.B
c = Move.C
d = Move.D
e = Move.E
ssto = Move.SSTO
bobs = Move.BOBS
worm = Move.WORM
fold = Move.FOLD

def get_indent(depth):
    return "\u23D0 " * depth

def get_method_color(method_name, bold=False):
    """Get a consistent 24-bit RGB color for a method name based on its hash"""
    # Generate RGB values from hash
    hash_bytes = hashlib.md5(method_name.encode()).digest()
    r = hash_bytes[0]
    g = hash_bytes[1]
    b = hash_bytes[2]

    # Ensure colors are bright enough to be readable
    r = max(r, 128)
    g = max(g, 128)
    b = max(b, 128)

    # 24-bit RGB color format: \033[38;2;R;G;Bm
    color = f'\033[38;2;{r};{g};{b}m'
    if bold:
        color = f'\033[1m{color}'  # Add bold

    reset = '\033[0m'
    return color, reset

def log_method_calls(cls):
    """Decorator that logs info when any method in the class is called"""

    original_init = cls.__init__

    @functools.wraps(original_init)
    def new_init(self, *args, **kwargs):
        self._call_depth = 0
        original_init(self, *args, **kwargs)
    cls.__init__ = new_init

    for attr_name in dir(cls):
        attr = getattr(cls, attr_name)
        if callable(attr) and not attr_name.startswith('_'):
            @functools.wraps(attr)
            def make_wrapper(method_name, original_method):
                def wrapper(self, *args, **kwargs):
                    args_str = ', '.join(str(arg) for arg in args)
                    kwargs_str = ', '.join(f'{k}={v}' for k, v in kwargs.items())
                    all_args = ', '.join(filter(None, [args_str, kwargs_str]))
                    indent = get_indent(self._call_depth)
                    color, reset = get_method_color(method_name, bold=True)
                    print(f"{indent}{color}{method_name}({all_args}){reset}")
                    self._call_depth += 1
                    try:
                        result = original_method(self, *args, **kwargs)
                    finally:
                        self._call_depth -= 1
                    return result
                return wrapper

            setattr(cls, attr_name, make_wrapper(attr_name, attr))
    return cls

@log_method_calls
class HipSeq6:
    piston_stack_depth = 4
    max_obs = 2
    _call_depth: int
    def __init__(self):
        self.moves: list[Move] = []
        self.stack_state = [False] * self.piston_stack_depth
        self.num_obs_out = 0

    def __iadd__(self, moves: list[Move] | Move):
        if isinstance(moves, Move):
            if hasattr(self, "_call_depth"):
                color, reset = get_method_color(moves.value)
                print(get_indent(self._call_depth), f"{color}{moves.value}{reset}")
            self.moves.append(moves)
        elif isinstance(moves, list):
            if hasattr(self, "_call_depth"):
                colored_moves = []
                for move in moves:
                    color, reset = get_method_color(move.value)
                    colored_moves.append(f"{color}{move.value}{reset}")
                print(get_indent(self._call_depth), *colored_moves)
            self.moves.extend(moves)
        return self

    def closing(self):
        self += [
            wait,
            *[ssto, b, worm]*4,
            a, ssto,
        ]
        self.more_pistons(0)
        self.extend(1)
        self += stop

    def storage_moves(self, *moves: Move):
        assert self.moves[-1] == b
        self.moves.pop()
        self.moves.extend(moves)

    def opening(self, tillRow: int):
        self += a
        self.retract(1)
        self += ssto

        self.full_row(2)
        self.storage_moves(a, b, ssto)

        for row in range(3, tillRow+1):
            self.full_row(row)
            self.storage_moves(a, ssto)

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
            case 0: self += d
            case 1: self += e
            case 2: self += [e, fold]
            case _:
                raise NotImplementedError

    def shift_pistons(self, layer: int):
        # layer: True -> False
        # layer-1: False -> True
        if not self.stack_state[layer]:
            raise ValueError(f"layer {layer} not out")
        self.stack_state[layer] = False

        if layer > 0:
            if self.stack_state[layer-1]:
                raise ValueError(f"layer {layer-1} is already out.")
            self.stack_state[layer-1] = True

        match layer:
            case 0:
                self += [d, c, c]
            case 1:
                self += [e, d]
            case 2:
                self += fold
            case _:
                raise NotImplementedError

    def more_obs(self):
        if self.num_obs_out >= self.max_obs:
            raise ValueError(f"More than {self.max_obs} observers.")
        self.num_obs_out += 1
        match self.num_obs_out:
            case 1:
                self += bobs
            case 2:
                self += [ bobs, bobs, ssto, bobs, bobs, a, bobs ]
            case _:
                raise NotImplementedError


    def less_obs(self):
        if self.num_obs_out <= 0:
            raise ValueError(f"Less than {self.max_obs} observers.")
        self.num_obs_out -= 1
        match self.num_obs_out:
            case 0 | 1:
                self += [bobs, ssto, ssto]
            case _:
                raise NotImplementedError

    def full_row(self, layer: int):
        """
        Does full row.
        _____B -> B_____
        """
        if layer == -2:
            return
        if layer >= 0:
            self.more_pistons(layer // 2)
        self.row_high(layer)

    def row_high(self, layer: int, pistons_very_high: bool = False):
        """
        Does row, but with layer of pistons already up.
            _P___B -> B_____
        """
        self.full_extend(layer, pistons_very_high)
        self.retract(layer)

    def full_extend(self, layer: int, pistons_very_high: bool = False):
        self.extend(layer, pistons_very_high)
        self.extra_pulses(layer, pistons_very_high)

    def extend(self, layer: int, pistons_high: bool = False):
        match layer:
            case -1: self += b
            case 0: self += a
            case 1:
                if not pistons_high:
                    self += b
                self += a
            case _ if layer >= 2:
                if not pistons_high:
                    self += b
                # todo: figure out alg for needs_parity
                self.more_obs()
                if layer >= 3:
                    self.more_pistons((layer-3)//2)
                self.extend(layer-3)
            case _:
                raise NotImplementedError

    def extra_pulses(self, layer: int, pistons_very_high: bool = False):
        match layer, pistons_very_high:
            case (-1, _) | (0, _) | (1, _): return
            case 2, _:
                self += b
            case 3, _:
                self += a
            case 4, _:
                self += [a, ssto, ssto]
            case 5, False:
                self += [b]*7
            case _, _:
                raise NotImplementedError

    def retract(self, layer: int):
        if layer <= -1:
            return
        if layer >= 3:
            self.retract(layer-3)
        if layer >= 2:
            self.less_obs()

        self.pull(layer - 2)
        if layer % 2 == 0:
            self.shift_pistons(layer // 2)
        self.row_high(layer - 1, True)

    def pull(self, layer: int):
        """
        Pulls pistons at row n-1 down.
        _____P -> ____P_
        """
        if layer == -2:
            return
        if layer == -1:
            self += b
            return

        self.more_pistons(layer // 2)
        self.full_extend(layer)

        # retract layer below (obs)
        self.retract(layer - 3)
        if layer >= 2:
            self.less_obs()

        # remove pistons
        self.full_row(layer-2)
        for layer in range(layer//2, -1, -1):
            self.shift_pistons(layer)


def write_file(file_path:str, moves: list[str]):
    with open(file_path, "w") as f:
        for move in moves:
            f.write(move+ "\n")
    return -1


# python -m gen.hip.hip6.py
if __name__ == "__main__":
    door = HipSeq6()
    door.closing()
    door.opening(5)
    write_file(os.path.join(getcwd(), "door_meta", "6x6hip", "sequence.txt"), [m.value for m in door.moves])
    # print(door.moves)
