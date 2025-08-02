import click
from os import path

from gen.rom_gen import gen_rom
from gen.params import parse_params, parse_sequence


def read_file(path: str) -> str:
    with open(path, "r") as f:
        return f.read()


@click.command()
@click.argument("door_name")
@click.argument("schem_file_name", required=False)
def main(door_name: str, schem_file_name: str | None):
    """
    Generate ROM from door information.

    \b
    INFO_DIR: Directory containing door information files
    OUT_PATH: Path to output file. Default: output_schematics/{door_name}/{door_name}.schem
    If OUT_PATH does not contain a file separator, the folder will be output_schematics/{door_name}.
    """

    if path.pathsep in door_name:
        info_dir = door_name
    else:
        info_dir = f"door_meta/{door_name}"

    if schem_file_name is None:
        schem_file_name = f"output_schematics/{door_name}/{door_name}.schem"
    else:
        if path.pathsep not in schem_file_name:
            schem_file_name = f"output_schematics/{door_name}/{schem_file_name}"

    sequence = parse_sequence(
        encoding_file=read_file(path.join(info_dir, "key.txt")),
        sequence_file=read_file(path.join(info_dir, "sequence.txt")),
    )
    params = parse_params(read_file(path.join(info_dir, "params.json")))
    print(params)

    schem = gen_rom(sequence, params)

    if not schem_file_name.endswith(".schem"):
        schem_file_name += ".schem"
    import os

    os.makedirs(path.dirname(schem_file_name), exist_ok=True)
    schem.save(schem_file_name)
    print("Wrote file to", os.path.abspath(schem_file_name))


if __name__ == "__main__":
    main()
