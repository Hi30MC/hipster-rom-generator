from enum import Enum
from doors.hip.basic_hip import BasicHip


class Move(Enum):
    STOP = "stop"
    WAIT = "wait"
    A = "a"
    B = "b"
    C = "c"
    D = "d"
    E = "e"
    STO = "sto"
    BOBS = "bobs"
    WORM = "worm"
    FOLD1 = "fold1"
    FOLD2 = "fold2"


stop = Move.STOP
wait = Move.WAIT
a = Move.A
b = Move.B
c = Move.C
d = Move.D
e = Move.E
sto = Move.STO
bobs = Move.BOBS
worm = Move.WORM
fold1 = Move.FOLD1
fold2 = Move.FOLD2


class HipSeq8(BasicHip[Move]):
    piston_stack_depth = 5
    max_obs = 3

    def the_whole_shebang(self):
        self += wait
        self.closing()
        self += stop
        self.opening()

    def closing(self):
        self += [sto, worm, e, e, d, d, c, c, b] * 2
        self += [sto, worm, worm, d, d, c, c, b]
        self += [sto, worm, d, d, c, c, b]
        self += [sto, worm, b, sto, b, a, sto]
        self.more_pistons(0)
        self.extend(1)

    def storage_moves(self, *moves: Move):
        assert self.moves[-1] == b
        self.moves.pop()
        self.moves.extend(moves)

    def opening(self):
        self += a
        self.retract(1)
        self += sto

        self.full_row(2)
        self.storage_moves(a, b, sto)

        for row in range(3, 7 + 1):
            self.full_row(row)
            self.storage_moves(a, sto)
        self.full_row(8)

        last_6 = self.moves[-6:]
        assert last_6 == [a, b, a, c, b, b]
        self.moves[-6:] = [a, b, c, b]

    def more_pistons(self, layer: int):
        if any(self.stack_state[:layer]):
            raise ValueError(f"not all layers below {layer} are False.")
        if self.stack_state[layer]:
            raise ValueError(f"layer {layer} is already True.")

        self.stack_state[layer] = True

        double_folded = self.stack_state[4]

        match layer, double_folded:
            case 0, _:
                self += c
            case 1, _:
                self += d
            case 2, False:
                self += e
            case 3, False:
                self += [e, fold1]

            case 2, True:
                self += [d, fold2]
            case 3, True:
                self += e
            case 4, _:
                self += [e, fold1]
            case _:
                raise NotImplementedError

    def shift_pistons(self, layer: int):
        if not self.stack_state[layer]:
            raise ValueError(f"layer {layer} not out")
        self.stack_state[layer] = False

        if layer > 0:
            if self.stack_state[layer - 1]:
                raise ValueError(f"layer {layer - 1} is already out.")
            self.stack_state[layer - 1] = True

        double_folded = self.stack_state[4]

        match layer, double_folded:
            case 0, _:
                self += [c, b]
            case 1, _:
                self += [d, c]
            case 2, False:
                self += [e, d]
            case 3, False:
                self += fold1

            case 2, True:
                self += fold2
            case 3, True:
                self += [e, d]
            case 4, _:
                pass
            case _:
                raise NotImplementedError

    def more_obs(self, needs_parity=False):
        if self.num_obs_out >= self.max_obs:
            raise ValueError(f"More than {self.max_obs} observers.")
        self.num_obs_out += 1
        match self.num_obs_out, needs_parity:
            case 1, _:
                self += [bobs, bobs]
            case 2, True:
                self += [bobs, sto, bobs, bobs, a, bobs]
            case 2, False:
                self += [bobs, a, bobs]
            case 3, _:
                self += sto
            case _:
                raise NotImplementedError

    def less_obs(self):
        if self.num_obs_out <= 0:
            raise ValueError(f"Less than {self.max_obs} observers.")
        self.num_obs_out -= 1
        match self.num_obs_out:
            case 0 | 1:
                self += [sto, sto]
            case 2:
                self += [b, sto]
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
        self._dedent().row_high(layer)

    def row_high(self, layer: int, pistons_high: bool = False):
        """
        Does row, but with layer of pistons already up.
            _P___B -> B_____
        """
        self.full_extend(layer, pistons_high)
        self._dedent().retract(layer)

    def full_extend(self, layer: int, pistons_high: bool = False):
        self.extend(layer, pistons_high, needs_parity=True)
        self.extra_pulses(layer, pistons_high)

    def extend(
        self, layer: int, pistons_high: bool = False, needs_parity: bool = False
    ):
        match layer:
            case -1:
                self += b
            case 0:
                self += a
            case 1:
                if not pistons_high:
                    self += b
                self += a
            case _ if layer >= 2:
                if not pistons_high:
                    self += b
                # todo: figure out alg for needs_parity
                self.more_obs(needs_parity)
                if layer >= 3:
                    self.more_pistons((layer - 3) // 2)
                self.extend(layer - 3, needs_parity=needs_parity)
            case _:
                raise NotImplementedError

    def extra_pulses(self, layer: int, pistons_high: bool = False):
        match layer, pistons_high:
            case (-1, _) | (0, _) | (1, _):
                return
            case 2, _:
                self += b
            case 3, _:
                self += a
            case 4, _:
                self += a
                if self.num_obs_out == 0:
                    self += [sto, sto]
            case 5, False:
                self += [b] * 5
            case 5, True:
                self += [b] * 3
            case 6, False:
                self += [a] * 7
            case 6, True:
                self += [a] * 3
            case 7, False:
                self += [a] * 7
            case 7, True:
                self += [a] * 3
            case 8, False:
                self += [a] * 8
            case _, _:
                raise NotImplementedError

    def retract(self, layer: int):
        if layer <= -1:
            return
        if layer >= 3:
            self.retract(layer - 3)
        if layer >= 2:
            self.less_obs()

        self.pull(layer - 2)
        if layer % 2 == 0:
            self.shift_pistons(layer // 2)
        self._dedent().row_high(layer - 1, True)

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
        self.full_row(layer - 2)
        for layer in range(layer // 2, -1, -1):
            self.shift_pistons(layer)


if __name__ == "__main__":
    door = HipSeq8()
    door.the_whole_shebang()
    door._write_sequence("door_meta/8x8hip/sequence.txt")
    door._write_log("door_meta/8x8hip/log.txt")
