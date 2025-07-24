from os import path, getcwd
from gen.out import encoding

def gen(door_name: str) -> list[int]:
    # open sequence file
    door_meta_path = path.join(getcwd(), "door_meta", door_name)

    with open(path.join(door_meta_path,"sequence.txt"), "r") as f:
        sequence_raw = f.read()

    # generate sequence based on encoding and text file
    ss_encode = encoding.get(door_name)
    ss_sequence = [int(ss_encode[x]) for x in sequence_raw.split("\n") if x != ""]

    return ss_sequence
