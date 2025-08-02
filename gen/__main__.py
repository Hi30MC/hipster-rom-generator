import click
from pathlib import Path

from gen.rom_gen import gen_rom
from gen.params import parse_params, parse_sequence


@click.command()
@click.argument("info_dir")
@click.argument("out_path", required=False)
def main(info_dir: str, out_path: str | None):
    """
    Generate ROM from door information.

    \b
    INFO_DIR: Directory containing door information files
    OUT_PATH: Path to output file. Default: output_schematics/{dir_name}/{dir_name}.schem

    """
    if out_path is None:
        dir_name = Path(info_dir).name
        out_path = f"output_schematics/{dir_name}/{dir_name}.schem"

    sequence = parse_sequence(
        encoding_file=Path(info_dir, "key.txt").read_text(),
        sequence_file=Path(info_dir, "sequence.txt").read_text(),
    )
    params = parse_params(Path(info_dir, "params.json").read_text())

    schem = gen_rom(sequence, params)

    if not out_path.endswith(".schem"):
        out_path += ".schem"
    import os
    print(os.path.abspath(out_path))
    schem.save(out_path)


if __name__ == "__main__":
    main()
