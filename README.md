# hipster-rom-generator

World Edit schematic generator for various types of cart-based ROMs.

Example file directory for a given door:

```
./
├── door_meta
│   └── door_1
│       ├── key.txt
│       ├── params.json
│       └── sequence.txt
├── gen
│   └── door_1
│       ├── __init__.py
│       ├── gen_seq.py
│       ├── part_1.txt
│       └── part_2.txt
└── output_schematics
    └── door_1
        └── door_1.schem
```

## Setup
Setup venv with:
`./venv_primer.sh`

`source .venv/bin/activate`

## Generation

To generate a given door's sequence, run that door's sequence file with:

`python3 -m doors.<path to file name> <params, if specified in file>`

Then run the main `gen.py` with:

`python3 -m gen.out.main <door name> <opt: schem_name>`

This will generate the finalized schematic in `output_schematics/<door_name>/<schem name>.schem`, which defaults to
`<door_name>.schem`.

Do note that this codebase was coded on a Linux file system, and has not been tested on either Windows or macOS. Feel
free to report any issues.
