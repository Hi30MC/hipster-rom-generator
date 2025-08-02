from dataclasses import dataclass

from pydantic import BaseModel, Field, TypeAdapter
from typing import Annotated, Literal


class CartRomParams(BaseModel):
    cart_pos: list[float] = [0.5, 0, 0.5]
    min_carts: int = 1


class Rom1(CartRomParams):
    rom_type: Literal["cart1"]
    add_stop_move: bool = True


class Rom27(CartRomParams):
    rom_type: Literal["cart27"]
    medium: Literal["shulker", "disc"]
    min_items_per_cart: int = 0
    cut_wait_moves: bool = False

    def min_items(self):
        return self.min_carts * self.min_items_per_cart


class Rom729(CartRomParams):
    rom_type: Literal["cart729"]
    min_shulkers_per_cart: int = 0
    min_discs_per_shulker: int = 0


RomParams = Rom1 | Rom27 | Rom729
RomParamsAnnotated = Annotated[RomParams, Field(discriminator="rom_type")]


def parse_params(contents: str) -> RomParams:
    """Parse the parameters from a string."""
    return TypeAdapter(RomParamsAnnotated).validate_json(contents)


def parse_encoding(contents: str) -> dict[str, int]:
    lines = [
        line.strip().split()
        for line in contents.split("\n")
        if len(line.split()) == 2 and line.split()[1] != ""
    ]

    return {name: int(ss) for ss, name in lines}


def parse_move_list(contents: str) -> list[str]:
    return [line.strip() for line in contents.split("\n") if line]


@dataclass(frozen=True)
class Sequence:
    ss_list: list[int]
    wait_move: int | None

    def with_min_items(self, min_length: int) -> list[int]:
        if len(self.ss_list) >= min_length:
            return self.ss_list
        if self.wait_move is None:
            raise ValueError(
                "Sequence is not long enough, and no wait move is defined."
            )
        return self.ss_list + [self.wait_move] * (min_length - len(self.ss_list))

    @classmethod
    def decode(cls, moves: list[str], key: dict[str, int]) -> "Sequence":
        ss_list = [key[move] for move in moves]
        wait_move = key.get("wait")
        return Sequence(ss_list, wait_move)


def parse_sequence(encoding_file: str, sequence_file: str) -> Sequence:
    encoding = parse_encoding(encoding_file)
    moves = parse_move_list(sequence_file)
    return Sequence.decode(moves, encoding)
