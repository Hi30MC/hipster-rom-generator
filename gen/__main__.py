import click
from pathlib import Path

from gen.rom_gen import gen_rom
from .params import parse_params, parse_sequence


@click.command()
@click.argument("info_dir")
@click.argument("out_path", required=False)
def main(info_dir: str, out_path: str | None):
    """
    Generate ROM from door information.

    \b
    INFO_DIR: Directory containing door information files
    OUT_PATH: Path to output file

    """
    if out_path is None:
        out_path = info_dir

    sequence = parse_sequence(
        encoding_file=Path(info_dir, "key.txt").read_text(),
        sequence_file=Path(info_dir, "sequence.txt").read_text(),
    )
    params = parse_params(Path(info_dir, "params.txt").read_text())

    schem = gen_rom(sequence, params)

    if not out_path.endswith(".schem"):
        out_path += ".schem"
    with open(out_path, "wb") as file:
        schem.write(file)


if __name__ == "__main__":
    main()
