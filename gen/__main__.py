import click
from os import path

from gen.rom_gen import gen_rom
from gen.params import parse_params, parse_sequence


def read_file(path: str) -> str:
    with open(path, "r") as f:
        return f.read()


@click.command()
@click.argument("info_dir")
@click.argument("out_path", required=False)
def main(info_dir: str, out_path: str | None):
    """
    Generate ROM from door information.

    \b
    INFO_DIR: Directory containing door information files
    OUT_PATH: Path to output file. Default: output_schematics/{door_name}/{door_name}.schem
    If OUT_PATH does not contain a file separator, the folder will be output_schematics/{door_name}.
    """

    if path.pathsep in info_dir:
        resolved_info_dir = info_dir
    else:
        resolved_info_dir = f"door_meta/{info_dir}"

    door_name = path.basename(resolved_info_dir)

    if out_path is None:
        out_path = door_name

    if path.pathsep not in out_path:
        out_path = f"output_schematics/{door_name}/{out_path}"

    sequence = parse_sequence(
        encoding_file=read_file(path.join(resolved_info_dir, "key.txt")),
        sequence_file=read_file(path.join(resolved_info_dir, "sequence.txt")),
    )
    params = parse_params(read_file(path.join(resolved_info_dir, "params.json")))
    schem = gen_rom(sequence, params)

    if not out_path.endswith(".schem"):
        out_path += ".schem"
    import os

    os.makedirs(path.dirname(out_path), exist_ok=True)
    schem.save(out_path)
    print("Wrote file to", os.path.abspath(out_path))


if __name__ == "__main__":
    main()
