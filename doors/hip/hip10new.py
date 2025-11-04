from doors.hip.basic_hip import BasicHip
from typing import NewType

from doors.hip.hip789 import worm

Move = NewType("Move", str)

wait = Move("wait")
a = Move("a")
b = Move("b")
c = Move("c")
d = Move("d")
e = Move("e")
f = Move("f")
bsto = Move("bsto")
obs = Move("obs")
TS = Move("TS")
fold = Move("fold")


class HipSeq10(BasicHip[Move]):
    piston_stack_depth = 6
    max_obs = 3

    fold_toggle = False
    fpull_primed = False

    def the_whole_shebang(self):
        self.closing()
        self.stop()
        self.opening()

    def closing(self):
        # fmt: off
        self += [bsto, b, a,
            b, bsto,
            worm, worm,
            bsto, a,
            bsto,
            fold, f, worm, worm,
            e, d, fold, worm, worm,
            fold, fold, d, c, c,
            bsto, a,
            bsto,
            f, fold, worm, worm,
            a, bsto,
            b, TS, a, bsto,
            worm, worm,
            b, d, fold, f, b, a, fold, fold, d, c]
        # fmt: on
        self.stack_state[0] = True

    def stop(self):
        self += [wait] * ((26 - len(self.moves) % 26) % 26)
        self += [wait] * 26

    def storage_moves(self, *moves: Move):
        assert self.moves[-1] == b
        self.moves.pop()
        self += list(moves)

    def only_sto(self):
        if self.moves[-1] == b:
            self.moves.pop()
            self += bsto
        else:
            self += [b, bsto]

    def opening(self):
        self += a
        self.retract(1)
        self.only_sto()

        self.full_row(2)
        self.storage_moves(a, bsto)

        for row in [3, 4]:
            self.full_row(row)
            self.storage_moves(a, b, bsto)

        self.full_row(5)
        self += [a, b, bsto]
        self += [d, fold, fold, fold]
        self += [worm, worm]
        self += fold
        self += [f, d, c, c, b]

        # self.full_row(6)
        # self += [a, b, bsto]
        # self += [d, fold, fold, fold]
        # self += [worm, worm]
        # self += fold
        # self += [d, c, c, b]

        # for row in [7, 8, 9]:
        #     self.full_row(row)
        #     self.storage_moves(a, b, bsto)

        # self.full_row(10)
        # last_6 = self.moves[-6:]
        # assert last_6 == [a, b, a, c, b, b]
        # self.moves[-6:] = [a, b, c, b]

    def more_pistons(self, layer: int):
        if any(self.stack_state[:layer]):
            raise ValueError(f"not all layers below {layer} are False.")
        if self.stack_state[layer]:
            raise ValueError(f"layer {layer} is already True.")

        self.stack_state[layer] = True

        match layer:
            case 0:
                self += c
            case 1:
                self += d
            case 2:
                self += [d, fold, fold]
            case 3:
                self += e
            case 4:
                assert not self.fpull_primed
                self += f
            case 5:
                self.fpull_primed = True
                self += f
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

        match layer:
            case 0:
                self += [c, b]
            case 1:
                self += [d, c]
            case 2:
                self += [d, c, c, b, b, fold, fold]
            case 3:
                self += [e, d]
            case 4:
                self += [f, e]
            case 5:
                self += [d, fold, d, c, c, b, b]
            case _:
                raise NotImplementedError

    def more_obs(self, needs_parity=False):
        if self.num_obs_out >= self.max_obs:
            raise ValueError("Not enough observers.")
        self.num_obs_out += 1
        match self.num_obs_out:
            case 1:
                self += [obs, obs]
            case 2:
                self += [obs, a, obs]
            case 3:
                self.only_sto()
            case _:
                raise NotImplementedError

    def less_obs(self):
        if self.num_obs_out <= 0:
            raise ValueError("Retracting more observers than there are.")
        self.num_obs_out -= 1
        match self.num_obs_out:
            case 0 | 1:
                self.only_sto()
                self.only_sto()
            case 2:
                self += bsto
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

    def row_high(self, layer: int, pistons_high: bool = False):
        """
        Does row, but with layer of pistons already up.
            _P___B -> B_____
        """
        self.full_extend(layer, pistons_high)
        self.retract(layer)

    def full_extend(self, layer: int, pistons_high: bool = False):
        self.extend(layer, pistons_high)
        self.extra_pulses(layer, pistons_high)

    def extend(self, layer: int, pistons_high: bool = False):
        match layer:
            case -1:
                self += b
            case 0:
                self += a
            case 1:
                if not pistons_high:
                    self += b
                self += a
            case _ if 2 <= layer < 9:
                if not pistons_high:
                    self += b
                self.more_obs(needs_parity=not pistons_high)
                if layer >= 3:
                    self.more_pistons((layer - 3) // 2)
                self.extend(layer - 3)
            case 9:
                if not pistons_high:
                    self += b
                self.more_obs()  # deploy sandwich
                self.more_pistons((layer - 3) // 2)
                self += [bsto, b]  # block
                self.more_obs(True)
                self.more_pistons(2 // 2)
                self += b
                self.more_obs()
                self += b
            case 10:
                assert not pistons_high
                self += [bsto, b]  # block
                self.more_obs()
                self.more_pistons((layer - 3) // 2)
                self += [bsto, b]  # block
                assert self.fpull_primed
                self.fpull_primed = False
                self += worm
                self.more_obs()
                self += fold
                self.more_pistons(2 // 2)
                self += b
                self.more_obs()  # actually a block
                self += b
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
            case 5, False:
                self += [b] * 5
            case 5, True:
                if self.num_obs_out == 3:
                    self += [a] * 2
                else:
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
            case 8, True:
                self += [a] * 4
            case (9, False) | (10, False):
                self += [a] * 8
            case 9, True:
                self += [a] * 4
            case _, _:
                raise NotImplementedError

    def retract(self, layer: int, no_recurse_first=False):
        if layer <= -1:
            return

        if layer == 9:
            # special retraction
            assert self.num_obs_out == 3
            self.retract(2)  # piston-obs
            self.less_obs()  # first obs
            self.full_row(3)  # remove the sandwich
            self.storage_moves(a, bsto)  # and eat it
        elif layer == 10:
            assert self.num_obs_out == 3
            self.retract(2)  # piston-obs
            self.less_obs()  # first obs
            self.full_row(3)  # remove the sandwich
            self.storage_moves(a, bsto)  # and eat it
            self.retract(layer - 4, no_recurse_first=layer >= 9)
            self.less_obs()  # first obs
            self.full_row(7)
            self.storage_moves(a, bsto)  # and eat it
            self.pull(layer - 2)
            if layer % 2 == 0:
                self.shift_pistons(layer // 2)
            self.row_high(layer - 1, True)
            return

        if layer >= 3 and not no_recurse_first:
            self.retract(layer - 3, no_recurse_first=layer >= 9)

        if layer >= 2 and not no_recurse_first:
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
        self.full_row(layer - 2)
        for layer in range(layer // 2, -1, -1):
            self.shift_pistons(layer)

    def _add(self, *moves: Move):
        self.call_tree.add_message(" ".join(map(str, moves)))
        for move in moves:
            last_move = self.moves[-1] if self.moves else None
            if move in (fold, obs) and last_move != wait:
                self.moves.append(wait)
            if move == bsto and last_move == a:
                self.moves.append(wait)
            self.moves.append(move)
            if move in (bsto, TS, obs):
                self.moves.append(wait)


def main():
    door = HipSeq10()
    door.stack_state[0] = True
    door.opening()
    print(len(door.moves))
    door._write_sequence("door_meta/10x10hipnew/sequence.txt")
    door._write_call_tree("door_meta/10x10hipnew/call_tree.yaml")


if __name__ == "__main__":
    main()
