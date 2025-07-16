from os import path, getcwd
from gen.out import ss_encode as enc

def gen_ss_sequence(door_name: str) -> list[int]:
    # open sequence file
    door_meta_path = path.join(getcwd(), "door_meta", door_name) 
    
    with open(path.join(door_meta_path,"sequence.txt"), "r") as f:
        sequence_raw = f.read()
            
    # generate sequence based on encoding and text file
    ss_encode = enc.get_encode(door_name)
    ss_sequence = [int(ss_encode[x]) for x in sequence_raw.split("\n")]
    
    return ss_sequence
