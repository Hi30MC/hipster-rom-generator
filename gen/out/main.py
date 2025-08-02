import sys
from os import path

from nbtlib import File
from gen.out import rom
from gen.out.gen_params import GenParams
from gen.util.types import Schematic

"""
General logic flow of the file:
- Generate sequence:
    - Generate full sequence as a list of strings of move names
    - Convert list of move names to a list of numerical signal strengths using the key
- Generate ROM as a list of carts
    - Determine structure of items based on door's meta
    - Optimize item placement based on door's meta
- Generate base file structure with gen_base()
- Add list of carts to base file and export
"""


def read_encoding(info_dir: str) -> dict[str, int]:
    key_path = path.join(info_dir, "key.txt")
    with open(key_path, "r") as f:
        contents = f.read()

    lines = [
        line.strip()
        for line in contents.split("\n")
        if len(line.split()) == 2 and line.split()[1] != ""
    ]

    return {name: int(ss) for name, ss in (line.split() for line in lines)}


def read_sequence(info_dir: str) -> list[str]:
    sequence_path = path.join(info_dir, "sequence.txt")
    with open(sequence_path, "r") as f:
        sequence = f.read()

    return [line for line in sequence.split("\n") if line != ""]


def read_params(info_dir: str) -> GenParams:
    params_path = path.join(info_dir, "params.txt")
    with open(params_path, "r") as f:
        contents = f.read()

    return GenParams.parse(contents)


def gen_carts(info_dir: str, out_file_name: str):

    encoding = read_encoding(out_file_name)
    sequence = read_sequence(info_dir)
    params = read_params(info_dir)

    ss_sequence = [encoding[move] for move in sequence]
    carts = rom.gen_ROM(ss_sequence, params)

    out = File(Schematic.empty(), gzipped=True)

    # add entity list to file
    out.update({"Entities": List(cart_list)})

    # save file
    out.save(path.join("output_schematics", info_dir, f"{out_file_name}.schem"))

    return out


if __name__ == "__main__":
    args = sys.argv[1:]
    if len(args) == 0:
        print(
            "Pass in door name, and file name as three separate parameters. \nLeave off file name to simply use door name."
        )
    elif len(args) == 1:
        gen_carts(*[args[0]] * 2)
    elif len(args) == 2:
        gen_carts(*args)
    else:
        print("Too many arguments.")
